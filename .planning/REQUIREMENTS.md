# Requirements

**Project:** WordPress Writer Tool
**Milestone:** v1.1 All Posts Table View
**Last Updated:** 2026-04-14

## v1.1 Requirements

### Backend API

- [ ] **BACKEND-01**: Backend exposes search, orderby, and order parameters in get_site_posts endpoint
- [ ] **BACKEND-02**: Backend supports 100 posts per page pagination
- [ ] **BACKEND-03**: Backend returns WordPress REST API data with proper transformation
- [ ] **BACKEND-04**: Backend caches WordPress posts in MongoDB or Redis for faster retrieval
- [ ] **BACKEND-05**: Backend implements cache invalidation when posts are created/updated/deleted
- [ ] **BACKEND-06**: Backend provides cache refresh mechanism for manual sync

### Frontend UI

- [x] **FRONTEND-01**: User can view posts in table layout with columns: Title, URL, Categories, Tags, Date, Status, Actions
- [x] **FRONTEND-02**: User can search posts by title using search input field
- [x] **FRONTEND-03**: User can sort posts by date, title, or status using sort dropdown
- [ ] **FRONTEND-04**: User can navigate between pages using Previous/Next pagination controls
- [ ] **FRONTEND-05**: User sees loading states when pagination changes
- [x] **FRONTEND-06**: User sees loading states when pagination changes
- [x] **FRONTEND-07**: User sees appropriate empty state when no posts match criteria

### Cleanup

- [x] **CLEANUP-01**: PostCard component is removed from All Posts tab
- [ ] **CLEANUP-02**: Origin badges are removed from All Posts tab
- [x] **CLEANUP-03**: Infinite scroll logic and event listeners are removed
- [x] **CLEANUP-04**: Unused state variables are removed

### Data Transformation

- [ ] **DATA-01**: WordPress REST API response is transformed to table format
- [ ] **DATA-02**: Nested categories and tags from _embedded['wp:term'] are handled correctly
- [ ] **DATA-03**: Dates are formatted for display
- [ ] **DATA-04**: Edit URLs are generated for WordPress admin

## Future Requirements

None deferred for this milestone.

## Out of Scope

- Site selection dropdown (scope is project's WordPress site only)
- Bulk operations
- Advanced filtering (date ranges, multiple status filters, category filtering)
- Input/output token separation
- Charts/visualizations

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BACKEND-01 | Phase 8 | Pending |
| BACKEND-02 | Phase 8 | Pending |
| BACKEND-03 | Phase 8 | Pending |
| BACKEND-04 | Phase 8 | Pending |
| BACKEND-05 | Phase 8 | Pending |
| BACKEND-06 | Phase 8 | Pending |
| FRONTEND-01 | Phase 6 | Complete |
| FRONTEND-02 | Phase 6 | Complete |
| FRONTEND-03 | Phase 6 | Complete |
| FRONTEND-04 | Phase 10 | Pending |
| FRONTEND-05 | Phase 10 | Pending |
| FRONTEND-06 | Phase 6 | Complete |
| FRONTEND-07 | Phase 6 | Complete |
| CLEANUP-01 | Phase 7 | Complete |
| CLEANUP-02 | Phase 11 | Pending |
| CLEANUP-03 | Phase 7 | Complete |
| CLEANUP-04 | Phase 7 | Complete |
| DATA-01 | Phase 9 | Pending |
| DATA-02 | Phase 9 | Pending |
| DATA-03 | Phase 9 | Pending |
| DATA-04 | Phase 9 | Pending |
