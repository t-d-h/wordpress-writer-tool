"""
Task definitions for each step of the AI post generation pipeline.
Each task updates MongoDB and Redis with status/results.
"""
import asyncio
import traceback
from datetime import datetime, timezone
from bson import ObjectId
from app.database import posts_col, jobs_col
from app.redis_client import set_job_status
from app.services import ai_service, image_service, wp_service


async def _update_job_status(job_id: str, post_id: str, status: str, error: str = None):
    """Update job status in both MongoDB and Redis."""
    now = datetime.now(timezone.utc)

    # Update in jobs collection
    update = {"status": status}
    if status == "running":
        update["started_at"] = now
    if status in ("completed", "failed"):
        update["completed_at"] = now
    if error:
        update["error"] = error

    await jobs_col.update_one({"job_id": job_id}, {"$set": update})

    # Update embedded job in posts collection
    await posts_col.update_one(
        {"_id": ObjectId(post_id), "jobs.job_id": job_id},
        {"$set": {
            "jobs.$.status": status,
            **({"jobs.$.error": error} if error else {}),
            **({"jobs.$.started_at": now} if status == "running" else {}),
            **({"jobs.$.completed_at": now} if status in ("completed", "failed") else {}),
        }}
    )

    # Cache in Redis
    await set_job_status(job_id, {
        "job_id": job_id,
        "post_id": post_id,
        "status": status,
        "error": error,
    })


async def run_research(job_data: dict):
    """Research a topic using AI."""
    job_id = job_data["job_id"]
    post_id = job_data["post_id"]

    try:
        await _update_job_status(job_id, post_id, "running")

        topic = job_data["topic"]
        additional = job_data.get("additional_requests", "")

        research_data, tokens = await ai_service.research_topic(topic, additional)

        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {
                "research_data": research_data,
                "research_done": True,
                "token_usage.research": tokens,
            }}
        )

        # Update total tokens
        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        tu = post.get("token_usage", {})
        total = sum(v for k, v in tu.items() if k != "total" and isinstance(v, int))
        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"token_usage.total": total}}
        )

        await _update_job_status(job_id, post_id, "completed")
        print(f"[TASK] Research completed for post {post_id}")

    except Exception as e:
        print(f"[TASK] Research failed for post {post_id}: {e}")
        traceback.print_exc()
        await _update_job_status(job_id, post_id, "failed", str(e))


async def run_outline(job_data: dict):
    """Generate an outline for a post."""
    job_id = job_data["job_id"]
    post_id = job_data["post_id"]

    try:
        await _update_job_status(job_id, post_id, "running")

        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise Exception("Post not found")

        topic = post["topic"]
        additional = post.get("additional_requests", "")
        research_data = post.get("research_data", {})

        outline, tokens = await ai_service.generate_outline(topic, research_data, additional)

        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {
                "outline": outline,
                "title": outline.get("title", topic),
                "meta_description": outline.get("meta_description", ""),
                "token_usage.outline": tokens,
            }}
        )

        # Update total tokens
        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        tu = post.get("token_usage", {})
        total = sum(v for k, v in tu.items() if k != "total" and isinstance(v, int))
        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"token_usage.total": total}}
        )

        await _update_job_status(job_id, post_id, "completed")
        print(f"[TASK] Outline completed for post {post_id}")

    except Exception as e:
        print(f"[TASK] Outline failed for post {post_id}: {e}")
        traceback.print_exc()
        await _update_job_status(job_id, post_id, "failed", str(e))


