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
