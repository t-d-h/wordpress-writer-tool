# Roadmap

**Project:** WordPress Writer Tool
**Milestone:** v1.1 All Posts Table View
**Last Updated:** 2026-04-14

## Milestones

- ✅ **v1.0 MVP** — Phases 1-3 (shipped 2026-04-14)
- 🔄 **v1.1 All Posts Table View** — Phases 4-7 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-3) — SHIPPED 2026-04-14</summary>

- [x] Phase 1: Token Usage Display (4/4 plans) — completed 2026-04-14
- [x] Phase 2: WordPress Integration Backend (3/3 plans) — completed 2026-04-14
- [x] Phase 3: All Posts Tab UI (7/7 plans) — completed 2026-04-14

</details>

<details>
<summary>🔄 v1.1 All Posts Table View (Phases 4-7) — IN PROGRESS</summary>

 - [ ] Phase 4: Backend API Enhancement — 3/3 plans planned
 - [ ] Phase 5: Data Transformation — Not started
 - [ ] Phase 6: Frontend UI — 3/3 plans planned
 - [ ] Phase 7: Cleanup — Not started

</details>

## Phase Details

### Phase 4: Backend API Enhancement

**Goal**: Backend provides efficient post retrieval with caching, pagination, and search/sort capabilities

**Depends on**: Phase 3 (v1.0 All Posts Tab UI)

**Requirements**: BACKEND-01, BACKEND-02, BACKEND-03, BACKEND-04, BACKEND-05, BACKEND-06

**Success Criteria** (what must be TRUE):
1. Backend API returns 100 posts per page with pagination parameters
2. Backend API supports search by title, sort by date/title/status
3. Backend API caches WordPress posts in MongoDB or Redis
4. Backend API invalidates cache when posts are created/updated/deleted
5. Backend API provides manual cache refresh endpoint

**Plans**: 3 plans
- [ ] 04-01-PLAN.md — Create WordPress post cache service with MongoDB storage and TTL
- [ ] 04-02-PLAN.md — Update get_site_posts endpoint with search/sort parameters
- [ ] 04-03-PLAN.md — Integrate cache service with hybrid pagination and refresh endpoint

### Phase 5: Data Transformation

**Goal**: WordPress REST API responses are transformed into table-ready format

**Depends on**: Phase 4

**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04

**Success Criteria** (what must be TRUE):
1. WordPress REST API response is transformed to table format with all required fields
2. Nested categories and tags from _embedded['wp:term'] are extracted correctly
3. Dates are formatted for display in table
4. Edit URLs are generated for WordPress admin

**Plans**: TBD

### Phase 6: Frontend UI

**Goal**: Users can view and manage posts in a table with search, sort, filter, and pagination

**Depends on**: Phase 5

**Requirements**: FRONTEND-01, FRONTEND-02, FRONTEND-03, FRONTEND-04, FRONTEND-05, FRONTEND-06, FRONTEND-07

**Success Criteria** (what must be TRUE):
1. User can view posts in table layout with columns: Title, URL, Categories, Tags, Date, Status, Actions
2. User can search posts by title using search input field
3. User can sort posts by date, title, or status using sort dropdown
4. User can filter posts by status using status filter dropdown
5. User can navigate between pages using Previous/Next pagination controls
6. User sees loading states when pagination changes
7. User sees appropriate empty state when no posts match criteria

**Plans**: 3 plans
- [x] 06-01-PLAN.md — Update API client and add search/sort state management
- [x] 06-02-PLAN.md — Add search input and sort dropdown UI controls
- [x] 06-03-PLAN.md — Verify all frontend requirements through comprehensive testing

**UI hint**: yes

### Phase 7: Cleanup

**Goal**: Legacy code and unused components are removed

**Depends on**: Phase 6

**Requirements**: CLEANUP-01, CLEANUP-02, CLEANUP-03, CLEANUP-04

**Success Criteria** (what must be TRUE):
1. PostCard component is removed from All Posts tab
2. Origin badges are removed from All Posts tab
3. Infinite scroll logic and event listeners are removed
4. Unused state variables are removed

**Plans**: 3 plans
- [ ] 07-01-PLAN.md — Remove PostCard component and import
- [ ] 07-02-PLAN.md — Remove infinite scroll logic and unused state variables
- [ ] 07-03-PLAN.md — Remove unused CSS classes

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Token Usage Display | v1.0 | 4/4 | Complete | 2026-04-14 |
| 2. WordPress Integration Backend | v1.0 | 3/3 | Complete | 2026-04-14 |
| 3. All Posts Tab UI | v1.0 | 7/7 | Complete | 2026-04-14 |
| 4. Backend API Enhancement | v1.1 | 0/3 | Planned | - |
| 5. Data Transformation | v1.1 | 0/0 | Not started | - |
| 6. Frontend UI | v1.1 | 3/3 | Complete   | 2026-04-15 |
| 7. Cleanup | v1.1 | 0/3 | Planned | - |

---

**See `.planning/milestones/v1.0-ROADMAP.md` for full v1.0 milestone details.**