async def run_content(job_data: dict):
    """Generate full content for a post."""
    job_id = job_data["job_id"]
    post_id = job_data["post_id"]

    try:
        await _update_job_status(job_id, post_id, "running")

        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise Exception("Post not found")

        topic = post["topic"]
        additional = post.get("additional_requests", "")
        outline = post.get("outline", {})

        if not outline:
            raise Exception("No outline found. Generate outline first.")

        full_html, sections, tokens = await ai_service.generate_full_content(
            topic, outline, additional
        )

        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {
                "content": full_html,
                "sections": sections,
                "content_done": True,
                "sections_done": True,
                "token_usage.content": tokens,
            }}
        )

        # Update total tokens
        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        tu = post.get("token_usage", {})
        total = sum(v for k, v in tu.items() if k != "total" and isinstance(v, int))
        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"token_usage.total": total}}
        )

        await _update_job_status(job_id, post_id, "completed")
        print(f"[TASK] Content generated for post {post_id}")

    except Exception as e:
        print(f"[TASK] Content failed for post {post_id}: {e}")
        traceback.print_exc()
        await _update_job_status(job_id, post_id, "failed", str(e))


async def run_thumbnail(job_data: dict):
    """Generate a thumbnail for a post."""
    job_id = job_data["job_id"]
    post_id = job_data["post_id"]

    try:
        await _update_job_status(job_id, post_id, "running")

        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise Exception("Post not found")

        filepath = await image_service.generate_thumbnail(
            post["topic"],
            post.get("title", post["topic"])
        )

        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {
                "thumbnail_url": filepath,
                "thumbnail_done": True,
            }}
        )

        await _update_job_status(job_id, post_id, "completed")
        print(f"[TASK] Thumbnail generated for post {post_id}")

    except Exception as e:
        print(f"[TASK] Thumbnail failed for post {post_id}: {e}")
        traceback.print_exc()
        await _update_job_status(job_id, post_id, "failed", str(e))


async def run_section_images(job_data: dict):
    """Generate images for each section of a post."""
    job_id = job_data["job_id"]
    post_id = job_data["post_id"]

    try:
        await _update_job_status(job_id, post_id, "running")

        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise Exception("Post not found")

        sections = post.get("sections", [])
        for i, section in enumerate(sections):
            if section.get("title"):
                filepath = await image_service.generate_section_image(
                    post["topic"], section["title"]
                )
                sections[i]["image_url"] = filepath

        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"sections": sections}}
        )

        await _update_job_status(job_id, post_id, "completed")
        print(f"[TASK] Section images generated for post {post_id}")

    except Exception as e:
        print(f"[TASK] Section images failed for post {post_id}: {e}")
        traceback.print_exc()
        await _update_job_status(job_id, post_id, "failed", str(e))


async def run_publish(job_data: dict):
    """Publish a post to WordPress."""
    job_id = job_data["job_id"]
    post_id = job_data["post_id"]
    project_id = job_data["project_id"]

    try:
        await _update_job_status(job_id, post_id, "running")

        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise Exception("Post not found")

        # Upload thumbnail if exists
        thumbnail_media_id = None
        if post.get("thumbnail_url"):
            try:
                media = await wp_service.upload_media(project_id, post["thumbnail_url"])
                thumbnail_media_id = media.get("id")
            except Exception as e:
                print(f"[TASK] Thumbnail upload failed: {e}, continuing without thumbnail")

        # Build final content with section images
        content = post.get("content", "")

        # Create or update WP post
        if post.get("wp_post_id"):
            wp_post = await wp_service.update_wp_post(
                project_id,
                post["wp_post_id"],
                title=post.get("title"),
                content=content,
                status="publish",
                thumbnail_media_id=thumbnail_media_id,
            )
        else:
            wp_post = await wp_service.create_wp_post(
                project_id,
                title=post.get("title", post["topic"]),
                content=content,
                meta_description=post.get("meta_description", ""),
                thumbnail_media_id=thumbnail_media_id,
                status="publish",
            )

        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {
                "status": "published",
                "wp_post_id": wp_post.get("id"),
            }}
        )

        await _update_job_status(job_id, post_id, "completed")
        print(f"[TASK] Post {post_id} published to WordPress (WP ID: {wp_post.get('id')})")

    except Exception as e:
        print(f"[TASK] Publish failed for post {post_id}: {e}")
        traceback.print_exc()
        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"status": "failed"}}
        )
        await _update_job_status(job_id, post_id, "failed", str(e))
