from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from typing import Optional
from app.database import projects_col, wp_sites_col, posts_col
from app.models.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    TokenUsageResponse,
)

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
    ).model_dump()


@router.get("")
async def list_projects():
    projects = []
    async for doc in projects_col.find().sort("created_at", -1):
        wp_site = await wp_sites_col.find_one({"_id": ObjectId(doc["wp_site_id"])})
        wp_name = wp_site["name"] if wp_site else "Unknown"
        wp_url = wp_site["url"] if wp_site else None
        projects.append(format_project(doc, wp_name, wp_url))
    return projects


@router.get("/{project_id}")
async def get_project(project_id: str):
    doc = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
    wp_site = await wp_sites_col.find_one({"_id": ObjectId(doc["wp_site_id"])})
    wp_name = wp_site["name"] if wp_site else "Unknown"
    wp_url = wp_site["url"] if wp_site else None
    return format_project(doc, wp_name, wp_url)


@router.get("/{project_id}/stats")
async def get_project_stats(project_id: str):
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
            }
        },
    ]
    token_result = await posts_col.aggregate(token_pipeline).to_list(length=1)
    token_usage = TokenUsageResponse(
        research=0, outline=0, content=0, thumbnail=0, total=0
    )
    if token_result:
        token_usage = TokenUsageResponse(
            research=token_result[0].get("research", 0),
            outline=token_result[0].get("outline", 0),
            content=token_result[0].get("content", 0),
            thumbnail=token_result[0].get("thumbnail", 0),
            total=token_result[0].get("total", 0),
        )

    # Add token usage to stats response
    stats["token_usage"] = token_usage.model_dump()
    return stats


@router.post("", status_code=201)
async def create_project(data: ProjectCreate):
    # Validate wp_site exists
    wp_site = await wp_sites_col.find_one({"_id": ObjectId(data.wp_site_id)})
    if not wp_site:
        raise HTTPException(status_code=400, detail="WordPress site not found")

    doc = {
        **data.model_dump(),
        "created_at": datetime.now(timezone.utc),
    }
    result = await projects_col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return format_project(doc, wp_site["name"], wp_site["url"])


@router.put("/{project_id}")
async def update_project(project_id: str, data: ProjectUpdate):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "wp_site_id" in update_data:
        wp_site = await wp_sites_col.find_one(
            {"_id": ObjectId(update_data["wp_site_id"])}
        )
        if not wp_site:
            raise HTTPException(status_code=400, detail="WordPress site not found")

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
async def delete_project(project_id: str):
    result = await projects_col.delete_one({"_id": ObjectId(project_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    # Also delete all posts in this project
    await posts_col.delete_many({"project_id": project_id})
    return {"message": "Project and its posts deleted"}
