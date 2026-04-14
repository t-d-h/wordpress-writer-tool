"""
Post Sync Service — sync WordPress posts to local database.
"""

from datetime import datetime
from bson import ObjectId
from app.database import posts_col
from app.services.wp_service import get_wp_posts


async def create_or_update_post(
    project_id: str, wp_post: dict, origin: str = "wordpress"
) -> dict:
    """Create or update a post record from WordPress data.

    Args:
        project_id: Project ID
        wp_post: WordPress post object from REST API
        origin: Post origin ("tool" or "wordpress")

    Returns:
        Created or updated post document
    """
    # Check if post already exists by wp_post_id
    existing = await posts_col.find_one(
        {"wp_post_id": wp_post["id"], "project_id": ObjectId(project_id)}
    )

    post_data = {
        "project_id": ObjectId(project_id),
        "wp_post_id": wp_post["id"],
        "wp_post_url": wp_post["link"],
        "title": wp_post["title"]["rendered"],
        "origin": origin,
        "status": wp_post["status"],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    if existing:
        # Update existing record
        await posts_col.update_one({"_id": existing["_id"]}, {"$set": post_data})
        post_data["_id"] = existing["_id"]
    else:
        # Create new record
        result = await posts_col.insert_one(post_data)
        post_data["_id"] = result.inserted_id

    return post_data


async def sync_wordpress_posts(
    project_id: str, status: str = "any", per_page: int = 100
) -> dict:
    """Sync all posts from WordPress to local database.

    Args:
        project_id: Project ID
        status: Filter by post status (default: "any")
        per_page: Posts per page (default: 100)

    Returns:
        dict with 'created', 'updated', 'total' counts
    """
    created_count = 0
    updated_count = 0
    page = 1

    while True:
        # Fetch posts from WordPress
        result = await get_wp_posts(
            project_id=project_id, per_page=per_page, page=page, status=status
        )

        wp_posts = result["posts"]
        total = result["total"]

        if not wp_posts:
            break

        # Sync each post
        for wp_post in wp_posts:
            existing = await posts_col.find_one(
                {"wp_post_id": wp_post["id"], "project_id": ObjectId(project_id)}
            )

            if existing:
                await create_or_update_post(project_id, wp_post, "wordpress")
                updated_count += 1
            else:
                await create_or_update_post(project_id, wp_post, "wordpress")
                created_count += 1

        # Check if we've fetched all posts
        if len(wp_posts) < per_page:
            break

        page += 1

    return {
        "created": created_count,
        "updated": updated_count,
        "total": created_count + updated_count,
    }
