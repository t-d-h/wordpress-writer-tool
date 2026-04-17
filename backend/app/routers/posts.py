from fastapi import APIRouter, HTTPException, UploadFile, File, Body, Query
from fastapi.responses import FileResponse
from bson import ObjectId
from datetime import datetime, timezone
import uuid
import os
from pydantic import BaseModel
from typing import List, Optional
from app.database import posts_col, projects_col, jobs_col
from app.models.post import PostCreate, BulkPostCreate, PostUpdate, PostResponse
from app.validation.content_validator import ContentValidationService
from app.redis_client import publish_job


class ThumbnailRequest(BaseModel):
    provider_id: str = None
    model_name: str = None


router = APIRouter(prefix="/api/posts", tags=["Posts"])


def format_post(doc: dict) -> dict:
    return PostResponse(
        id=str(doc["_id"]),
        project_id=doc["project_id"],
        topic=doc["topic"],
        additional_requests=doc.get("additional_requests", ""),
        ai_provider_id=doc.get("ai_provider_id"),
        model_name=doc.get("model_name"),
        auto_publish=doc.get("auto_publish", False),
        thumbnail_source=doc.get("thumbnail_source", "ai"),
        thumbnail_provider_id=doc.get("thumbnail_provider_id"),
        thumbnail_model_name=doc.get("thumbnail_model_name"),
        target_word_count=doc.get("target_word_count"),
        target_section_count=doc.get("target_section_count"),
        language=doc.get("language", "english"),
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
        token_usage=doc.get("token_usage", {}),
        jobs=doc.get("jobs", []),
        created_at=doc["created_at"],
        wp_post_id=doc.get("wp_post_id"),
        wp_post_url=doc.get("wp_post_url"),
        validation_results=doc.get("validation_results"),
    ).model_dump()


@router.get("/by-project/{project_id}")
async def list_posts_by_project(
    project_id: str, page: int = Query(1, ge=1), limit: int = Query(100, ge=1, le=100)
):
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    posts = []
    skip = (page - 1) * limit
    async for doc in (
        posts_col.find({"project_id": project_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    ):
        posts.append(format_post(doc))
    return {"posts": posts, "total": len(posts)}


@router.get("/{post_id}")
async def get_post(post_id: str):
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")

    if doc.get("target_word_count") and doc.get("target_section_count"):
        validator = ContentValidationService(
            min_words=doc.get("target_word_count", 0) * 0.8,
            max_words=doc.get("target_word_count", 0) * 1.2,
            min_sections=doc.get("target_section_count", 0),
            max_sections=doc.get("target_section_count", 0),
        )
        validation_results = validator.validate(
            html_content=doc.get("content", ""),
            sections=doc.get("sections", []),
        )
        doc["validation_results"] = validation_results

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
        "auto_publish": data.auto_publish,
        "thumbnail_source": data.thumbnail_source,
        "thumbnail_provider_id": data.thumbnail_provider_id,
        "thumbnail_model_name": data.thumbnail_model_name,
        "target_word_count": data.target_word_count,
        "target_section_count": data.target_section_count,
        "language": data.language,
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
        "token_usage": {
            "research": 0,
            "outline": 0,
            "content": 0,
            "thumbnail": 0,
            "total": 0,
        },
        "jobs": [],
        "created_at": datetime.now(timezone.utc),
        "wp_post_id": None,
        "wp_post_url": None,
    }
    result = await posts_col.insert_one(post_doc)
    post_id = str(result.inserted_id)
    post_doc["_id"] = result.inserted_id

    # Perform validation
    if data.target_word_count is not None and data.target_section_count is not None:
        validator = ContentValidationService(
            min_words=data.target_word_count * 0.8,
            max_words=data.target_word_count * 1.2,
            min_sections=data.target_section_count,
            max_sections=data.target_section_count,
        )
        validation_results = validator.validate(
            html_content=post_doc.get("content", ""),
            sections=post_doc.get("sections", []),
        )
        post_doc["validation_results"] = validation_results
        await posts_col.update_one(
            {"_id": result.inserted_id},
            {"$set": {"validation_results": validation_results}},
        )

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
            "target_section_count": data.target_section_count,
            "target_word_count": data.target_word_count,
            "language": data.language,
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
            auto_publish=data.auto_publish,
            thumbnail_source=data.thumbnail_source,
            thumbnail_provider_id=data.thumbnail_provider_id,
            thumbnail_model_name=data.thumbnail_model_name,
            target_word_count=data.target_word_count,
            target_section_count=data.target_section_count,
            language=data.language,
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

    # Perform validation
    target_word_count = doc.get("target_word_count")
    target_section_count = doc.get("target_section_count")

    if target_word_count is not None and target_section_count is not None:
        validator = ContentValidationService(
            min_words=target_word_count * 0.8,
            max_words=target_word_count * 1.2,
            min_sections=target_section_count,
            max_sections=target_section_count,
        )
        validation_results = validator.validate(
            html_content=doc.get("content", ""),
            sections=doc.get("sections", []),
        )
        doc["validation_results"] = validation_results
        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"validation_results": validation_results}},
        )

    return format_post(doc)


@router.delete("/{post_id}")
async def delete_post(post_id: str):
    result = await posts_col.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    await jobs_col.delete_many({"post_id": post_id})
    return {"message": "Post deleted"}


class PublishRequest(BaseModel):
    force_publish: bool = False


