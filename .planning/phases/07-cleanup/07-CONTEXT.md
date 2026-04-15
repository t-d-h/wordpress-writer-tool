# Phase 7: Cleanup - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

## Phase Boundary

Remove legacy code and unused components from the All Posts tab that were replaced by the table view in Phase 6. This includes PostCard component, origin badges, infinite scroll logic, and related state variables.

## Implementation Decisions

### Verification Approach
- **D-01:** Manual testing of All Posts tab after each removal to ensure functionality remains intact
- **D-02:** Run existing frontend tests if available (npm test or similar)
- **D-03:** Verify no console errors in browser after cleanup
- **D-04:** Test all filter, sort, search, and pagination functionality still works

### CSS Cleanup Scope
- **D-05:** Remove unused CSS classes related to PostCard and origin badges
- **D-06:** Remove `.post-card`, `.post-card-header`, `.post-card-title`, `.post-card-meta`, `.post-card-url`, `.post-card-categories`, `.post-card-tags` classes
- **D-07:** Remove `.origin-badge`, `.origin-tool`, `.origin-existing` classes
- **D-08:** Remove `.badge-category`, `.badge-tag` classes (if only used by PostCard)
- **D-09:** Keep generic `.badge` class if used elsewhere in the application

### State Variable Cleanup
- **D-10:** Remove `allPosts` state (replaced by table data from API)
- **D-11:** Remove `loadingAllPosts` state (replaced by table loading state)
- **D-12:** Remove `allPostsError` state (replaced by table error state)
- **D-13:** Remove `page` state (infinite scroll pagination - replaced by manual pagination)
- **D-14:** Remove `hasMore` state (infinite scroll - no longer needed)
- **D-15:** Remove `loadingMore` state (infinite scroll - no longer needed)
- **D-16:** Keep `statusFilter`, `sortBy`, `searchQuery` states (still used by table)
- **D-17:** Keep `project`, `stats`, `posts`, `loading`, `tokenUsage` states (used by other tabs)

### Component Removal
- **D-18:** Remove PostCard.jsx component file entirely
- **D-19:** Remove PostCard import from ProjectDetail.jsx
- **D-20:** Remove PostCard usage in All Posts tab rendering

### Logic Removal
- **D-21:** Remove infinite scroll event listener (handleScroll useEffect)
- **D-22:** Remove loadMorePosts function
- **D-23:** Remove scroll detection logic (scrollHeight, scrollTop, clientHeight calculations)
- **D-24:** Remove "Loading more posts..." and "No more posts to load" UI elements

### Rollback Strategy
- **D-25:** Create git commit before each major removal (component, CSS, state, logic)
- **D-26:** Use descriptive commit messages for easy rollback (e.g., "remove: PostCard component")
- **D-27:** Test after each commit to identify which change caused issues
- **D-28:** Use `git revert` if needed to undo specific commits

### the agent's Discretion
- **D-29:** Order of removal (component first, then CSS, then state, then logic - or different order)
- **D-30:** Whether to remove unused imports immediately or after testing
- **D-31:** Whether to add comments explaining removals or just remove cleanly
- **D-32:** Whether to verify CSS classes are unused before removal (grep search)

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Project vision, core value, requirements
- `.planning/REQUIREMENTS.md` — Detailed requirements with REQ-IDs (CLEANUP-01 through CLEANUP-04)
- `.planning/ROADMAP.md` — Phase goals and success criteria

### Codebase Patterns
- `frontend/src/components/Projects/ProjectDetail.jsx` — Component with legacy code to remove
- `frontend/src/components/Projects/PostCard.jsx` — Component to delete entirely
- `frontend/src/index.css` — CSS file with unused classes to remove
- `frontend/src/components/AllPosts.jsx` — Reference implementation for table view (Phase 6)

### Prior Phase Context
- `.planning/phases/06-frontend-ui/06-CONTEXT.md` — Table view implementation decisions
- `.planning/phases/03-all-posts-tab-ui/03-CONTEXT.md` — Original card layout decisions (being removed)
- `.planning/phases/05-data-transformation/05-CONTEXT.md` — Data transformation decisions

## Existing Code Insights

### Reusable Assets
- **Table view implementation**: AllPosts.jsx shows the new table pattern that replaces PostCard
- **CSS classes**: `.table-container`, `table`, `thead`, `tbody` classes for table layout
- **Pagination**: Manual pagination controls in AllPosts.jsx (Previous/Next buttons)

### Established Patterns
- **Component removal**: No prior examples of component removal in this codebase
- **CSS cleanup**: No prior examples of CSS class removal
- **State cleanup**: No prior examples of state variable removal
- **Git workflow**: Commits are made after each plan completion

### Integration Points
- **Frontend**: ProjectDetail.jsx is the only file using PostCard and infinite scroll
- **CSS**: index.css contains all styling, no separate CSS files per component
- **API**: No backend changes needed (cleanup is frontend-only)

## Specific Ideas

No specific requirements — follow standard cleanup practices with careful verification.

## Deferred Ideas

None — discussion stayed within phase scope

---

*Phase: 07-cleanup*
*Context gathered: 2026-04-15*