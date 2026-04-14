# Phase 2: WordPress Integration Backend - Research

**Researched:** 2026-04-14
**Status:** Complete

## Domain Analysis

### WordPress REST API Capabilities

The WordPress REST API (`/wp-json/wp/v2/posts`) provides comprehensive post management capabilities:

**Available Query Parameters:**
- `page` - Page number for pagination
- `per_page` - Posts per page (max 100)
- `status` - Filter by post status (publish, draft, pending, private, future, trash, any)
- `search` - Search by post title/content
- `orderby` - Order by field (date, title, modified, etc.)
- `order` - ASC or DESC
- `_embed` - Include embedded data (author, media, terms, etc.)

**Response Headers:**
- `X-WP-Total` - Total number of posts matching query
- `X-WP-TotalPages` - Total number of pages

### Current Implementation Status

**Existing in `backend/app/services/wp_service.py`:**
- ✅ `get_wp_posts()` - Basic post fetching with pagination and status filtering
- ✅ Authentication via Basic Auth (application passwords)
- ✅ Async HTTP client (httpx)
- ✅ Error handling with `raise_for_status()`

**Missing Functionality:**
- ❌ Search by title parameter (WP-04)
- ❌ Rate limiting handling (WP-05)
- ❌ Post origin tracking (DATA-02)
- ❌ Orphaned post record handling (DATA-03)
- ❌ Duplicate post prevention (DATA-04)
- ❌ Caching layer (PERF-04 - optional for MVP)

## Technical Approach

### 1. Enhanced Post Fetching (WP-01, WP-02, WP-03, WP-04)

**Extend `get_wp_posts()` function:**

```python
async def get_wp_posts(
    project_id: str,
    per_page: int = 100,
    page: int = 1,
    status: str = None,
    search: str = None,
    orderby: str = "date",
    order: str = "desc"
) -> dict:
    """Fetch posts from WordPress REST API with filtering and search.

    Args:
        project_id: Project ID to get WordPress site configuration
        per_page: Number of posts per page (default: 100, max 100)
        page: Page number (default: 1)
        status: Filter by post status (e.g., 'publish', 'draft', 'any')
        search: Search by post title/content
        orderby: Order by field (date, title, modified, etc.)
        order: ASC or DESC

    Returns:
        dict with 'posts' list and 'total' count
    """
    # Implementation with all parameters
```

**WordPress REST API endpoint:**
```
GET /wp-json/wp/v2/posts?page=1&per_page=100&status=publish&search=keyword&orderby=date&order=desc
```

### 2. Rate Limiting (WP-05)

**WordPress REST API Rate Limits:**
- No built-in rate limiting in WordPress core
- Depends on hosting provider and plugins
- Common limits: 100-1000 requests/hour
- HTTP 429 (Too Many Requests) response when exceeded

**Implementation Strategy:**

```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    """Simple rate limiter for WordPress API calls."""

    def __init__(self, max_calls: int = 100, period: int = 3600):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    async def acquire(self):
        """Wait if rate limit exceeded."""
        now = datetime.now()
        # Remove calls older than period
        self.calls = [c for c in self.calls if c > now - timedelta(seconds=self.period)]

        if len(self.calls) >= self.max_calls:
            wait_time = (self.calls[0] + timedelta(seconds=self.period)) - now
            await asyncio.sleep(wait_time.total_seconds())

        self.calls.append(now)
```

**Alternative: Exponential Backoff**
```python
async def fetch_with_retry(url, headers, params, max_retries=3):
    """Fetch with exponential backoff on rate limit errors."""
    for attempt in range(max_retries):
        try:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code == 429:
                wait_time = 2 ** attempt  # 1, 2, 4 seconds
                await asyncio.sleep(wait_time)
                continue
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                continue
            raise
```

**Recommendation:** Use exponential backoff for MVP (simpler, no state management). Rate limiter can be added later if needed.

### 3. Post Origin Tracking (DATA-02)

**Database Schema Changes:**

Add `origin` field to Post model:
```python
class PostResponse(BaseModel):
    # ... existing fields ...
    origin: str = "tool"  # "tool" or "wordpress"
    wp_post_id: Optional[int] = None
    wp_post_url: Optional[str] = None
```

**Migration Strategy:**
- Existing posts: Set `origin = "tool"` (default)
- New posts from WordPress: Set `origin = "wordpress"`
- No migration script needed for MVP (field has default value)