@router.post("/{post_id}/publish")
async def publish_post(post_id: str, request: PublishRequest = None):
    """Queue a publish job for a post."""
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")
    if not doc.get("content"):
        raise HTTPException(status_code=400, detail="Post has no content to publish")

    force_publish = request.force_publish if request else False

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
            "force_publish": force_publish,
        }
    )
    return {"message": "Publish job queued", "job_id": job_id}


@router.post("/{post_id}/unpublish")
async def unpublish_post(post_id: str):
    """Unpublish a post from WordPress (set to draft)."""
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")

    # Create an unpublish job entry
    job_id = str(uuid.uuid4())
    job_info = {
        "job_id": job_id,
        "job_type": "unpublish",
        "status": "completed",
        "error": None,
        "started_at": datetime.now(timezone.utc),
        "completed_at": datetime.now(timezone.utc),
    }
    await posts_col.update_one(
        {"_id": ObjectId(post_id)}, {"$push": {"jobs": job_info}}
    )
    await jobs_col.insert_one(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": doc["project_id"],
            "job_type": "unpublish",
            "status": "completed",
            "created_at": datetime.now(timezone.utc),
            "started_at": datetime.now(timezone.utc),
            "completed_at": datetime.now(timezone.utc),
        }
    )

    # If post has a WordPress post ID, update it to draft status
    if doc.get("wp_post_id"):
        from app.services import wp_service

        try:
            await wp_service.update_wp_post(
                doc["project_id"],
                doc["wp_post_id"],
                title=doc.get("title"),
                content=doc.get("content", ""),
                status="draft",
            )
        except Exception as e:
            # Log error but continue with database update
            print(f"Warning: Failed to update WordPress post: {e}")

    # Update database status
    result = await posts_col.update_one(
        {"_id": ObjectId(post_id)}, {"$set": {"status": "draft"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post unpublished", "job_id": job_id}


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
async def generate_thumbnail(post_id: str, request: ThumbnailRequest = None):
    """Queue thumbnail generation job with optional provider/model."""
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")

    provider_id = request.provider_id if request else None
    model_name = request.model_name if request else None

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

    # Resize to 150x150 square
    from app.utils.image_utils import resize_to_square

    resized_path = resize_to_square(filepath, size=150)

    # Create a completed job entry for tracking
    job_id = str(uuid.uuid4())
    job_info = {
        "job_id": job_id,
        "job_type": "thumbnail",
        "status": "completed",
        "error": None,
        "started_at": datetime.now(timezone.utc),
        "completed_at": datetime.now(timezone.utc),
    }

    await posts_col.update_one(
        {"_id": ObjectId(post_id)},
        {
            "$set": {
                "thumbnail_url": resized_path,
                "thumbnail_done": True,
            },
            "$push": {"jobs": job_info},
        },
    )

    # Store job in jobs collection for tracking
    await jobs_col.insert_one(
        {
            "job_id": job_id,
            "post_id": post_id,
            "project_id": doc["project_id"],
            "job_type": "thumbnail",
            "status": "completed",
            "created_at": datetime.now(timezone.utc),
            "started_at": datetime.now(timezone.utc),
            "completed_at": datetime.now(timezone.utc),
        }
    )

    return {"message": "Thumbnail uploaded and resized", "thumbnail_url": resized_path}


@router.get("/{post_id}/thumbnail")
async def get_thumbnail(post_id: str):
    """Serve the thumbnail image for a post."""
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")

    thumbnail_url = doc.get("thumbnail_url")
    if not thumbnail_url:
        raise HTTPException(status_code=404, detail="No thumbnail found for this post")

    if not os.path.exists(thumbnail_url):
        raise HTTPException(
            status_code=404, detail="Thumbnail file not found on server"
        )

    return FileResponse(thumbnail_url)


@router.post("/{post_id}/update-thumbnail-to-wp")
async def update_thumbnail_to_wp(post_id: str):
    """Upload thumbnail to WordPress and set as featured image."""
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")

    if not doc.get("thumbnail_url"):
        raise HTTPException(status_code=400, detail="No thumbnail found for this post")

    # Import wp_service
    from app.services import wp_service

    try:
        # Upload thumbnail to WordPress media library
        media = await wp_service.upload_media(doc["project_id"], doc["thumbnail_url"])
        thumbnail_media_id = media.get("id")

        # Update WordPress post with featured image
        if doc.get("wp_post_id"):
            # Post exists in WordPress, update it
            wp_post = await wp_service.update_wp_post(
                doc["project_id"],
                doc["wp_post_id"],
                thumbnail_media_id=thumbnail_media_id,
            )
        else:
            # Post doesn't exist in WordPress yet, create it as draft
            wp_post = await wp_service.create_wp_post(
                doc["project_id"],
                title=doc.get("title", doc["topic"]),
                content=doc.get("content", ""),
                meta_description=doc.get("meta_description", ""),
                thumbnail_media_id=thumbnail_media_id,
                status="draft",
            )

        # Update database with WordPress post info
        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$set": {
                    "wp_post_id": wp_post.get("id"),
                    "wp_post_url": wp_post.get("link"),
                }
            },
        )

        return {
            "message": "Thumbnail uploaded to WordPress and set as featured image",
            "media_id": thumbnail_media_id,
            "wp_post_id": wp_post.get("id"),
            "wp_post_url": wp_post.get("link"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
