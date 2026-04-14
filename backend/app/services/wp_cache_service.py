"""
WordPress Cache Service — cache WordPress posts in MongoDB with TTL-based expiration.
"""

import asyncio
from datetime import datetime, timezone
from app.database import wp_posts_cache_col
from app.services.wp_service import get_wp_posts


class WPCacheService:
    """Service for caching WordPress posts with automatic expiration and staleness detection."""

    def __init__(self):
        """Initialize cache service with MongoDB collection reference."""
        self.collection = wp_posts_cache_col

    def get_cache_key(
        self,
        project_id: str,
        per_page: int,
        page: int,
        status: str,
        orderby: str,
        order: str,
    ) -> str:
        """Generate unique cache key for a specific query.

        Args:
            project_id: Project ID
            per_page: Posts per page
            page: Page number
            status: Post status filter
            orderby: Order by field
            order: Order direction

        Returns:
            str: Unique cache key
        """
        return f"wp_posts:{project_id}:{per_page}:{page}:{status}:{orderby}:{order}"

    async def get_cached_posts(self, cache_key: str) -> dict:
        """Retrieve cached posts from MongoDB.

        Args:
            cache_key: Unique cache key

        Returns:
            dict: Cached data with 'posts', 'total', 'cached_at' or None if not found
        """
        cached = await self.collection.find_one({"_id": cache_key})
        if cached:
            return {
                "posts": cached.get("posts", []),
                "total": cached.get("total", 0),
                "cached_at": cached.get("cached_at"),
            }
        return None

    async def cache_posts(self, cache_key: str, posts: list, total: int) -> None:
        """Store posts in cache with TTL.

        Args:
            cache_key: Unique cache key
            posts: List of posts to cache
            total: Total number of posts
        """
        cache_doc = {
            "_id": cache_key,
            "posts": posts,
            "total": total,
            "cached_at": datetime.now(timezone.utc),
            "ttl": 10800,  # 3 hours in seconds
        }
        await self.collection.replace_one({"_id": cache_key}, cache_doc, upsert=True)
        print(f"[CACHE] Cached {len(posts)} posts with key {cache_key}")

    async def is_cache_stale(self, cache_key: str, project_id: str) -> bool:
        """Detect staleness by comparing with WordPress API.

        Args:
            cache_key: Unique cache key
            project_id: Project ID

        Returns:
            bool: True if cache is stale, False if fresh
        """
        cached = await self.collection.find_one({"_id": cache_key})
        if not cached:
            return True

        # Fetch single post from WordPress API to check if data has changed
        try:
            wp_data = await get_wp_posts(project_id, per_page=1, page=1, status=None)
            wp_total = wp_data.get("total", 0)
            cached_total = cached.get("total", 0)

            if wp_total != cached_total:
                print(f"[CACHE] Stale detected: cached={cached_total}, wp={wp_total}")
                return True

            return False
        except Exception as e:
            print(f"[CACHE] Error checking staleness: {str(e)}")
            # If we can't check, assume cache is stale to be safe
            return True

    async def refresh_cache(
        self,
        project_id: str,
        per_page: int,
        page: int,
        status: str,
        orderby: str,
        order: str,
        search: str = None,
    ) -> dict:
        """Refresh cache from WordPress API with progress tracking.

        Args:
            project_id: Project ID
            per_page: Posts per page
            page: Page number
            status: Post status filter
            orderby: Order by field
            order: Order direction
            search: Search query (optional)

        Returns:
            dict: Progress information with status, posts_refreshed, total_posts, message
        """
        cache_key = self.get_cache_key(
            project_id, per_page, page, status, orderby, order
        )

        try:
            # Fetch posts from WordPress API with retry logic
            wp_data = await get_wp_posts(
                project_id, per_page, page, status, search, orderby, order
            )
            posts = wp_data.get("posts", [])
            total = wp_data.get("total", 0)

            # Store in cache
            await self.cache_posts(cache_key, posts, total)

            return {
                "status": "success",
                "posts_refreshed": len(posts),
                "total_posts": total,
                "message": f"Successfully refreshed {len(posts)} posts",
            }
        except Exception as e:
            print(f"[CACHE] Error refreshing cache: {str(e)}")
            return {
                "status": "failed",
                "posts_refreshed": 0,
                "total_posts": 0,
                "message": f"Failed to refresh cache: {str(e)}",
            }


# Global cache service instance
_wp_cache_service = None


def get_wp_cache_service() -> WPCacheService:
    """Get or create the global cache service instance.

    Returns:
        WPCacheService: Global cache service instance
    """
    global _wp_cache_service
    if _wp_cache_service is None:
        _wp_cache_service = WPCacheService()
    return _wp_cache_service
