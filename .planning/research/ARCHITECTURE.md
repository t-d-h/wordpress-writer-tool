# Architecture Patterns

**Domain:** WordPress content management features (token usage display, All Posts tab)
**Researched:** 2026-04-14
**Overall confidence:** HIGH

## Executive Summary

The WordPress Writer Tool's existing architecture provides a solid foundation for both token usage aggregation and WordPress post listing features. The system already implements MongoDB aggregation patterns for statistics and has a working WordPress REST API integration layer. Token usage tracking is embedded in post documents with per-type fields (research, outline, content, thumbnail) and a calculated total. WordPress post listing is partially implemented via an existing endpoint and frontend component. Both features can be built using established patterns in the codebase without requiring architectural changes.

## Key Findings

**Stack:** Python/FastAPI backend with MongoDB aggregation, React frontend with existing API client patterns
**Architecture:** Layered architecture with clear separation: Routers → Services → Database (backend), Components → API Client → Backend (frontend)
**Critical pattern:** MongoDB aggregation pipeline for on-demand calculations, WordPress REST API service layer for external integration

## Recommended Architecture

### Token Usage Aggregation

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                            │
├─────────────────────────────────────────────────────────────┤
│  ProjectDetail.jsx (General Tab)                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ TokenUsageDisplay Component                              │ │
│  │ - Breakdown by type (research, outline, content, thumb)  │ │
│  │ - Total input/output tokens                              │ │
│  │ - Calculated on-the-fly                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Client Layer                          │
├─────────────────────────────────────────────────────────────┤
│  client.js                                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ getProjectTokenUsage(projectId)                          │ │
│  │   → GET /api/projects/{id}/token-usage                   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend Router Layer                     │
├─────────────────────────────────────────────────────────────┤
│  projects.py                                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ @router.get("/{project_id}/token-usage")                 │ │
│  │   - Validates project exists                             │ │
│  │   - Calls aggregation service                           │ │
│  │   - Returns TokenUsageResponse                           │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend Service Layer                    │
├─────────────────────────────────────────────────────────────┤
│  token_usage_service.py (NEW)                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ async def aggregate_project_tokens(project_id)           │ │
│  │   - MongoDB aggregation pipeline                         │ │
│  │   - Groups by project_id                                 │ │
│  │   - Sums token_usage fields                              │ │
│  │   - Includes deleted posts                               │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Database Layer                           │
├─────────────────────────────────────────────────────────────┤
│  MongoDB posts collection                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Document structure:                                      │ │
│  │ {                                                        │ │
│  │   project_id: ObjectId,                                  │ │
│  │   token_usage: {                                        │ │
│  │     research: int,                                       │ │
│  │     outline: int,                                        │ │
│  │     content: int,                                        │ │
│  │     thumbnail: int,                                      │ │
│  │     total: int                                           │ │
│  │   }                                                      │ │
│  │ }                                                        │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### All Posts Tab Integration

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                            │
├─────────────────────────────────────────────────────────────┤
│  ProjectDetail.jsx (New "All Posts" Tab)                      │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ AllPostsTab Component                                    │ │
│  │ - Site selector (if multiple sites)                      │ │
│  │ - Status filter (publish, draft, pending, any)          │ │
│  │ - Search by title                                        │ │
│  │ - Sort by date                                           │ │
│  │ - Visual distinction: tool-created vs existing           │ │
│  │ - Edit button → WordPress admin                          │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Client Layer                          │
├─────────────────────────────────────────────────────────────┤
│  client.js                                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ getProjectAllPosts(projectId, params)                   │ │
│  │   → GET /api/projects/{id}/all-posts                     │ │
│  │     ?status={status}&search={query}&page={page}          │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend Router Layer                     │
├─────────────────────────────────────────────────────────────┤
│  projects.py                                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ @router.get("/{project_id}/all-posts")                   │ │
│  │   - Validates project exists                             │ │
│  │   - Fetches tool posts from MongoDB                      │ │
│  │   - Fetches WP posts via wp_service                      │ │
│  │   - Merges and marks origin                              │ │
│  │   - Applies filters/sorting                              │ │
│  │   - Returns paginated response                           │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend Service Layer                    │
├─────────────────────────────────────────────────────────────┤
│  wp_service.py (EXTENDED)                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ async def get_wp_posts(project_id, ...)                  │ │
│  │   - Already exists                                       │ │
│  │   - Supports pagination, status filter                    │ │
│  │   - Returns {posts, total}                               │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  post_merge_service.py (NEW)                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ async def merge_posts(tool_posts, wp_posts)              │ │
│  │   - Matches by wp_post_id                               │ │
│  │   - Marks origin: 'tool' | 'existing' | 'both'          │ │
│  │   - Applies client-side filters/sorting                 │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     External Systems                         │
├─────────────────────────────────────────────────────────────┤
│  WordPress REST API                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ GET /wp-json/wp/v2/posts                                │ │
│  │   ?per_page=100&page=1&status=publish                   │ │
│  │   &search={query}&orderby=date&order=desc               │ │
│  │   &_embed=wp:term (categories, tags)                     │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Boundaries

