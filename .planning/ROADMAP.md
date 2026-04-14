# Roadmap

**Project:** WordPress Writer Tool
**Version:** 1.0
**Last Updated:** 2026-04-14

## Phases

- [ ] **Phase 1: Token Usage Display** - Display token usage breakdown in project details
- [ ] **Phase 2: WordPress Integration Backend** - Backend services for fetching WordPress posts
- [ ] **Phase 3: All Posts Tab UI** - Frontend interface for viewing and managing all posts

## Phase Details

### Phase 1: Token Usage Display

**Goal**: Users can view token usage breakdown for each project, including all post types and deleted posts

**Depends on**: Nothing (first phase)

**Requirements**: TOKEN-01, TOKEN-02, TOKEN-03, TOKEN-04, TOKEN-05, TOKEN-06, TOKEN-07, PERF-01, PERF-03, DATA-01, UX-01

**Success Criteria** (what must be TRUE):
1. User can view token usage breakdown in Project general tab above statistics section
2. System displays token usage breakdown by post type (research, outline, content, thumbnail)
3. System shows total input tokens and total output tokens across all post types
4. System includes deleted posts in token usage calculations
5. Token usage display loads within 1 second for projects with <100 posts

**Plans**: TBD

### Phase 2: WordPress Integration Backend

**Goal**: Backend provides robust WordPress REST API integration for fetching, filtering, and searching posts

**Depends on**: Phase 1

**Requirements**: WP-01, WP-02, WP-03, WP-04, WP-05, PERF-02, PERF-04, DATA-02, DATA-03, DATA-04

**Success Criteria** (what must be TRUE):
1. Backend WordPress service can fetch all posts from WordPress REST API
2. Backend WordPress service supports pagination for large post lists
3. Backend WordPress service supports status filtering and search by title
4. Backend WordPress service handles API rate limiting gracefully
5. System correctly identifies post origin (tool-created vs existing)

**Plans**: 3 plans
- [x] 02-01-PLAN.md — Enhanced WordPress service with search, filtering, and rate limiting
- [x] 02-02-PLAN.md — Post origin tracking and sync service
- [x] 02-03-PLAN.md — Orphan detection and API endpoints

### Phase 3: All Posts Tab UI

**Goal**: Users can view, filter, sort, and search all WordPress posts for a project with clear visual distinction

**Depends on**: Phase 2

**Requirements**: POSTS-01, POSTS-02, POSTS-03, POSTS-04, POSTS-05, POSTS-06, POSTS-07, POSTS-08, POSTS-09, POSTS-10, POSTS-11, POSTS-12, POSTS-13, POSTS-14, UX-02, UX-03, UX-04, UX-05

**Success Criteria** (what must be TRUE):
1. User can view "All Posts" tab in each project
2. System displays all WordPress posts (both tool-created and existing)
3. System provides visual distinction between tool-created and existing posts
4. User can click Edit button to open WordPress admin edit page in new tab
5. User can filter posts by status, sort by date, and search by title

**Plans**: TBD
**UI hint**: yes

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Token Usage Display | 0/0 | Not started | - |
| 2. WordPress Integration Backend | 0/3 | Planned | - |
| 3. All Posts Tab UI | 0/0 | Not started | - |

## Dependencies

```
Phase 1 (Token Usage Display)
    ↓
Phase 2 (WordPress Integration Backend)
    ↓
Phase 3 (All Posts Tab UI)
```

## Notes

- All phases follow existing codebase patterns and conventions
- Performance requirements are scoped for MVP (no caching unless necessary)
- Token usage calculated on-the-fly for simplicity
- Post origin tracking added to support All Posts tab functionality
