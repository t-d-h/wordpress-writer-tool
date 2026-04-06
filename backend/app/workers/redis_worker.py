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
from app.workers.tasks import (
    run_research,
    run_outline,
    run_content,
    run_thumbnail,
    run_section_images,
    run_publish,
)

TASK_MAP = {
    "research": run_research,
    "outline": run_outline,
    "content": run_content,
    "thumbnail": run_thumbnail,
    "section_images": run_section_images,
    "publish": run_publish,
}

running = True


async def process_job(job_data: dict):
    """Route a job to the appropriate task handler."""
    job_type = job_data.get("job_type")
    handler = TASK_MAP.get(job_type)

    if not handler:
        print(f"[WORKER] Unknown job type: {job_type}")
        return

    print(f"[WORKER] Processing {job_type} job: {job_data.get('job_id')}")
    try:
        await handler(job_data)
    except Exception as e:
        print(f"[WORKER] Error processing job {job_data.get('job_id')}: {e}")


async def main():
    global running
    print("[WORKER] Starting Redis worker...")
    print(f"[WORKER] Connecting to Redis at {settings.REDIS_URL}")

    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe("wp_writer:jobs")

    print("[WORKER] Subscribed to wp_writer:jobs channel. Waiting for jobs...")

    while running:
        try:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                try:
                    job_data = json.loads(message["data"])
                    # Run job in a separate task so we can process multiple jobs concurrently
                    asyncio.create_task(process_job(job_data))
                except json.JSONDecodeError:
                    print(f"[WORKER] Invalid JSON received: {message['data']}")
            else:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[WORKER] Error: {e}")
            await asyncio.sleep(1)

    await pubsub.unsubscribe("wp_writer:jobs")
    await redis.close()
    print("[WORKER] Worker stopped.")


def handle_shutdown(signum, frame):
    global running
    print(f"\n[WORKER] Received signal {signum}, shutting down...")
    running = False


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    asyncio.run(main())