### Backend Components

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| **projects.py (router)** | HTTP endpoints for project token usage and all posts | token_usage_service.py, post_merge_service.py, posts_col, wp_sites_col |
| **token_usage_service.py (service)** | MongoDB aggregation for token usage statistics | posts_col (MongoDB) |
| **post_merge_service.py (service)** | Merges tool-created and WordPress posts, applies filters | posts_col, wp_service.py |
| **wp_service.py (service)** | WordPress REST API integration | External WordPress API |
| **posts_col (database)** | Stores post documents with token_usage field | token_usage_service.py, post_merge_service.py |

### Frontend Components

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| **ProjectDetail.jsx** | Main project view with tabs | API client, child components |
| **TokenUsageDisplay.jsx** | Displays token usage breakdown | API client (getProjectTokenUsage) |
| **AllPostsTab.jsx** | Displays merged WordPress posts | API client (getProjectAllPosts) |
| **API client (client.js)** | HTTP communication with backend | Backend API endpoints |

### Data Flow

#### Token Usage Aggregation Flow

```
User opens ProjectDetail → General tab
  ↓
TokenUsageDisplay component mounts
  ↓
API client calls GET /api/projects/{id}/token-usage
  ↓
Backend router validates project exists
  ↓
token_usage_service.py executes MongoDB aggregation:
  [
    {"$match": {"project_id": ObjectId(project_id)}},
    {"$group": {
      "_id": "$project_id",
      "research": {"$sum": "$token_usage.research"},
      "outline": {"$sum": "$token_usage.outline"},
      "content": {"$sum": "$token_usage.content"},
      "thumbnail": {"$sum": "$token_usage.thumbnail"},
      "total": {"$sum": "$token_usage.total"}
    }}
  ]
  ↓
Aggregation results returned as JSON
  ↓
Frontend displays breakdown by type + total
```

**Key characteristics:**
- On-demand calculation (no caching for MVP)
- Includes all posts (deleted posts not filtered out)
- Single MongoDB aggregation query (efficient)
- No input/output token separation (current model only tracks total per type)

#### All Posts Tab Flow

```
User opens ProjectDetail → All Posts tab
  ↓
AllPostsTab component mounts
  ↓
User selects filters (status, search, sort)
  ↓
API client calls GET /api/projects/{id}/all-posts?status={status}&search={query}
  ↓
Backend router validates project exists
  ↓
post_merge_service.py:
  1. Fetches tool posts from MongoDB (posts_col)
  2. Calls wp_service.get_wp_posts() for WordPress posts
  3. Merges by wp_post_id matching
  4. Marks origin: 'tool' (no wp_post_id), 'existing' (no match), 'both' (match)
  5. Applies client-side filters (status, search, sort)
  ↓
Returns paginated response with merged posts
  ↓
Frontend displays table with visual distinction by origin
  ↓
User clicks "Edit" → Opens WordPress admin in new tab
```

**Key characteristics:**
- Two data sources merged (MongoDB + WordPress REST API)
- Origin tracking via wp_post_id presence
- Client-side filtering/sorting (simpler for MVP)
- WordPress API supports pagination, status filter, search
- Edit action opens external WordPress admin (no in-app editing)

## Patterns to Follow

### Pattern 1: MongoDB Aggregation for Statistics

**What:** Use MongoDB aggregation pipeline for on-demand calculations across multiple documents.

**When:** Need to aggregate data from multiple documents (counts, sums, averages).

**Example:**

```python
# In token_usage_service.py
async def aggregate_project_tokens(project_id: str) -> dict:
    pipeline = [
        {"$match": {"project_id": ObjectId(project_id)}},
        {"$group": {
            "_id": "$project_id",
            "research": {"$sum": "$token_usage.research"},
            "outline": {"$sum": "$token_usage.outline"},
            "content": {"$sum": "$token_usage.content"},
            "thumbnail": {"$sum": "$token_usage.thumbnail"},
            "total": {"$sum": "$token_usage.total"}
        }}
    ]
    result = await posts_col.aggregate(pipeline).to_list(length=1)
    if result:
        return {
            "research": result[0].get("research", 0),
            "outline": result[0].get("outline", 0),
            "content": result[0].get("content", 0),
            "thumbnail": result[0].get("thumbnail", 0),
            "total": result[0].get("total", 0)
        }
    return {"research": 0, "outline": 0, "content": 0, "thumbnail": 0, "total": 0}
```

