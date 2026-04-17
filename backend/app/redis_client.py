import json
import redis.asyncio as aioredis
from app.config import settings

redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

# Queue and channel names
JOB_QUEUE = "wp_writer:job_queue"
JOB_STATUS_CHANNEL = "wp_writer:job_status"


async def publish_job(job_data: dict):
    """Push a job to the Redis job queue (list-based for single-consumer delivery)."""
    await redis_client.lpush(JOB_QUEUE, json.dumps(job_data))


async def set_job_status(job_id: str, status: dict):
    """Store job status in Redis for quick access."""
    await redis_client.set(f"job:{job_id}", json.dumps(status), ex=86400)


async def get_job_status(job_id: str) -> dict | None:
    """Get job status from Redis."""
    data = await redis_client.get(f"job:{job_id}")
    if data:
        return json.loads(data)
    return None
