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
from app.services.job_service import create_and_queue_job
from app.logging_config import setup_logging

logger = setup_logging()


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
        {
            "$set": {
                "jobs.$.status": status,
                **({"jobs.$.error": error} if error else {}),
                **({"jobs.$.started_at": now} if status == "running" else {}),
                **(
                    {"jobs.$.completed_at": now}
                    if status in ("completed", "failed")
                    else {}
                ),
            }
        },
    )

    # Cache in Redis
    await set_job_status(
        job_id,
        {
            "job_id": job_id,
            "post_id": post_id,
            "status": status,
            "error": error,
        },
    )


async def queue_next_job(
    post_id: str, project_id: str, next_job_type: str, extra_data: dict = None
) -> str:
    """Queue the next job in the pipeline after current job completes successfully."""
    logger.info(f"[PIPELINE] Queuing {next_job_type} job for post {post_id}")
    job_id = await create_and_queue_job(post_id, project_id, next_job_type, extra_data)
    logger.info(f"[PIPELINE] Queued {next_job_type} job {job_id} for post {post_id}")
    return job_id


async def run_research(job_data: dict):
    """Research a topic using AI."""
    job_id = job_data["job_id"]
    post_id = job_data["post_id"]

    try:
        logger.info(f"[RESEARCH] Starting research for post {post_id}")

        await _update_job_status(job_id, post_id, "running")

        topic = job_data["topic"]
        additional = job_data.get("additional_requests", "")
        provider_id = job_data.get("ai_provider_id")
        model_name = job_data.get("model_name")
        language = job_data.get("language", "vietnamese")

        logger.info(f"[RESEARCH] Topic: {topic}")
        logger.info(f"[RESEARCH] Additional requests: {additional}")
        logger.info(f"[RESEARCH] Using AI provider: {provider_id}")
        logger.info(f"[RESEARCH] Calling AI model: {model_name}")
        logger.info(f"[RESEARCH] Language: {language}")

        research_data, total_tokens = await ai_service.research_topic(
            topic, additional, provider_id, model_name, language
        )

        logger.info(f"[RESEARCH] AI call completed, {total_tokens} tokens used")
        logger.info(f"[RESEARCH] Generated {len(research_data)} research points")

        logger.info(f"[RESEARCH] Updating database with research data")
        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$set": {
                    "research_data": research_data,
                    "research_done": True,
                    "token_usage.research": total_tokens,
                }
            },
        )

        # Update total tokens
        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        tu = post.get("token_usage", {})
        total = sum(v for k, v in tu.items() if k != "total" and isinstance(v, int))
        await posts_col.update_one(
            {"_id": ObjectId(post_id)}, {"$set": {"token_usage.total": total}}
        )

        await _update_job_status(job_id, post_id, "completed")
        logger.info(f"[RESEARCH] Research completed successfully")

        # Queue next job in pipeline
        project_id = job_data.get("project_id")
        if project_id:
            await queue_next_job(post_id, project_id, "outline")
            logger.info(f"[PIPELINE] Queued outline job for post {post_id}")

    except Exception as e:
        logger.error(f"[RESEARCH] Research failed for post {post_id}: {e}")
        logger.exception("[RESEARCH] Full stack trace:")
        await _update_job_status(job_id, post_id, "failed", str(e))


async def run_outline(job_data: dict):
    """Generate an outline for a post."""
    job_id = job_data["job_id"]
    post_id = job_data["post_id"]

    try:
        logger.info(f"[OUTLINE] Starting outline generation for post {post_id}")

        await _update_job_status(job_id, post_id, "running")

        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise Exception("Post not found")

        topic = post["topic"]
        additional = post.get("additional_requests", "")
        research_data = post.get("research_data", {})
        provider_id = post.get("ai_provider_id")
        model_name = post.get("model_name")
        language = post.get("language", "vietnamese")

        logger.info(f"[OUTLINE] Topic: {topic}")
        logger.info(f"[OUTLINE] Using research data with {len(research_data)} points")
        logger.info(f"[OUTLINE] Calling AI provider: {provider_id}")
        logger.info(f"[OUTLINE] Calling AI model: {model_name}")
        logger.info(f"[OUTLINE] Language: {language}")

        outline, tokens = await ai_service.generate_outline(
            topic, research_data, additional, provider_id, model_name, language
        )

        logger.info(f"[OUTLINE] AI call completed, {tokens} tokens used")
        logger.info(
            f"[OUTLINE] Generated outline with {len(outline.get('sections', []))} sections"
        )

        logger.info(f"[OUTLINE] Updating database with outline")
        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$set": {
                    "outline": outline,
                    "title": outline.get("title", topic),
                    "meta_description": outline.get("meta_description", ""),
                    "token_usage.outline": tokens,
                }
            },
        )

        # Update total tokens
        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        tu = post.get("token_usage", {})
        total = sum(v for k, v in tu.items() if k != "total" and isinstance(v, int))
        await posts_col.update_one(
            {"_id": ObjectId(post_id)}, {"$set": {"token_usage.total": total}}
        )

        await _update_job_status(job_id, post_id, "completed")
        logger.info(f"[OUTLINE] Outline completed successfully")

        # Queue next job in pipeline
        project_id = post.get("project_id")
        if project_id:
            await queue_next_job(post_id, project_id, "content")
            logger.info(f"[PIPELINE] Queued content job for post {post_id}")

    except Exception as e:
        logger.error(f"[OUTLINE] Outline failed for post {post_id}: {e}")
        logger.exception("[OUTLINE] Full stack trace:")
        await _update_job_status(job_id, post_id, "failed", str(e))


