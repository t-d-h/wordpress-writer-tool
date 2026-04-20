"""
WordPress Router — API endpoints for WordPress sync operations.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from bson import ObjectId
from app.services.post_sync_service import sync_wordpress_posts, detect_orphaned_posts
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/projects/{project_id}/wordpress", tags=["wordpress"])


@router.post("/sync")
async def sync_posts(
    project_id: str,
    status: str = "any",
    per_page: int = 100,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Sync posts from WordPress to local database.

    Args:
        project_id: Project ID
        status: Filter by post status (default: "any")
        per_page: Posts per page (default: 100)

    Returns:
        dict with 'created', 'updated', 'total' counts
    """
    try:
        result = await sync_wordpress_posts(
            project_id=project_id, status=status, per_page=per_page
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orphans")
async def get_orphaned_posts(
    project_id: str, current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """Get posts that exist locally but not in WordPress.

    Args:
        project_id: Project ID

    Returns:
        List of orphaned post documents
    """
    try:
        orphans = await detect_orphaned_posts(project_id=project_id)
        return {"orphans": orphans, "count": len(orphans)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts")
async def get_wordpress_posts(
    project_id: str,
    per_page: int = 100,
    page: int = 1,
    status: str = None,
    search: str = None,
    orderby: str = "date",
    order: str = "desc",
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Fetch posts from WordPress REST API.

    Args:
        project_id: Project ID
        per_page: Posts per page (default: 100)
        page: Page number (default: 1)
        status: Filter by post status
        search: Search by title
        orderby: Order by field
        order: ASC or DESC

    Returns:
        dict with 'posts' list and 'total' count
    """
    try:
        from app.services.wp_service import get_wp_posts

        result = await get_wp_posts(
            project_id=project_id,
            per_page=per_page,
            page=page,
            status=status,
            search=search,
            orderby=orderby,
            order=order,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
