# Phase 4: Backend API Enhancement - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-14
**Phase:** 04-backend-api-enhancement
**Areas discussed:** Caching storage strategy, Cache refresh mechanism, Search implementation approach, Pagination implementation approach

---

## Caching storage strategy

| Option | Description | Selected |
|--------|-------------|----------|
| MongoDB | Store cached posts in MongoDB collection with TTL index for automatic expiration. Good for complex queries and joins with existing data. | ✓ |
| Redis | Store cached posts in Redis with TTL for fast in-memory access. Better for simple key-value lookups and high throughput. | |
| Hybrid | Hybrid approach - use Redis for hot data (recent posts) and MongoDB for full cache. More complex but leverages both strengths. | |

**User's choice:** MongoDB
**Notes:** User chose MongoDB for caching storage, preferring it for complex queries and joins with existing data.

---

## Cache refresh mechanism

### Refresh trigger

| Option | Description | Selected |
|--------|-------------|----------|
| API endpoint | REST API endpoint that triggers cache refresh. Simple, can be called by admin or automated system. | |
| Admin UI button | Admin UI button in frontend that calls refresh endpoint. User-friendly, visible in admin interface. | ✓ |
| Both API and UI | Both API endpoint and admin UI button. API for automation, UI for manual use. Most flexible. | |

**User's choice:** Admin UI button
**Notes:** User chose admin UI button for manual cache refresh trigger.

### Cache TTL

| Option | Description | Selected |
|--------|-------------|----------|
| Short TTL (5-15 min) | Short TTL (5-15 minutes). Cache expires quickly, always relatively fresh. More frequent refreshes needed. | |
| Medium TTL (1-6 hours) | Medium TTL (1-6 hours). Good balance between freshness and performance. Reasonable refresh frequency. | ✓ |
| Long TTL (24+ hours) | Long TTL (24+ hours). Cache stays fresh for a day. Manual refresh needed for updates. Less frequent refreshes. | |

**User's choice:** Medium TTL (1-6 hours)
**Notes:** User chose medium TTL for balance between freshness and performance.

### Refresh feedback

| Option | Description | Selected |
|--------|-------------|----------|
| Loading + success message | Show loading spinner during refresh, then success message. Simple and clear user feedback. | ✓ |
| Progress bar | Show progress bar with percentage during refresh. More detailed feedback for long refreshes. | |
| Toast notification | Show toast notification when refresh completes. Non-blocking, allows user to continue working. | |

**User's choice:** Loading + success message
**Notes:** User chose loading spinner with success message for cache refresh feedback.

### Refresh scope

| Option | Description | Selected |
|--------|-------------|----------|
| All posts | Refresh all posts for the site. Simple, but may be slow for sites with many posts. | |
| Modified posts only | Refresh only posts modified since last cache. More efficient, but requires tracking modification timestamps. | ✓ |
| All posts in batches | Refresh all posts, but in batches with progress updates. Balances simplicity and performance. | |

**User's choice:** Modified posts only
**Notes:** User chose to refresh only modified posts for efficiency.

---

## Search implementation approach

### Search fields

| Option | Description | Selected |
|--------|-------------|----------|
| Title only | Search post titles only. Simpler, faster, but may miss relevant content in post body. | ✓ |
| Title and content | Search both post titles and content. More comprehensive, but slower and may return more results. | |
| Title, content, and excerpt | Search titles, content, and excerpt. Most comprehensive, but slowest and may return many results. | |

**User's choice:** Title only
**Notes:** User chose to search post titles only for simplicity and speed.

### Case sensitivity

| Option | Description | Selected |
|--------|-------------|----------|
| Case-insensitive | Case-insensitive search. User-friendly, matches regardless of capitalization. Standard behavior. | ✓ |
| Case-sensitive | Case-sensitive search. More precise, but may miss results due to capitalization differences. | |
| User choice | User choice - let user toggle case sensitivity. Most flexible, but adds UI complexity. | |

**User's choice:** Case-insensitive
**Notes:** User chose case-insensitive search for user-friendly behavior.

### Partial matching

| Option | Description | Selected |
|--------|-------------|----------|
| Partial match | Partial matching - search for "blog" matches "blogging". More flexible, returns more results. | ✓ |
| Exact word match | Exact word matching - search for "blog" only matches "blog". More precise, fewer results. | |
| User choice | User choice - let user toggle partial matching. Most flexible, but adds UI complexity. | |

**User's choice:** Partial match
**Notes:** User chose partial matching for more flexible search results.

### Search results limit

| Option | Description | Selected |
|--------|-------------|----------|
| Limit to 100 posts | Limit search results to 100 posts. Consistent with pagination, prevents overwhelming results. | ✓ |
| Limit to 500 posts | Limit search results to 500 posts. More results, but may be overwhelming. | |
| No limit | No limit - return all matching posts. Most comprehensive, but may be slow for large result sets. | |

**User's choice:** Limit to 100 posts
**Notes:** User chose to limit search results to 100 posts for consistency with pagination.

---

## Pagination implementation approach

### Fallback strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Fallback to WordPress API | Fall back to WordPress API if cache is stale or missing. Ensures fresh data, but may be slower. | ✓ |
| Fallback only if missing | Fall back to WordPress API only if cache is missing. If cache exists but stale, show stale data with warning. | |
| No fallback | No fallback - always use cache. If cache is stale, show error message. Forces user to refresh cache. | |

**User's choice:** Fallback to WordPress API
**Notes:** User chose to fall back to WordPress API if cache is stale or missing to ensure fresh data.

### Staleness detection

| Option | Description | Selected |
|--------|-------------|----------|
| Time-based (TTL) | Cache is stale if older than TTL. Simple, time-based staleness detection. | |
| Compare with WordPress API | Cache is stale if WordPress API reports newer posts. More accurate, but requires additional API call. | ✓ |
| Both TTL and comparison | Cache is stale if older than TTL OR WordPress API reports newer posts. Most comprehensive, but more complex. | |

**User's choice:** Compare with WordPress API
**Notes:** User chose to detect staleness by comparing with WordPress API for accuracy.

### Page size

| Option | Description | Selected |
|--------|-------------|----------|
| 50 posts per page | 50 posts per page. Smaller pages, faster load, more page turns. | |
| 100 posts per page | 100 posts per page. Balanced size, reasonable load time, fewer page turns. | ✓ |
| 200 posts per page | 200 posts per page. Larger pages, slower load, fewer page turns. | |

**User's choice:** 100 posts per page
**Notes:** User chose 100 posts per page for balanced size and load time.

### Navigation controls

| Option | Description | Selected |
|--------|-------------|----------|
| Previous/Next only | Previous/Next buttons only. Simple, minimal UI. | |
| Previous/Next + page numbers | Previous/Next buttons + page numbers. More navigation options, shows total pages. | ✓ |
| Full navigation | Previous/Next buttons + page numbers + jump to page. Most comprehensive, but more complex UI. | |

**User's choice:** Previous/Next + page numbers
**Notes:** User chose Previous/Next buttons with page numbers for navigation.

---

## the agent's Discretion

Areas where user deferred to the agent:
- Specific MongoDB collection name and schema for cached posts
- Exact TTL value within 1-6 hour range
- Cache refresh progress granularity
- Error handling for cache refresh failures
- Cache key format and structure
- How to track modification timestamps for "modified posts only" refresh scope

## Deferred Ideas

None — discussion stayed within phase scope
