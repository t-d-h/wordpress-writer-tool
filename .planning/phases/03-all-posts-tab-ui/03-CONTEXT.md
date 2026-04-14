# Phase 3: All Posts Tab UI - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

## Phase Boundary

Add "All Posts" tab to ProjectDetail component (inside each project, not main navigation). Display all WordPress posts (both tool-created and existing) with filtering, sorting, and search capabilities. Provide visual distinction between post types and edit button to open WordPress admin.

## Implementation Decisions

### Post List Layout
- **D-01:** Use card-based layout for post display (reuses existing Card component)
- **D-02:** Card shows essential information only: title, status, date, origin badge, edit button
- **D-03:** Cards arranged in grid layout (consistent with existing stat-card pattern)

### Visual Distinction
- **D-04:** Use badge to distinguish tool-created vs existing posts
- **D-05:** Badge shows "Tool" for tool-created posts, "Existing" for WordPress posts
- **D-06:** Badge placed on card (position at agent's discretion)

### Filter UI
- **D-07:** Status filter placed at top of tab, above post list
- **D-08:** Filter dropdown shows status options (all, published, draft, pending, etc.)
- **D-09:** Filter dropdown positioned in control bar at top

### Sorting UI
- **D-10:** Sort dropdown placed at top of tab, next to filter
- **D-11:** Sort options include date (newest/oldest), title (A-Z/Z-A), status
- **D-12:** Sort dropdown positioned in control bar at top

### Search UI
- **D-13:** Search input placed at top of tab, next to filter and sort
- **D-14:** Search filters by post title
- **D-15:** Search input positioned in control bar at top

### Empty State
- **D-16:** Show simple "No posts yet" message with icon when no posts exist
- **D-17:** No call-to-action button (keep it simple)

### Pagination
- **D-18:** Use infinite scroll to load more posts as user scrolls down
- **D-19:** Seamless experience without manual pagination controls

### the agent's Discretion
- **D-20:** Exact badge placement on card (top-right, top-left, etc.)
- **D-21:** Card grid layout (2 columns, 3 columns, responsive)
- **D-22:** Control bar layout (filter, sort, search arrangement)
- **D-23:** Loading state for infinite scroll (spinner, skeleton, etc.)
- **D-24:** Error handling for failed API calls

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Project vision, core value, requirements
- `.planning/REQUIREMENTS.md` — Detailed requirements with REQ-IDs
- `.planning/ROADMAP.md` — Phase goals and success criteria

### Codebase Patterns
- `frontend/src/components/Projects/ProjectDetail.jsx` — Existing tab system and patterns
- `frontend/src/components/Projects/TokenUsageCard.jsx` — Card component example
- `frontend/src/index.css` — CSS variables and stat-card styling
- `frontend/src/api/client.js` — API client patterns

### Backend Integration
- `backend/app/routers/wordpress.py` — WordPress sync endpoints (from Phase 02)
- `backend/app/services/post_sync_service.py` — Post sync service (from Phase 02)
- `backend/app/services/wp_service.py` — WordPress service with search/filtering (from Phase 02)
- `backend/app/models/post.py` — Post model with origin field (from Phase 02)

### Prior Phase Context
- `.planning/phases/01-token-usage-display/01-CONTEXT.md` — Card-based layout decisions
- `.planning/phases/02-wordpress-integration-backend/02-CONTEXT.md` — Post origin tracking decisions

## Existing Code Insights

### Reusable Assets
- **Tab system**: Already exists in ProjectDetail.jsx with `activeTab` state (general, content tabs)
- **Card component**: TokenUsageCard.jsx shows card pattern with stat-card CSS class
- **CSS classes**: `.stat-card`, `.stats-grid` for card-based layouts
- **API client**: getPostsByProject() function exists for fetching posts
- **Loading states**: Loading spinner pattern already used in ProjectDetail.jsx
- **Error handling**: alert() pattern already used for user feedback

### Established Patterns
- **Tab navigation**: Uses `activeTab` state with conditional rendering
- **Data fetching**: Uses `useEffect` hook with API calls
- **Loading states**: Uses `loading` state with spinner and conditional rendering
- **Error handling**: Uses try/catch with `alert()` for user feedback
- **Card layout**: Uses grid layout with CSS classes
- **Infinite scroll**: Not currently used in codebase (new pattern for this phase)

### Integration Points
- **Frontend**: Add new "All Posts" tab to ProjectDetail.jsx (third tab after general, content)
- **Backend**: Use existing WordPress sync endpoints from Phase 02
- **API**: Extend or use existing getPostsByProject() with filter/sort/search parameters
- **Data**: Post model already has `origin` field from Phase 02

## Specific Ideas

No specific requirements — open to standard approaches that match existing codebase patterns.

## Deferred Ideas

None — discussion stayed within phase scope

---

*Phase: 03-all-posts-tab-ui*
*Context gathered: 2026-04-14*
