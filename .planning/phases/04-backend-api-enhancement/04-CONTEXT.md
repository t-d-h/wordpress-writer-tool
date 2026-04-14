# Phase 4: Backend API Enhancement - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

## Phase Boundary

Backend provides efficient post retrieval with caching, pagination, and search/sort capabilities. Expose search, orderby, and order parameters in get_site_posts endpoint. Support 100 posts per page pagination. Cache WordPress posts in MongoDB or Redis for faster retrieval. Implement cache invalidation when posts are created/updated/deleted. Provide manual cache refresh mechanism.

## Implementation Decisions

### Caching Storage Strategy
- **D-01:** Store cached WordPress posts in MongoDB collection with TTL index for automatic expiration
- **D-02:** Use MongoDB for complex queries and joins with existing data
- **D-03:** Cache TTL set to medium duration (1-6 hours) for balance between freshness and performance

### Cache Refresh Mechanism
- **D-04:** Manual cache refresh only - no automatic invalidation on post operations
- **D-05:** Manual refresh triggered via admin UI button in frontend
- **D-06:** Cache refresh provides feedback with loading spinner during refresh, then success message
- **D-07:** Cache refresh scope is modified posts only - refresh only posts modified since last cache
- **D-08:** Cache staleness detected by comparing with WordPress API (not time-based TTL)

### Search Implementation Approach
- **D-09:** Search always hits WordPress API with search parameter (not cached data)
- **D-10:** Search queries post titles only (not content or excerpt)
- **D-11:** Search is case-insensitive for user-friendly behavior
- **D-12:** Search supports partial matching (e.g., "blog" matches "blogging")
- **D-13:** Search results limited to 100 posts for consistency with pagination

### Pagination Implementation Approach
- **D-14:** Pagination uses hybrid approach - paginate cache first, fall back to WordPress API if cache is stale or missing
- **D-15:** Hybrid pagination falls back to WordPress API if cache is stale or missing (ensures fresh data)
- **D-16:** Cache staleness detected by comparing with WordPress API (not time-based TTL)
- **D-17:** Pagination page size is 100 posts per page
- **D-18:** Pagination controls show Previous/Next buttons + page numbers

### Data Transformation
- **D-19:** Backend returns WordPress REST API data with proper transformation for table format
- **D-20:** Backend exposes search, orderby, and order parameters in get_site_posts endpoint
- **D-21:** Backend supports 100 posts per page pagination

### the agent's Discretion
- **D-22:** Specific MongoDB collection name and schema for cached posts
- **D-23:** Exact TTL value within 1-6 hour range (choose based on performance testing)
- **D-24:** Cache refresh progress granularity (how often to update progress)
- **D-25:** Error handling for cache refresh failures (retry logic, user messaging)
- **D-26:** Cache key format and structure for efficient lookups
- **D-27:** How to track modification timestamps for "modified posts only" refresh scope

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Project vision, core value, requirements
- `.planning/REQUIREMENTS.md` — Detailed requirements with REQ-IDs (BACKEND-01 through BACKEND-06)
- `.planning/ROADMAP.md` — Phase goals and success criteria

### Research Findings
- `.planning/research/STACK.md` — Technology stack recommendations, no new libraries needed
- `.planning/research/FEATURES.md` — Feature landscape for table view
- `.planning/research/ARCHITECTURE.md` — Integration points and data flow
- `.planning/research/PITFALLS.md` — Common mistakes and prevention strategies

### Codebase Patterns
- `backend/app/services/wp_service.py` — WordPress REST API service with existing search/sort parameters
- `backend/app/routers/wp_sites.py` — Current router endpoint for get_site_posts
- `backend/app/database.py` — MongoDB connection and collection access patterns
- `frontend/src/api/client.js` — API client with getSitePosts function
- `frontend/src/components/AllPosts.jsx` — Working table implementation reference

### Prior Phase Context
- `.planning/phases/03-all-posts-tab-ui/03-CONTEXT.md` — All Posts tab UI decisions (infinite scroll, server-side filtering)
- `.planning/phases/01-token-usage-display/01-CONTEXT.md` — Token usage display patterns (MongoDB aggregation)

## Existing Code Insights

### Reusable Assets
- **MongoDB aggregation**: Existing patterns in `backend/app/routers/projects.py` for stats calculation
- **WordPress REST API service**: `backend/app/services/wp_service.py` already supports search, orderby, order parameters
- **Redis client**: `backend/app/redis_client.py` for pub/sub messaging (could be reused for cache invalidation if needed)
- **MongoDB collections**: `posts_col`, `wp_sites_col` for existing data structures

### Established Patterns
- **Service layer**: WordPress API calls isolated in `wp_service.py` with error handling
- **Rate limiting**: Exponential backoff pattern in `wp_service.py` for WordPress API calls
- **Data transformation**: WordPress REST API response transformation in existing endpoints
- **Pagination**: WordPress REST API pagination with per_page and page parameters
- **Error handling**: Try/catch with HTTPException for backend, alert() for frontend

### Integration Points
- **Backend**: Extend `backend/app/routers/wp_sites.py` get_site_posts endpoint with search, orderby, order parameters
- **Backend**: Create new cache service or extend `wp_service.py` for caching logic
- **Backend**: Add cache refresh endpoint for manual refresh
- **Frontend**: Update `frontend/src/api/client.js` getSitePosts function to pass new parameters
- **Frontend**: Add admin UI button for cache refresh in appropriate component
- **Database**: Create new MongoDB collection for cached posts or use existing `posts_col`

## Specific Ideas

No specific requirements — open to standard approaches that match existing codebase patterns.

## Deferred Ideas

None — discussion stayed within phase scope

---

*Phase: 04-backend-api-enhancement*
*Context gathered: 2026-04-14*