**Why this pattern:**
- Efficient single-query aggregation
- Leverages MongoDB's native aggregation capabilities
- Consistent with existing patterns in projects.py and jobs.py
- No need for pre-computed/cached values for MVP

### Pattern 2: Service Layer for External API Integration

**What:** Isolate external API calls in dedicated service modules.

**When:** Integrating with third-party APIs (WordPress, AI providers).

**Example:**

```python
# In wp_service.py (already exists)
async def get_wp_posts(
    project_id: str,
    per_page: int = 100,
    page: int = 1,
    status: str = None,
    search: str = None
) -> dict:
    """Fetch posts from WordPress REST API."""
    wp_site = await _get_wp_site(project_id)
    headers = _get_auth_header(wp_site["username"], wp_site["api_key"])

    url = f"{wp_site['url'].rstrip('/')}/wp-json/wp/v2/posts"
    params = {
        "per_page": per_page,
        "page": page,
        "_embed": "wp:term"  # Include categories and tags
    }
    if status:
        params["status"] = status
    if search:
        params["search"] = search

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        posts = response.json()
        total = int(response.headers.get("X-WP-Total", len(posts)))
        return {"posts": posts, "total": total}
```

**Why this pattern:**
- Separates external API concerns from business logic
- Centralizes authentication and error handling
- Easy to mock for testing
- Consistent with existing wp_service.py implementation

### Pattern 3: Data Merging with Origin Tracking

**What:** Merge data from multiple sources while tracking origin for display purposes.

**When:** Combining internal data with external API results.

**Example:**

```python
# In post_merge_service.py (NEW)
async def merge_posts(tool_posts: list, wp_posts: list) -> list:
    """Merge tool-created posts with WordPress posts, tracking origin."""
    # Create lookup by wp_post_id for tool posts
    tool_by_wp_id = {p["wp_post_id"]: p for p in tool_posts if p.get("wp_post_id")}

    merged = []
    tool_ids_seen = set()

    # Process WordPress posts
    for wp_post in wp_posts:
        wp_id = wp_post.get("id")
        if wp_id in tool_by_wp_id:
            # Post exists in both systems
            tool_post = tool_by_wp_id[wp_id]
            merged.append({
                **_format_wp_post(wp_post),
                "origin": "both",
                "tool_post_id": str(tool_post["_id"]),
                "wp_post_id": wp_id
            })
            tool_ids_seen.add(str(tool_post["_id"]))
        else:
            # Post only exists in WordPress
            merged.append({
                **_format_wp_post(wp_post),
                "origin": "existing",
                "wp_post_id": wp_id
            })

    # Add tool-only posts (not published to WordPress yet)
    for tool_post in tool_posts:
        if str(tool_post["_id"]) not in tool_ids_seen:
            merged.append({
                **_format_tool_post(tool_post),
                "origin": "tool",
                "tool_post_id": str(tool_post["_id"])
            })

    return merged
```

**Why this pattern:**
- Clear visual distinction in UI
- Enables filtering by origin
- Supports future features (e.g., "Import existing post")
- Maintains data integrity across systems

## Anti-Patterns to Avoid

### Anti-Pattern 1: Pre-computed Token Totals

**What:** Storing aggregated token totals in a separate collection or document.

**Why bad:**
- Adds complexity (need to update on every post change)
- Risk of inconsistency (totals out of sync with individual posts)
- Unnecessary for MVP scale (aggregation is fast enough)

**Instead:** Calculate on-demand using MongoDB aggregation. Add caching later if performance becomes an issue.

### Anti-Pattern 2: Client-Side WordPress API Calls

**What:** Making WordPress REST API calls directly from the frontend.

**Why bad:**
- Exposes WordPress credentials (username, application password)
- CORS issues with WordPress sites
- No centralized error handling or logging
- Bypasses backend validation and business logic

**Instead:** All WordPress API calls go through backend wp_service.py. Frontend only calls backend endpoints.

### Anti-Pattern 3: Separate Endpoints for Tool vs WordPress Posts

**What:** Creating `/api/projects/{id}/tool-posts` and `/api/projects/{id}/wp-posts` endpoints.

**Why bad:**
- Frontend has to make two requests and merge data
- Inconsistent filtering/sorting across sources
- Poor UX (loading states, synchronization issues)
- Duplicates logic in two places

