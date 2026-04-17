from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB]

# Collections
ai_providers_col = db["ai_providers"]
wp_sites_col = db["wp_sites"]
projects_col = db["projects"]
posts_col = db["posts"]
jobs_col = db["jobs"]
default_models_col = db["default_models"]
wp_posts_cache_col = db["wp_posts_cache"]
link_maps_col = db["link_maps"]


async def create_indexes():
    """Create database indexes for optimized queries."""
    # Index on posts collection for token usage aggregation
    await posts_col.create_index([("project_id", 1)])
    await posts_col.create_index([("token_usage.research", 1)])
    await posts_col.create_index([("token_usage.outline", 1)])
    await posts_col.create_index([("token_usage.content", 1)])
    await posts_col.create_index([("token_usage.thumbnail", 1)])

    # New indexes for Phase 2: WordPress Integration
    await posts_col.create_index([("wp_post_id", 1)])
    await posts_col.create_index([("origin", 1)])
    await posts_col.create_index(
        [("project_id", 1), ("wp_post_id", 1)],
        unique=True,
        partialFilterExpression={"wp_post_id": {"$ne": None}},
    )

    # Index for Phase 4: WordPress post cache with TTL
    await wp_posts_cache_col.create_index([("cached_at", 1)], expireAfterSeconds=10800)

    # Index for link maps
    await link_maps_col.create_index([("project_id", 1)])
