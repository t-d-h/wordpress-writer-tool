from fastapi import APIRouter, HTTPException, UploadFile, File
from bson import ObjectId
from datetime import datetime, timezone
import uuid
import os
from app.database import posts_col, projects_col, jobs_col
from app.models.post import PostCreate, BulkPostCreate, PostUpdate, PostResponse
from app.redis_client import publish_job

router = APIRouter(prefix="/api/posts", tags=["Posts"])


def format_post(doc: dict) -> dict:
    return PostResponse(
        id=str(doc["_id"]),
        project_id=doc["project_id"],
        topic=doc["topic"],
        additional_requests=doc.get("additional_requests", ""),
        ai_provider_id=doc.get("ai_provider_id"),
        model_name=doc.get("model_name"),
        title=doc.get("title"),
        meta_description=doc.get("meta_description"),
        outline=doc.get("outline"),
        sections=doc.get("sections", []),
        content=doc.get("content"),
        thumbnail_url=doc.get("thumbnail_url"),
        status=doc.get("status", "draft"),
        research_data=doc.get("research_data"),
        research_done=doc.get("research_done", False),
        content_done=doc.get("content_done", False),
        thumbnail_done=doc.get("thumbnail_done", False),
        sections_done=doc.get("sections_done", False),
        token_usage=doc.get("token_usage", {}),
        jobs=doc.get("jobs", []),
        created_at=doc["created_at"],
        wp_post_id=doc.get("wp_post_id"),
    ).model_dump()


@router.get("/by-project/{project_id}")
async def list_posts_by_project(project_id: str):
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    posts = []
    async for doc in posts_col.find({"project_id": project_id}).sort("created_at", -1):
        posts.append(format_post(doc))
    return posts


@router.get("/{post_id}")
async def get_post(post_id: str):
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")
    return format_post(doc)


@router.post("", status_code=201)
async def create_post(data: PostCreate):
    """Create a single post and queue AI pipeline jobs."""
    project = await projects_col.find_one({"_id": ObjectId(data.project_id)})
    if not project:
        raise HTTPException(status_code=400, detail="Project not found")

    post_doc = {
        "project_id": data.project_id,
        "topic": data.topic,
        "additional_requests": data.additional_requests or "",
        "ai_provider_id": data.ai_provider_id,
        "model_name": data.model_name,
        "title": None,
        "meta_description": None,
        "outline": None,
        "sections": [],
        "content": None,
        "thumbnail_url": None,
        "status": "draft",
        "research_data": None,
        "research_done": False,
        "content_done": False,
        "thumbnail_done": False,
        "sections_done": False,
        "token_usage": {
            "research": 0,
            "outline": 0,
            "content": 0,
            "thumbnail": 0,
            "section_images": 0,
            "total": 0,
        },
        "jobs": [],
        "created_at": datetime.now(timezone.utc),
        "wp_post_id": None,
    }
    result = await posts_col.insert_one(post_doc)
    post_id = str(result.inserted_id)
    post_doc["_id"] = result.inserted_id

    # Create the research job (first step in pipeline)
    job_id = str(uuid.uuid4())
    job_info = {
        "job_id": job_id,
        "job_type": "research",
        "status": "pending",
        "error": None,
        "started_at": None,
        "completed_at": None,
    }
    await posts_col.update_one(
        {"_id": result.inserted_id}, {"$push": {"jobs": job_info}}
    )

    # Store job in jobs collection for tracking
    await jobs_col.insert_one(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": data.project_id,
            "job_type": "research",
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
        }
    )

    # Publish job to Redis
    await publish_job(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": data.project_id,
            "job_type": "research",
            "topic": data.topic,
            "additional_requests": data.additional_requests or "",
            "ai_provider_id": data.ai_provider_id,
            "model_name": data.model_name,
        }
    )

    post_doc["jobs"] = [job_info]
    return format_post(post_doc)


@router.post("/bulk", status_code=201)
async def create_bulk_posts(data: BulkPostCreate):
    """Create multiple posts from a list of topics."""
    project = await projects_col.find_one({"_id": ObjectId(data.project_id)})
    if not project:
        raise HTTPException(status_code=400, detail="Project not found")

    created_posts = []
    for topic in data.topics:
        single = PostCreate(
            project_id=data.project_id,
            topic=topic,
            additional_requests=data.additional_requests,
            ai_provider_id=data.ai_provider_id,
            model_name=data.model_name,
        )
        # Reuse single post creation logic
        post = await create_post(single)
        created_posts.append(post)

    return created_posts