async def run_content(job_data: dict):
    """Generate full content for a post."""
    job_id = job_data["job_id"]
    post_id = job_data["post_id"]

    try:
        logger.info(f"[CONTENT] Starting content generation for post {post_id}")

        await _update_job_status(job_id, post_id, "running")

        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise Exception("Post not found")

        topic = post["topic"]
        additional = post.get("additional_requests", "")
        outline = post.get("outline", {})
        provider_id = post.get("ai_provider_id")
        model_name = post.get("model_name")
        target_word_count = post.get("target_word_count")
        target_section_count = post.get("target_section_count")

        logger.info(f"[CONTENT] Topic: {topic}")
        logger.info(
            f"[CONTENT] Outline has {len(outline.get('sections', []))} sections"
        )
        logger.info(f"[CONTENT] Calling AI provider: {provider_id}")
        logger.info(f"[CONTENT] Calling AI model: {model_name}")
        logger.info(f"[CONTENT] Target word count: {target_word_count}")
        logger.info(f"[CONTENT] Target section count: {target_section_count}")

        if not outline:
            raise Exception("No outline found. Generate outline first.")

        (
            full_html,
            sections,
            total_tokens,
        ) = await ai_service.generate_full_content(
            topic, outline, additional, provider_id, model_name, target_word_count
        )

        logger.info(f"[CONTENT] AI call completed, {total_tokens} tokens used")
        logger.info(f"[CONTENT] Generated {len(full_html)} characters of content")
        logger.info(f"[CONTENT] Generated {len(sections)} sections")

        logger.info(f"[CONTENT] Updating database with content")
        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$set": {
                    "content": full_html,
                    "sections": sections,
                    "content_done": True,
                    "token_usage.content": total_tokens,
                }
            },
        )

        # Update total tokens
        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        tu = post.get("token_usage", {})
        total = sum(v for k, v in tu.items() if k != "total" and isinstance(v, int))
        await posts_col.update_one(
            {"_id": ObjectId(post_id)}, {"$set": {"token_usage.total": total}}
        )

        await _update_job_status(job_id, post_id, "completed")
        logger.info(f"[CONTENT] Content generation completed successfully")

        # Queue next job in pipeline
        project_id = post.get("project_id")
        if project_id:
            await queue_next_job(post_id, project_id, "thumbnail")
            logger.info(f"[PIPELINE] Queued thumbnail job for post {post_id}")

    except Exception as e:
        logger.error(f"[CONTENT] Content failed for post {post_id}: {e}")
        logger.exception("[CONTENT] Full stack trace:")
        await _update_job_status(job_id, post_id, "failed", str(e))


async def run_thumbnail(job_data: dict):
    """Generate a thumbnail for a post."""
    job_id = job_data["job_id"]
    post_id = job_data["post_id"]

    try:
        logger.info(f"[THUMBNAIL] Starting thumbnail generation for post {post_id}")

        await _update_job_status(job_id, post_id, "running")

        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise Exception("Post not found")

        topic = post["topic"]
        title = post.get("title", topic)
        # Use provider/model from job_data first, then fall back to post document
        provider_id = job_data.get("ai_provider_id") or post.get(
            "thumbnail_provider_id"
        )
        model_name = job_data.get("model_name") or post.get("thumbnail_model_name")

        logger.info(f"[THUMBNAIL] Topic: {topic}")
        logger.info(f"[THUMBNAIL] Title: {title}")
        logger.info(f"[THUMBNAIL] Provider ID: {provider_id}")
        logger.info(f"[THUMBNAIL] Model: {model_name}")
        logger.info(f"[THUMBNAIL] Calling image service")

        filepath = await image_service.generate_thumbnail(
            topic, title, provider_id, model_name
        )

        logger.info(f"[THUMBNAIL] Generated thumbnail: {filepath}")

        logger.info(f"[THUMBNAIL] Updating database")
        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$set": {
                    "thumbnail_url": filepath,
                    "thumbnail_done": True,
                }
            },
        )

        await _update_job_status(job_id, post_id, "completed")
        logger.info(f"[THUMBNAIL] Thumbnail completed successfully")

        # Queue next job in pipeline
        project_id = post.get("project_id")
        if project_id:
            await queue_next_job(post_id, project_id, "publish")
            logger.info(f"[PIPELINE] Queued publish job for post {post_id}")

    except Exception as e:
        logger.error(f"[THUMBNAIL] Thumbnail failed for post {post_id}: {e}")
        logger.exception("[THUMBNAIL] Full stack trace:")
        await _update_job_status(job_id, post_id, "failed", str(e))


