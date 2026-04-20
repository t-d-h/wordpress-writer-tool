from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Annotated, Optional
from bson import ObjectId
from app.utils.time_utils import get_now
from app.database import projects_col, wp_sites_col, posts_col
from app.models.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    TokenUsageResponse,
)
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/projects", tags=["Projects"])


def format_project(
    doc: dict, wp_site_name: Optional[str] = None, wp_site_url: Optional[str] = None
) -> dict:
    return ProjectResponse(
        id=str(doc["_id"]),
        title=doc["title"],
        description=doc.get("description", ""),
        wp_site_id=doc["wp_site_id"],
        wp_site_name=wp_site_name,
        wp_site_url=wp_site_url,
        created_at=doc["created_at"],
        language=doc.get("language", "en"),
    ).model_dump()


@router.get("")
async def list_projects(current_user: Annotated[dict, Depends(get_current_user)]):
    projects = []
    async for doc in projects_col.find().sort("created_at", -1):
        wp_site = await wp_sites_col.find_one({"_id": ObjectId(doc["wp_site_id"])})
        wp_name = wp_site["name"] if wp_site else "Unknown"
        wp_url = wp_site["url"] if wp_site else None
        projects.append(format_project(doc, wp_name, wp_url))
    return projects


@router.get("/{project_id}")
async def get_project(
    project_id: str, current_user: Annotated[dict, Depends(get_current_user)]
):
    doc = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
    wp_site = await wp_sites_col.find_one({"_id": ObjectId(doc["wp_site_id"])})
    wp_name = wp_site["name"] if wp_site else "Unknown"
    wp_url = wp_site["url"] if wp_site else None
    return format_project(doc, wp_name, wp_url)


