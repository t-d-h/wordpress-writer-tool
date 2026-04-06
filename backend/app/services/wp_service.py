"""
WordPress Service — publish/update posts via the WordPress REST API.
"""
import base64
import httpx
import os
from app.database import wp_sites_col, projects_col
from bson import ObjectId


async def _get_wp_site(project_id: str) -> dict:
    """Get the WordPress site configuration for a project."""
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise Exception(f"Project {project_id} not found")
    wp_site = await wp_sites_col.find_one({"_id": ObjectId(project["wp_site_id"])})
    if not wp_site:
        raise Exception(f"WordPress site not found for project {project_id}")
    return wp_site


def _get_auth_header(username: str, api_key: str) -> dict:
    """Create Basic Auth header for WordPress REST API."""
    credentials = base64.b64encode(f"{username}:{api_key}".encode()).decode()
    return {"Authorization": f"Basic {credentials}"}


async def upload_media(project_id: str, file_path: str, filename: str = None) -> dict:
    """Upload an image to WordPress media library. Returns media object."""
    wp_site = await _get_wp_site(project_id)
    headers = _get_auth_header(wp_site["username"], wp_site["api_key"])

    if not filename:
        filename = os.path.basename(file_path)

    # Determine content type
    ext = filename.rsplit(".", 1)[-1].lower()
    content_type_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    content_type = content_type_map.get(ext, "image/png")

    headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    headers["Content-Type"] = content_type

    with open(file_path, "rb") as f:
        file_data = f.read()

    url = f"{wp_site['url'].rstrip('/')}/wp-json/wp/v2/media"

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, content=file_data)
        response.raise_for_status()
        return response.json()


async def create_wp_post(
    project_id: str,
    title: str,
    content: str,
    meta_description: str = "",
    thumbnail_media_id: int = None,
    status: str = "draft",
) -> dict:
    """Create a post on WordPress. Returns the WP post object."""
    wp_site = await _get_wp_site(project_id)
    headers = _get_auth_header(wp_site["username"], wp_site["api_key"])
    headers["Content-Type"] = "application/json"

    url = f"{wp_site['url'].rstrip('/')}/wp-json/wp/v2/posts"

    post_data = {
        "title": title,
        "content": content,
        "status": status,
        "excerpt": meta_description,
    }
    if thumbnail_media_id:
        post_data["featured_media"] = thumbnail_media_id

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, json=post_data)
        response.raise_for_status()
        return response.json()


async def update_wp_post(
    project_id: str,
    wp_post_id: int,
    title: str = None,
    content: str = None,
    status: str = None,
    thumbnail_media_id: int = None,
) -> dict:
    """Update an existing WordPress post."""
    wp_site = await _get_wp_site(project_id)
    headers = _get_auth_header(wp_site["username"], wp_site["api_key"])
    headers["Content-Type"] = "application/json"

    url = f"{wp_site['url'].rstrip('/')}/wp-json/wp/v2/posts/{wp_post_id}"

    post_data = {}
    if title:
        post_data["title"] = title
    if content:
        post_data["content"] = content
    if status:
        post_data["status"] = status
    if thumbnail_media_id:
        post_data["featured_media"] = thumbnail_media_id

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, json=post_data)
        response.raise_for_status()
        return response.json()