**Implementation:**
```python
async def sync_wordpress_posts(project_id: str):
    """Sync posts from WordPress to local database."""
    wp_posts = await get_wp_posts(project_id, per_page=100, status="any")

    for wp_post in wp_posts["posts"]:
        # Check if post already exists
        existing = await posts_col.find_one({
            "wp_post_id": wp_post["id"],
            "project_id": ObjectId(project_id)
        })

        if not existing:
            # Create new post record with origin="wordpress"
            await posts_col.insert_one({
                "project_id": ObjectId(project_id),
                "wp_post_id": wp_post["id"],
                "wp_post_url": wp_post["link"],
                "title": wp_post["title"]["rendered"],
                "origin": "wordpress",
                "status": wp_post["status"],
                "created_at": datetime.now(),
                # ... other fields
            })
```

### 4. Orphaned Post Record Handling (DATA-03)

**Definition:** Orphaned post = local record exists but WordPress post was deleted

**Detection Strategy:**
```python
async def detect_orphaned_posts(project_id: str):
    """Find posts that exist locally but not in WordPress."""
    # Get all local posts with wp_post_id
    local_posts = await posts_col.find({
        "project_id": ObjectId(project_id),
        "wp_post_id": {"$ne": None}
    }).to_list(None)

    # Get all WordPress posts
    wp_posts = await get_wp_posts(project_id, per_page=100, status="any")
    wp_post_ids = {p["id"] for p in wp_posts["posts"]}

    # Find orphans
    orphans = [p for p in local_posts if p["wp_post_id"] not in wp_post_ids]

    return orphans
```

**Handling Strategy:**
- Mark orphans with `wp_post_deleted = True` flag
- Display warning in UI
- Allow user to delete orphaned records
- Don't auto-delete (user may want to keep content)

### 5. Duplicate Post Prevention (DATA-04)

**Definition:** Duplicate = same WordPress post synced multiple times

**Prevention Strategy:**
```python
async def sync_wordpress_posts(project_id: str):
    """Sync posts from WordPress to local database."""
    wp_posts = await get_wp_posts(project_id, per_page=100, status="any")

    for wp_post in wp_posts["posts"]:
        # Check for duplicates by wp_post_id
        existing = await posts_col.find_one({
            "wp_post_id": wp_post["id"],
            "project_id": ObjectId(project_id)
        })

        if existing:
            # Update existing record
            await posts_col.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "title": wp_post["title"]["rendered"],
                    "wp_post_url": wp_post["link"],
                    "status": wp_post["status"],
                    # ... other fields
                }}
            )
        else:
            # Create new record
            await posts_col.insert_one({
                "project_id": ObjectId(project_id),
                "wp_post_id": wp_post["id"],
                "wp_post_url": wp_post["link"],
                "title": wp_post["title"]["rendered"],
                "origin": "wordpress",
                "status": wp_post["status"],
                "created_at": datetime.now(),
                # ... other fields
            })
```

**Unique Index:**
```python
# Add unique index on (project_id, wp_post_id)
await posts_col.create_index(
    [("project_id", 1), ("wp_post_id", 1)],
    unique=True,
    partialFilterExpression={"wp_post_id": {"$ne": None}}
)
```

### 6. Caching (PERF-04 - Optional for MVP)

**Redis-based Caching:**
```python
import json
from app.redis_client import redis_client

async def get_wp_posts_cached(project_id: str, **kwargs):
    """Fetch posts with Redis caching."""
    cache_key = f"wp_posts:{project_id}:{hash(str(kwargs))}"

    # Try cache first
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Fetch from WordPress
    result = await get_wp_posts(project_id, **kwargs)

    # Cache for 5 minutes
    await redis_client.setex(cache_key, 300, json.dumps(result))

    return result
```

**Cache Invalidation:**
- Invalidate on post publish/update
- TTL-based expiration (5 minutes)
- Manual cache clear option

**Recommendation:** Skip for MVP (PERF-04 is optional). Add in v2 if performance issues arise.

## Architecture Patterns

### Service Layer Pattern

**Current Structure:**
```
backend/app/services/
├── wp_service.py (WordPress API client)
├── ai_service.py (AI provider abstraction)
└── redis_client.py (Redis pub/sub)
```

**Proposed Addition:**
```
backend/app/services/
├── wp_service.py (enhanced with search, rate limiting)
├── post_sync_service.py (sync WordPress posts to local DB)
└── cache_service.py (optional, for v2)
```

### API Layer Pattern

**Router Structure:**
```
backend/app/routers/
├── posts.py (existing)
└── wordpress.py (new - WordPress sync endpoints)
```