**Instead:** Single `/api/projects/{id}/all-posts` endpoint that merges data server-side.

## Scalability Considerations

| Concern | At 100 users | At 10K users | At 1M users |
|---------|--------------|--------------|-------------|
| Token usage aggregation | On-demand MongoDB aggregation (fast) | Add Redis caching for project stats | Pre-compute with background jobs |
| WordPress post listing | On-demand merge (acceptable) | Cache WordPress posts in MongoDB | Implement incremental sync |
| Post origin tracking | In-memory merge (fast) | Database-backed merge | Dedicated sync service |
| Pagination | Client-side (acceptable) | Server-side pagination | Cursor-based pagination |

**Current approach (MVP):**
- On-demand aggregation for token usage
- On-demand merge for WordPress posts
- Client-side filtering/sorting
- No caching

**When to scale:**
- Add Redis caching for project token usage (TTL: 5-10 minutes)
- Cache WordPress posts in MongoDB with sync jobs
- Move filtering/sorting to backend for large datasets

## Build Order Dependencies

### Phase 1: Token Usage Display (Independent)

**Dependencies:** None (can build in parallel with other features)

**Build order:**
1. Backend models: `TokenUsageResponse` in `backend/app/models/project.py`
2. Backend service: `token_usage_service.py` with aggregation logic
3. Backend router: Add `GET /api/projects/{id}/token-usage` endpoint in `projects.py`
4. Frontend API client: Add `getProjectTokenUsage()` in `client.js`
5. Frontend component: Create `TokenUsageDisplay.jsx` component
6. Frontend integration: Add to `ProjectDetail.jsx` General tab

**Estimated effort:** 2-3 hours

### Phase 2: All Posts Tab (Depends on existing WordPress integration)

**Dependencies:** Existing `wp_service.py` and `get_wp_posts()` function

**Build order:**
1. Backend service: Create `post_merge_service.py` with merge logic
2. Backend router: Add `GET /api/projects/{id}/all-posts` endpoint in `projects.py`
3. Frontend API client: Add `getProjectAllPosts()` in `client.js`
4. Frontend component: Create `AllPostsTab.jsx` component
5. Frontend integration: Add new tab to `ProjectDetail.jsx`
6. Styling: Add visual distinction for post origins

**Estimated effort:** 4-5 hours

### Phase 3: Post Origin Tracking (Database Schema Change)

**Dependencies:** Phase 2 (All Posts tab)

**Build order:**
1. Database migration: Add `origin` field to posts collection (optional, can be computed)
2. Backend service: Update `post_merge_service.py` to persist origin
3. Backend router: Update post creation to set origin
4. Frontend: Update display to use persisted origin

**Estimated effort:** 1-2 hours (optional for MVP)

**Total estimated effort:** 7-10 hours for both features

## Integration Points

### Existing Codebase Integration

**Token Usage Display:**
- Reuses existing `posts_col` aggregation pattern from `projects.py`
- Follows same router structure as `GET /api/projects/{id}/stats`
- Integrates with existing `ProjectDetail.jsx` tab system
- No database schema changes required

**All Posts Tab:**
- Extends existing `wp_service.py` (already has `get_wp_posts()`)
- Reuses existing `AllPosts.jsx` patterns (site selector, status filter)
- Integrates with existing `ProjectDetail.jsx` tab system
- Optional: Add `origin` field to posts collection (can be computed on-the-fly)

### External System Integration

**WordPress REST API:**
- Already integrated via `wp_service.py`
- Supports pagination, filtering, sorting, search
- Returns total count in `X-WP-Total` header
- Supports `_embed` for related resources (categories, tags)
- Authentication via Basic Auth (username + application password)

## Data Models

### Token Usage Response Model

```python
# backend/app/models/project.py
class TokenUsageResponse(BaseModel):
    research: int = 0
    outline: int = 0
    content: int = 0
    thumbnail: int = 0
    total: int = 0
```

### All Posts Response Model

```python
# backend/app/models/project.py
class PostOrigin(str, Enum):
    TOOL = "tool"           # Created by tool, not published
    EXISTING = "existing"   # Existed in WordPress before
    BOTH = "both"           # Created by tool and published

class MergedPost(BaseModel):
    id: int  # WordPress post ID
    title: str
    link: str
    status: str
    date: str
    origin: PostOrigin
    tool_post_id: Optional[str] = None  # MongoDB post ID if origin is 'tool' or 'both'
    categories: List[dict] = []
    tags: List[dict] = []

class AllPostsResponse(BaseModel):
    posts: List[MergedPost]
    total: int
    page: int
    per_page: int
```

## Error Handling