async def run_publish(job_data: dict):
    """Publish a post to WordPress."""
    job_id = job_data["job_id"]
    post_id = job_data["post_id"]
    project_id = job_data["project_id"]

    try:
        logger.info(f"[PUBLISH] Starting publish for post {post_id}")

        await _update_job_status(job_id, post_id, "running")

        post = await posts_col.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise Exception("Post not found")

        content = post.get("content", "")
        logger.info(f"[PUBLISH] Post has {len(content)} characters")

        # Check force_publish flag first, then fall back to auto_publish
        force_publish = job_data.get("force_publish", False)
        auto_publish = post.get("auto_publish", False)
        should_publish = force_publish or auto_publish
        logger.info(f"[PUBLISH] Force publish: {force_publish}")
        logger.info(f"[PUBLISH] Auto-publish: {auto_publish}")
        logger.info(f"[PUBLISH] Will publish: {should_publish}")

        # Upload thumbnail if exists
        thumbnail_media_id = None
        if post.get("thumbnail_url"):
            logger.info(f"[PUBLISH] Thumbnail exists: True")
            logger.info(f"[PUBLISH] Thumbnail URL: {post.get('thumbnail_url')}")
            logger.info(f"[PUBLISH] Uploading thumbnail to WordPress...")
            try:
                media = await wp_service.upload_media(project_id, post["thumbnail_url"])
                thumbnail_media_id = media.get("id")
                logger.info(
                    f"[PUBLISH] Thumbnail uploaded, media ID: {thumbnail_media_id}"
                )
            except Exception as e:
                logger.error(f"[PUBLISH] Thumbnail upload failed with exception: {e}")
                logger.exception("[PUBLISH] Full stack trace:")
                logger.warning(f"[PUBLISH] Continuing without thumbnail")
        else:
            logger.info(f"[PUBLISH] Thumbnail exists: False")

        # Build final content with section images
        content = post.get("content", "")

        # Determine status based on force_publish and auto_publish flags
        status = "publish" if should_publish else "draft"
        logger.info(f"[PUBLISH] WordPress status: {status}")

        # Create or update WP post
        logger.info(f"[PUBLISH] Creating/updating WordPress post...")
        if post.get("wp_post_id"):
            wp_post = await wp_service.update_wp_post(
                project_id,
                post["wp_post_id"],
                title=post.get("title"),
                content=content,
                status=status,
                thumbnail_media_id=thumbnail_media_id,
            )
        else:
            wp_post = await wp_service.create_wp_post(
                project_id,
                title=post.get("title", post["topic"]),
                content=content,
                meta_description=post.get("meta_description", ""),
                thumbnail_media_id=thumbnail_media_id,
                status=status,
            )

        logger.info(f"[PUBLISH] WordPress post ID: {wp_post.get('id')}")
        logger.info(f"[PUBLISH] WordPress post URL: {wp_post.get('link')}")

        # Set post status based on force_publish and auto_publish flags
        post_status = "published" if should_publish else "draft"
        logger.info(
            f"[PUBLISH] Updating database with WP post ID, URL, and status: {post_status}"
        )
        await posts_col.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$set": {
                    "status": post_status,
                    "wp_post_id": wp_post.get("id"),
                    "wp_post_url": wp_post.get("link"),
                }
            },
        )

        await _update_job_status(job_id, post_id, "completed")
        logger.info(f"[PUBLISH] Publish completed successfully")

    except Exception as e:
        logger.error(f"[PUBLISH] Publish failed for post {post_id}: {e}")
        logger.exception("[PUBLISH] Full stack trace:")
        await posts_col.update_one(
            {"_id": ObjectId(post_id)}, {"$set": {"status": "failed"}}
        )
        await _update_job_status(job_id, post_id, "failed", str(e))