**Proposed Endpoints:**
- `GET /api/projects/{project_id}/wordpress/posts` - Fetch WordPress posts
- `POST /api/projects/{project_id}/wordpress/sync` - Sync WordPress posts to local DB
- `GET /api/projects/{project_id}/wordpress/orphans` - Detect orphaned posts

## Dependencies

### External Dependencies
- `httpx` >=0.28.1 - Already present, used for WordPress API calls
- `redis` 5.0.0 - Already present, used for pub/sub (can reuse for caching)

### Internal Dependencies
- `backend/app/services/wp_service.py` - WordPress API client
- `backend/app/database.py` - MongoDB collections
- `backend/app/models/post.py` - Post model (needs `origin` field)

## Common Pitfalls

### 1. Rate Limiting
- **Pitfall:** Not handling 429 responses causes sync failures
- **Solution:** Implement exponential backoff with retry logic

### 2. Pagination
- **Pitfall:** Only fetching first page misses posts
- **Solution:** Loop through all pages until no more results

### 3. Large Post Lists
- **Pitfall:** Fetching all posts at once causes timeout
- **Solution:** Use pagination, fetch in batches of 100

### 4. Orphan Detection
- **Pitfall:** Comparing all posts is slow for large sites
- **Solution:** Use MongoDB aggregation for efficient comparison

### 5. Duplicate Prevention
- **Pitfall:** Race conditions create duplicates
- **Solution:** Use unique index on (project_id, wp_post_id)

## Performance Considerations

### Database Indexes
```python
# Existing indexes (from database.py)
await posts_col.create_index([("project_id", 1)])
await posts_col.create_index([("token_usage.research", 1)])
await posts_col.create_index([("token_usage.outline", 1)])
await posts_col.create_index([("token_usage.content", 1)])
await posts_col.create_index([("token_usage.thumbnail", 1)])

# New indexes for Phase 2
await posts_col.create_index([("wp_post_id", 1)])
await posts_col.create_index([("origin", 1)])
await posts_col.create_index([("project_id", 1), ("wp_post_id", 1)], unique=True)
```

### Query Optimization
- Use `find_one()` for single post lookups
- Use `find()` with projection for list queries
- Use aggregation for complex queries (orphan detection)

### API Response Time
- Target: <2 seconds for <200 posts (PERF-02)
- Strategy: Pagination + caching (optional)

## Security Considerations

### WordPress API Credentials
- Already stored securely in database (wp_sites collection)
- Application passwords are scoped to specific user
- No additional security measures needed for MVP

### Data Validation
- Validate all WordPress API responses before storing
- Sanitize post titles/content from WordPress
- Handle malformed API responses gracefully

## Testing Strategy

### Unit Tests
- Test `get_wp_posts()` with various parameters
- Test rate limiting backoff logic
- Test orphan detection logic
- Test duplicate prevention logic

### Integration Tests
- Test with real WordPress site (test environment)
- Test pagination with large post lists
- Test rate limiting with throttled API

### Manual Testing
- Test sync with WordPress site containing 200+ posts
- Test search functionality with various queries
- Test rate limiting by making rapid requests

## Implementation Order

1. **Enhance `get_wp_posts()`** - Add search, orderby, order parameters
2. **Add `origin` field to Post model** - Database schema change
3. **Create `post_sync_service.py`** - Sync WordPress posts to local DB
4. **Add unique index** - Prevent duplicates
5. **Implement rate limiting** - Exponential backoff
6. **Create API endpoints** - Expose sync functionality
7. **Add orphan detection** - Find deleted WordPress posts
8. **Add caching (optional)** - Redis-based caching for v2

## Open Questions

1. **Rate Limiting Strategy:** Should we use exponential backoff or a rate limiter class?
   - **Recommendation:** Exponential backoff for MVP (simpler)

2. **Sync Frequency:** How often should we sync WordPress posts?
   - **Recommendation:** Manual sync for MVP (user-triggered)

3. **Orphan Handling:** Should we auto-delete orphans or mark them?
   - **Recommendation:** Mark with flag, let user decide

4. **Caching:** Should we implement caching for MVP?
   - **Recommendation:** No, defer to v2 (PERF-04 is optional)

## Next Steps

1. Update `PostResponse` model to include `origin` field
2. Enhance `get_wp_posts()` with search and sorting parameters
3. Create `post_sync_service.py` for sync logic
4. Add database indexes for performance
5. Implement rate limiting with exponential backoff
6. Create API endpoints for WordPress sync
7. Add orphan detection endpoint
8. Test with real WordPress site

---

*Phase: 02-wordpress-integration-backend*
*Research completed: 2026-04-14*
