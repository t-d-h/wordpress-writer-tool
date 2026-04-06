"""
Job Service — helper to create and queue jobs from the API layer.
"""
import uuid
from datetime import datetime, timezone
from bson import ObjectId
from app.database import posts_col, jobs_col
from app.redis_client import publish_job


async def create_and_queue_job(post_id: str, project_id: str, job_type: str, extra_data: dict = None) -> str:
    """Create a job record and publish it to the Redis queue. Returns job_id."""
    job_id = str(uuid.uuid4())

    job_info = {
        "job_id": job_id,
        "job_type": job_type,
        "status": "pending",
        "error": None,
        "started_at": None,
        "completed_at": None,
    }

    # Add job to post's embedded jobs array
    await posts_col.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"jobs": job_info}}
    )

    # Store in jobs collection
    await jobs_col.insert_one({
        "job_id": job_id,
        "post_id": post_id,
        "project_id": project_id,
        "job_type": job_type,
        "status": "pending",
        "created_at": datetime.now(timezone.utc),
    })

    # Publish to Redis
    job_message = {
        "job_id": job_id,
        "post_id": post_id,
        "project_id": project_id,
        "job_type": job_type,
    }
    if extra_data:
        job_message.update(extra_data)

    await publish_job(job_message)

    return job_id
