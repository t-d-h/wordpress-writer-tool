# Phase 5: Data Transformation - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

## Phase Boundary

WordPress REST API responses are transformed into table-ready format. Backend service layer transforms WordPress REST API data before sending to frontend, including extracting nested categories/tags, formatting dates, and generating edit URLs.

## Implementation Decisions

### Transformation Location
- **D-01:** Transformation happens in backend service layer (wp_service.py or new transformation service)
- **D-02:** Backend returns properly transformed data for table format (aligns with Phase 4 decision D-19)
- **D-03:** Frontend becomes simpler, just displays what backend sends
- **D-04:** No transformation logic in frontend for this phase (frontend already has transformation logic that will be removed in Phase 7)

### Date Format
- **D-05:** Backend sends formatted date string (not ISO 8601 or Unix timestamp)
- **D-06:** Date format is fixed: DD MMMM YYYY (e.g., "14 April 2026")
- **D-07:** No locale-based formatting (consistent across all users)
- **D-08:** No relative time formatting (simpler implementation)

### Transformation Scope
- **D-09:** Backend transforms nested categories from _embedded['wp:term'][0] into simple array of category names
- **D-10:** Backend transforms nested tags from _embedded['wp:term'][1] into simple array of tag names
- **D-11:** Backend formats dates from WordPress REST API into DD MMMM YYYY format
- **D-12:** Backend generates edit URLs for WordPress admin (constructs full URL)
- **D-13:** Backend returns all required table fields: title, url, categories, tags, date, status, edit_url

### Error Handling
- **D-14:** If _embedded is missing or null, categories and tags return empty array
- **D-15:** If categories or tags array is null, return empty array
- **D-16:** If date is invalid or missing, return empty string or placeholder
- **D-17:** If post ID is missing, edit_url returns empty string
- **D-18:** Graceful degradation - missing fields don't break entire response

### Data Structure
- **D-19:** Transformed response structure matches frontend table expectations
- **D-20:** Categories and tags are arrays of strings (names only), not full objects
- **D-21:** Date is formatted string, not Date object or timestamp
- **D-22:** Edit URL is full URL string ready for use in href attribute

### the agent's Discretion
- **D-23:** Exact implementation location (wp_service.py vs new transformation service)
- **D-24:** Whether to create helper functions or inline transformation
- **D-25:** How to handle edge cases (empty arrays, null values, invalid dates)
- **D-26:** Whether to add logging for transformation steps
- **D-27:** Whether to validate WordPress site URL before generating edit URLs

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Project vision, core value, requirements
- `.planning/REQUIREMENTS.md` — Detailed requirements with REQ-IDs (DATA-01 through DATA-04)
- `.planning/ROADMAP.md` — Phase goals and success criteria

### Research Findings
- `.planning/research/STACK.md` — Technology stack recommendations
- `.planning/research/ARCHITECTURE.md` — Integration points and data flow
- `.planning/research/FEATURES.md` — Feature landscape for table view
- `.planning/research/PITFALLS.md` — Common mistakes and prevention strategies

### Codebase Patterns
- `backend/app/services/wp_service.py` — WordPress REST API service with get_wp_posts function
- `backend/app/routers/wp_sites.py` — Current router endpoint for get_site_posts
- `frontend/src/components/AllPosts.jsx` — Working table implementation with transformation logic (for reference)
- `frontend/src/api/client.js` — API client with getSitePosts function

### Prior Phase Context
- `.planning/phases/04-backend-api-enhancement/04-CONTEXT.md` — Backend API enhancement decisions (caching, search, sort)
- `.planning/phases/03-all-posts-tab-ui/03-CONTEXT.md` — All Posts tab UI decisions (infinite scroll, server-side filtering)
- `.planning/phases/01-token-usage-display/01-CONTEXT.md` — Token usage display patterns (MongoDB aggregation)

## Existing Code Insights

### Reusable Assets
- **WordPress REST API service**: `backend/app/services/wp_service.py` already fetches posts with _embed=True
- **Frontend transformation logic**: AllPosts.jsx has formatDate, getEditUrl, getCategoryNames, getTagNames functions (for reference)
- **Error handling patterns**: Try/catch with HTTPException for backend, alert() for frontend

### Established Patterns
- **Service layer**: WordPress API calls isolated in wp_service.py with error handling
- **Data transformation**: WordPress REST API response transformation in existing endpoints
- **Response format**: Backend returns dict with 'posts' list and 'total' count
- **Error handling**: Try/catch with HTTPException for backend, alert() for frontend

### Integration Points
- **Backend**: Extend wp_service.py get_wp_posts function to transform data before returning
- **Backend**: Or create new transformation service called by wp_service.py
- **Frontend**: Update frontend to use transformed data directly (remove transformation logic in Phase 7)
- **API**: get_site_posts endpoint returns transformed data from service layer

## Specific Ideas

No specific requirements — open to standard approaches that match existing codebase patterns.

## Deferred Ideas

None — discussion stayed within phase scope

---

*Phase: 05-data-transformation*
*Context gathered: 2026-04-14*