@router.put("/{post_id}")
async def update_post(post_id: str, data: PostUpdate):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    # Convert sections to dicts if present
    if "sections" in update_data:
        update_data["sections"] = [
            s.model_dump() if hasattr(s, "model_dump") else s
            for s in update_data["sections"]
        ]
    result = await posts_col.update_one(
        {"_id": ObjectId(post_id)}, {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    return format_post(doc)


@router.delete("/{post_id}")
async def delete_post(post_id: str):
    result = await posts_col.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    await jobs_col.delete_many({"post_id": post_id})
    return {"message": "Post deleted"}


@router.post("/{post_id}/publish")
async def publish_post(post_id: str):
    """Queue a publish job for a post."""
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")
    if not doc.get("content"):
        raise HTTPException(status_code=400, detail="Post has no content to publish")

    job_id = str(uuid.uuid4())
    job_info = {
        "job_id": job_id,
        "job_type": "publish",
        "status": "pending",
        "error": None,
        "started_at": None,
        "completed_at": None,
    }
    await posts_col.update_one(
        {"_id": ObjectId(post_id)}, {"$push": {"jobs": job_info}}
    )
    await jobs_col.insert_one(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": doc["project_id"],
            "job_type": "publish",
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
        }
    )
    await publish_job(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": doc["project_id"],
            "job_type": "publish",
        }
    )
    return {"message": "Publish job queued", "job_id": job_id}


@router.post("/{post_id}/unpublish")
async def unpublish_post(post_id: str):
    """Mark a post as draft."""
    result = await posts_col.update_one(
        {"_id": ObjectId(post_id)}, {"$set": {"status": "draft"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post unpublished"}


@router.post("/{post_id}/generate-outline")
async def generate_outline(post_id: str):
    """Queue outline generation job."""
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")

    job_id = str(uuid.uuid4())
    job_info = {
        "job_id": job_id,
        "job_type": "outline",
        "status": "pending",
        "error": None,
        "started_at": None,
        "completed_at": None,
    }
    await posts_col.update_one(
        {"_id": ObjectId(post_id)}, {"$push": {"jobs": job_info}}
    )
    await jobs_col.insert_one(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": doc["project_id"],
            "job_type": "outline",
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
        }
    )
    await publish_job(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": doc["project_id"],
            "job_type": "outline",
            "ai_provider_id": doc.get("ai_provider_id"),
            "model_name": doc.get("model_name"),
        }
    )
    return {"message": "Outline generation queued", "job_id": job_id}


@router.post("/{post_id}/generate-content")
async def generate_content(post_id: str):
    """Queue content generation job."""
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")

    job_id = str(uuid.uuid4())
    job_info = {
        "job_id": job_id,
        "job_type": "content",
        "status": "pending",
        "error": None,
        "started_at": None,
        "completed_at": None,
    }
    await posts_col.update_one(
        {"_id": ObjectId(post_id)}, {"$push": {"jobs": job_info}}
    )
    await jobs_col.insert_one(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": doc["project_id"],
            "job_type": "content",
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
        }
    )
    await publish_job(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": doc["project_id"],
            "job_type": "content",
        }
    )
    return {"message": "Content generation queued", "job_id": job_id}


@router.post("/{post_id}/generate-thumbnail")
async def generate_thumbnail(
    post_id: str, provider_id: str = None, model_name: str = None
):
    """Queue thumbnail generation job with optional provider/model."""
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")

    job_id = str(uuid.uuid4())
    job_info = {
        "job_id": job_id,
        "job_type": "thumbnail",
        "status": "pending",
        "error": None,
        "started_at": None,
        "completed_at": None,
    }
    await posts_col.update_one(
        {"_id": ObjectId(post_id)}, {"$push": {"jobs": job_info}}
    )
    await jobs_col.insert_one(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": doc["project_id"],
            "job_type": "thumbnail",
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
        }
    )
    await publish_job(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": doc["project_id"],
            "job_type": "thumbnail",
            "ai_provider_id": provider_id or doc.get("ai_provider_id"),
            "model_name": model_name or doc.get("model_name"),
        }
    )
    return {"message": "Thumbnail generation queued", "job_id": job_id}


@router.post("/{post_id}/upload-thumbnail")
async def upload_thumbnail(post_id: str, file: UploadFile = File(...)):
    """Upload a thumbnail image for a post."""
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = f"/tmp/wp_images/{filename}"

    os.makedirs("/tmp/wp_images", exist_ok=True)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    await posts_col.update_one(
        {"_id": ObjectId(post_id)},
        {
            "$set": {
                "thumbnail_url": filepath,
                "thumbnail_done": True,
            }
        },
    )

    return {"message": "Thumbnail uploaded", "thumbnail_url": filepath}


@router.post("/{post_id}/generate-section-images")
async def generate_section_images(post_id: str):
    """Queue section images generation job."""
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")

    job_id = str(uuid.uuid4())
    job_info = {
        "job_id": job_id,
        "job_type": "section_images",
        "status": "pending",
        "error": None,
        "started_at": None,
        "completed_at": None,
    }
    await posts_col.update_one(
        {"_id": ObjectId(post_id)}, {"$push": {"jobs": job_info}}
    )
    await jobs_col.insert_one(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": doc["project_id"],
            "job_type": "section_images",
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
        }
    )
    await publish_job(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": doc["project_id"],
            "job_type": "section_images",
        }
    )
    return {"message": "Section images generation queued", "job_id": job_id}