@router.get("/{project_id}/stats")
async def get_project_stats(
    project_id: str, current_user: Annotated[dict, Depends(get_current_user)]
):
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Aggregate post status counts
    pipeline = [
        {"$match": {"project_id": project_id}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]
    stats = {"draft": 0, "waiting_approve": 0, "published": 0, "failed": 0, "total": 0}
    async for doc in posts_col.aggregate(pipeline):
        stats[doc["_id"]] = doc["count"]
        stats["total"] += doc["count"]

    # Aggregate token usage (includes all posts, no status filter)
    token_pipeline = [
        {"$match": {"project_id": project_id}},
        {
            "$group": {
                "_id": "$project_id",
                "research": {"$sum": "$token_usage.research"},
                "outline": {"$sum": "$token_usage.outline"},
                "content": {"$sum": "$token_usage.content"},
                "thumbnail": {"$sum": "$token_usage.thumbnail"},
                "total": {"$sum": "$token_usage.total"},
                "input_tokens": {"$sum": "$token_usage.input_tokens"},
                "output_tokens": {"$sum": "$token_usage.output_tokens"},
            }
        },
    ]
    token_result = await posts_col.aggregate(token_pipeline).to_list(length=1)
    token_usage = TokenUsageResponse(
        research=0,
        outline=0,
        content=0,
        thumbnail=0,
        total=0,
        input_tokens=0,
        output_tokens=0,
    )
    if token_result:
        token_usage = TokenUsageResponse(
            research=token_result[0].get("research", 0),
            outline=token_result[0].get("outline", 0),
            content=token_result[0].get("content", 0),
            thumbnail=token_result[0].get("thumbnail", 0),
            total=token_result[0].get("total", 0),
            input_tokens=token_result[0].get("input_tokens", 0),
            output_tokens=token_result[0].get("output_tokens", 0),
        )

    # Add token usage to stats response
    stats["token_usage"] = token_usage.model_dump()
    return stats


@router.post("", status_code=201)
async def create_project(
    data: ProjectCreate, current_user: Annotated[dict, Depends(get_current_user)]
):
    # Validate wp_site exists
    wp_site = await wp_sites_col.find_one({"_id": ObjectId(data.wp_site_id)})
    if not wp_site:
        raise HTTPException(status_code=400, detail="WordPress site not found")

    # Check if user has permission to access this site
    if current_user["role"] not in ["admin", "editor"]:
        raise HTTPException(
            status_code=403, detail="Only admin and editor roles can create projects"
        )

    # Add token usage to stats response
    stats = {
        "draft": 0,
        "waiting_approve": 0,
        "published": 0,
        "failed": 0,
        "total": 0,
        "input_tokens": 0,
        "output_tokens": 0,
    }

    # Create project
    project_data = data.model_dump()
    project_data["created_at"] = get_now()
    project_data["created_by"] = current_user["username"]

    result = await projects_col.insert_one(project_data)
    return {
        "id": str(result.inserted_id),
        "title": project_data["title"],
        "description": project_data.get("description", ""),
        "wp_site_id": project_data["wp_site_id"],
        "language": project_data.get("language", "en"),
        "created_at": project_data["created_at"],
        "created_by": project_data["created_by"],
    }


@router.put("/{project_id}")
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Check if user has permission to access this project
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if (
        current_user["id"] != project["created_by"]
        and current_user.get("role") != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the user who created the project can update it",
        )

    if "wp_site_id" in update_data:
        wp_site = await wp_sites_col.find_one(
            {"_id": ObjectId(update_data["wp_site_id"])}
        )
        if not wp_site:
            raise HTTPException(status_code=404, detail="WordPress site not found")

        # Check if user has permission to access this site
        if current_user["id"] != wp_site["created_by"]:
            raise HTTPException(
                status_code=403,
                detail="Only the user who created the site can update it",
            )

        result = await wp_sites_col.update_one(
            {"_id": ObjectId(wp_site["_id"])}, {"$set": {"name": update_data["name"]}}
        )

    result = await projects_col.update_one(
        {"_id": ObjectId(project_id)}, {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    doc = await projects_col.find_one({"_id": ObjectId(project_id)})
    wp_site = await wp_sites_col.find_one({"_id": ObjectId(doc["wp_site_id"])})
    wp_name = wp_site["name"] if wp_site else "Unknown"
    wp_url = wp_site["url"] if wp_site else None
    return format_project(doc, wp_name, wp_url)


@router.delete("/{project_id}")
async def delete_project(
    project_id: str, current_user: Annotated[dict, Depends(get_current_user)]
):
    # Check if user has permission to access this project
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if (
        current_user["id"] != project["created_by"]
        and current_user.get("role") != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the user who created the project can delete it",
        )

    result = await projects_col.delete_one({"_id": ObjectId(project_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    # Also delete all posts in this project
    await posts_col.delete_many({"project_id": ObjectId(project_id)})
    return {"message": "Project and its posts deleted"}


@router.get("/{project_id}/posts")
async def get_all_posts(
    project_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    sort_by: str = Query(
        "date-desc", regex="^(date-desc|date-asc|title-asc|title-desc|status)$"
    ),
    search: Optional[str] = Query(None),
):
    """Get all posts for a project with filter, sort, and search support."""
    # Verify project exists
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Build query filter
    query_filter = {"project_id": project_id}

    # Apply status filter if provided
    if status:
        query_filter["status"] = status

    # Apply search filter if provided (case-insensitive title search)
    if search:
        query_filter["title"] = {"$regex": search, "$options": "i"}

    # Determine sort order
    sort_field = "created_at"
    sort_direction = -1  # descending

    if sort_by == "date-asc":
        sort_field = "created_at"
        sort_direction = 1
    elif sort_by == "title-asc":
        sort_field = "title"
        sort_direction = 1
    elif sort_by == "title-desc":
        sort_field = "title"
        sort_direction = -1
    elif sort_by == "status":
        sort_field = "status"
        sort_direction = 1

    # Get total count
    total = await posts_col.count_documents(query_filter)

    # Apply pagination
    skip = (page - 1) * limit

    # Query posts with filter, sort, and pagination
    posts = []
    async for doc in (
        posts_col.find(query_filter)
        .sort(sort_field, sort_direction)
        .skip(skip)
        .limit(limit)
    ):
        # Convert ObjectId to string for response
        post_dict = {
            "id": str(doc["_id"]),
            "project_id": doc["project_id"],
            "topic": doc.get("topic"),
            "title": doc.get("title"),
            "status": doc.get("status", "draft"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at", doc.get("created_at")),
            "wp_post_id": doc.get("wp_post_id"),
            "wp_post_url": doc.get("wp_post_url"),
            "categories": doc.get("categories", []),
            "tags": doc.get("tags", []),
            "origin": doc.get("origin", "tool"),
        }
        posts.append(post_dict)

    return {"posts": posts, "total": total, "page": page, "limit": limit}