### Token Usage Aggregation

**Error scenarios:**
- Project not found: Return 404 with detail
- No posts in project: Return zeros for all fields
- Aggregation failure: Return 500 with error message

**Example:**

```python
@router.get("/{project_id}/token-usage")
async def get_project_token_usage(project_id: str):
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        usage = await aggregate_project_tokens(project_id)
        return usage
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to aggregate token usage: {str(e)}")
```

### All Posts Tab

**Error scenarios:**
- Project not found: Return 404 with detail
- WordPress site not configured: Return 400 with detail
- WordPress API error: Return 502 with error message
- Merge failure: Return 500 with error message

**Example:**

```python
@router.get("/{project_id}/all-posts")
async def get_project_all_posts(project_id: str, status: str = None, search: str = None, page: int = 1):
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # Fetch tool posts
        tool_posts = await posts_col.find({"project_id": project_id}).to_list(length=None)

        # Fetch WordPress posts
        wp_result = await get_wp_posts(project_id, per_page=100, page=page, status=status, search=search)

        # Merge
        merged = await merge_posts(tool_posts, wp_result["posts"])

        return {
            "posts": merged,
            "total": len(merged),
            "page": page,
            "per_page": 100
        }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"WordPress API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posts: {str(e)}")
```

## Performance Considerations

### Token Usage Aggregation

**Current approach:** On-demand MongoDB aggregation

**Performance characteristics:**
- Single aggregation query (efficient)
- O(n) where n = number of posts in project
- For 100 posts: <10ms
- For 10,000 posts: ~100ms
- For 100,000 posts: ~1s (may need caching)

**Optimization opportunities:**
- Add Redis caching with 5-10 minute TTL
- Pre-compute on post creation/update (eventual consistency)
- Use MongoDB indexes on `project_id` field

### All Posts Tab

**Current approach:** On-demand merge of MongoDB + WordPress API

**Performance characteristics:**
- Two data sources (MongoDB + WordPress REST API)
- WordPress API latency: 100-500ms (depends on site)
- Merge operation: O(n+m) where n = tool posts, m = WordPress posts
- For 100 posts total: ~600ms
- For 1,000 posts total: ~1-2s

**Optimization opportunities:**
- Cache WordPress posts in MongoDB with background sync
- Use WordPress `_fields` parameter to reduce payload size
- Implement server-side pagination (not client-side)
- Add loading states and progressive rendering

## Security Considerations

### Token Usage Display

**Security concerns:**
- None significant (read-only aggregation of existing data)
- No sensitive data exposed

**Recommendations:**
- No additional security measures needed for MVP

### All Posts Tab

**Security concerns:**
- WordPress credentials stored in database (already existing)
- WordPress API calls expose credentials in Basic Auth header
- Potential for credential leakage if logs are exposed

**Recommendations:**
- Ensure credentials are never logged (already implemented in wp_service.py)
- Use HTTPS for all WordPress API calls (already required by WordPress)
- Consider credential rotation mechanism for production
- Add rate limiting for WordPress API calls (prevent abuse)

## Testing Strategy

### Token Usage Aggregation

**Unit tests:**
- Test aggregation with empty project (returns zeros)
- Test aggregation with single post (returns post's token usage)
- Test aggregation with multiple posts (sums correctly)
- Test aggregation with deleted posts (includes in total)

**Integration tests:**
- Test endpoint returns correct response format
- Test endpoint returns 404 for non-existent project
- Test endpoint handles aggregation errors gracefully

### All Posts Tab

**Unit tests:**
- Test merge with only tool posts (all marked 'tool')
- Test merge with only WordPress posts (all marked 'existing')
- Test merge with matching posts (marked 'both')
- Test merge with no matches (correct separation)

**Integration tests:**
- Test endpoint returns correct response format
- Test endpoint returns 404 for non-existent project
- Test endpoint handles WordPress API errors gracefully
- Test filtering by status works correctly
- Test search by title works correctly

## Sources

- WordPress REST API documentation: https://developer.wordpress.org/rest-api/reference/posts/ (HIGH confidence)
- WordPress REST API global parameters: https://developer.wordpress.org/rest-api/using-the-rest-api/global-parameters/ (HIGH confidence)
- MongoDB aggregation documentation: https://www.mongodb.com/docs/manual/core/aggregation-pipeline/ (HIGH confidence)
- Existing codebase analysis: backend/app/routers/projects.py, backend/app/routers/jobs.py, backend/app/services/wp_service.py, frontend/src/components/ProjectDetail.jsx (HIGH confidence)
- FastAPI documentation: https://fastapi.tiangolo.com/ (HIGH confidence)
