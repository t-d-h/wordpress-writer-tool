"""Worker entry point - imports and runs redis_worker"""

from app.workers.redis_worker import main

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
