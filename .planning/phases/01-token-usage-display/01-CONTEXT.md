# Phase 1: Token Usage Display - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

## Phase Boundary

Display token usage breakdown in Project general tab above existing statistics section. Show breakdown by post type (research, outline, content, thumbnail) with total input and output tokens. Include deleted posts in calculations. Always visible, calculate on-the-fly from posts collection.

## Implementation Decisions

### Visual Presentation
- **D-01:** Token usage displayed as a separate section above the existing stats-grid in the general tab
- **D-02:** Use card-based layout consistent with existing stat-cards (reuses `.stat-card` CSS class)
- **D-03:** Display total tokens prominently at top, with breakdown by type below
- **D-04:** Use simple HTML/CSS for MVP (no charting library needed)

### Information Hierarchy
- **D-05:** Primary display: Total input tokens and total output tokens (large, prominent)
- **D-06:** Secondary display: Breakdown by post type (research, outline, content, thumbnail)
- **D-07:** Each type shows both input and output tokens

### Data Format
- **D-08:** Format numbers with commas for readability (e.g., "15,432" not "15432")
- **D-09:** Use "tokens" label for clarity (e.g., "15,432 tokens")
- **D-10:** No abbreviations (show full numbers, not "15.4K")

### Loading State
- **D-11:** Show loading spinner while aggregation query runs
- **D-12:** Display skeleton or placeholder text during load
- **D-13:** Load token usage data in parallel with existing stats (no blocking)

### Error Handling
- **D-14:** Show error message if aggregation fails (e.g., "Unable to load token usage")
- **D-15:** Graceful degradation - show "N/A" for failed calculations
- **D-16:** Log errors to console for debugging

### Performance
- **D-17:** Target <1 second load time for projects with <100 posts
- **D-18:** Use MongoDB aggregation pipeline with `$group` and `$sum` operators
- **D-19:** Add database indexes on `project_id` and `token_usage` fields for optimization

### Data Query
- **D-20:** Query all posts for project (no status filter - includes deleted)
- **D-21:** Aggregate token_usage.research, token_usage.outline, token_usage.content, token_usage.thumbnail
- **D-22:** Calculate total input = sum of all token_usage fields
- **D-23:** Calculate total output = sum of all token_usage fields (if separated)

### the agent's Discretion
- **D-24:** Specific visual styling (colors, spacing, typography) - match existing stat-card design
- **D-25:** Exact placement within general tab (margin/padding values)
- **D-26:** Whether to show zero values or hide them

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Project vision, core value, requirements
- `.planning/REQUIREMENTS.md` — Detailed requirements with REQ-IDs
- `.planning/ROADMAP.md` — Phase goals and success criteria

### Codebase Patterns
- `frontend/src/components/Projects/ProjectDetail.jsx` — Existing stats display pattern
- `frontend/src/index.css` — CSS variables and stat-card styling
- `backend/app/models/post.py` — TokenUsage model structure
- `backend/app/routers/projects.py` — Existing project stats endpoint

### Research Findings
- `.planning/research/STACK.md` — MongoDB aggregation approach
- `.planning/research/ARCHITECTURE.md` — Component boundaries and data flow
- `.planning/research/PITFALLS.md` — Performance and data consistency concerns

## Existing Code Insights

### Reusable Assets
- **stat-card CSS class**: Already defined in `frontend/src/index.css` with variants for different stat types
- **MongoDB aggregation**: Existing patterns in `backend/app/routers/projects.py` for stats calculation
- **TokenUsage model**: Already defined in `backend/app/models/post.py` with research, outline, content, thumbnail fields

### Established Patterns
- **Stats display**: Uses card-based layout with `.stat-card` class, `.stats-grid` container
- **Data fetching**: Uses `getProjectStats()` API call in `useEffect` hook
- **Loading states**: Uses `loading` state with spinner and conditional rendering
- **Error handling**: Uses try/catch with `alert()` for user feedback

### Integration Points
- **Frontend**: Add new section in `ProjectDetail.jsx` general tab, above existing stats-grid
- **Backend**: Add new endpoint or extend existing `/api/projects/{id}/stats` to include token usage
- **Database**: Query posts collection with aggregation pipeline on `token_usage` field

## Specific Ideas

No specific requirements — open to standard approaches that match existing codebase patterns.

## Deferred Ideas

None — discussion stayed within phase scope

---

*Phase: 01-token-usage-display*
*Context gathered: 2026-04-14*
