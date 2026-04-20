"""
Link Map Router — endpoints for scanning and retrieving link maps.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from bson import ObjectId
from app.database import projects_col
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/projects", tags=["Link Map"])


@router.post("/{project_id}/link-map/refresh")
async def refresh_link_map(
    project_id: str, current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """Trigger a fresh scan of all published posts to build the link map."""
    from app.services.link_map_service import scan_and_build_link_map

    # Verify project exists
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = await scan_and_build_link_map(project_id)
        return result
    except Exception as e:
        print(f"[LINK_MAP_ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to scan links: {str(e)}")


@router.get("/{project_id}/link-map")
async def get_link_map(
    project_id: str, current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """Get the latest link map for a project."""
    from app.services.link_map_service import get_link_map as get_map

    # Verify project exists
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await get_map(project_id)
    if not result:
        return {
            "project_id": project_id,
            "scanned_at": None,
            "nodes": [],
            "edges": [],
            "stats": {
                "total_posts_scanned": 0,
                "total_internal_links": 0,
                "total_external_links": 0,
                "total_unique_external_domains": 0,
            },
        }
    return result
