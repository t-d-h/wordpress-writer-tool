"""
Redis Worker — listens for jobs on Redis pub/sub and dispatches them to task handlers.
Run as: python -m app.workers.redis_worker
"""

import asyncio
import json
import signal
import sys
import redis.asyncio as aioredis
from app.config import settings
from app.logging_config import setup_logging
from app.workers.tasks import (
    run_research,
    run_outline,
    run_content,
    run_thumbnail,
    run_publish,
)

logger = setup_logging()

TASK_MAP = {
    "research": run_research,
    "outline": run_outline,
    "content": run_content,
    "thumbnail": run_thumbnail,
    "publish": run_publish,
}

running = True


async def process_job(job_data: dict):
    """Route a job to the appropriate task handler."""
    job_type = job_data.get("job_type")
    handler = TASK_MAP.get(job_type)

    if not handler:
        logger.error(f"Unknown job type: {job_type}")
        return

    job_id = job_data.get("job_id")
    logger.info(f"Received job: {job_type} (ID: {job_id})")
    logger.info(f"Dispatching to handler: {job_type}")
    logger.info(f"Job {job_id} started")
    try:
        await handler(job_data)
        logger.info(f"Job {job_id} completed")
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        logger.exception("Full stack trace:")


async def main():
    global running
    logger.info("Starting Redis worker...")
    logger.info(f"Connecting to Redis at {settings.REDIS_URL}")

    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe("wp_writer:jobs")

    logger.info("Subscribed to wp_writer:jobs channel. Waiting for jobs...")

    while running:
        try:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message["type"] == "message":
                try:
                    job_data = json.loads(message["data"])
                    # Run job in a separate task so we can process multiple jobs concurrently
                    asyncio.create_task(process_job(job_data))
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message['data']}")
            else:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.exception("Full stack trace:")
            await asyncio.sleep(1)

    await pubsub.unsubscribe("wp_writer:jobs")
    await redis.close()
    logger.info("Worker stopped.")


def handle_shutdown(signum, frame):
    global running
    logger.info(f"Received signal {signum}, shutting down...")
    running = False


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    asyncio.run(main())
