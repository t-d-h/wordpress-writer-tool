from fastapi import APIRouter
from app.database import jobs_col, posts_col
from app.redis_client import get_job_status

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.get("/dashboard-stats")
async def get_dashboard_stats():
    """Get overall job statistics for the dashboard."""
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    stats = {"pending": 0, "running": 0, "completed": 0, "failed": 0}
    async for doc in jobs_col.aggregate(pipeline):
        if doc["_id"] in stats:
            stats[doc["_id"]] = doc["count"]
    return stats


@router.get("/{job_id}")
async def get_job(job_id: str):
    """Get a specific job's status."""
    # Check Redis cache first
    cached = await get_job_status(job_id)
    if cached:
        return cached

    # Fallback to MongoDB
    doc = await jobs_col.find_one({"job_id": job_id})
    if doc:
        return {
            "job_id": doc["job_id"],
            "post_id": doc["post_id"],
            "project_id": doc["project_id"],
            "job_type": doc["job_type"],
            "status": doc["status"],
            "error": doc.get("error"),
        }
    return {"error": "Job not found"}


@router.get("/by-post/{post_id}")
async def get_jobs_by_post(post_id: str):
    """Get all jobs for a specific post."""
    jobs = []
    async for doc in jobs_col.find({"post_id": post_id}).sort("created_at", -1):
        jobs.append({
            "job_id": doc["job_id"],
            "post_id": doc["post_id"],
            "job_type": doc["job_type"],
            "status": doc["status"],
            "error": doc.get("error"),
            "created_at": doc["created_at"].isoformat() if doc.get("created_at") else None,
        })
    return jobs
