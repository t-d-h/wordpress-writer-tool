# Requirements

**Version:** 1.0
**Status:** Active
**Last Updated:** 2026-04-14

## v1 Requirements

### Token Usage Display (TOKEN)

- [ ] **TOKEN-01**: User can view token usage breakdown in Project general tab above statistics section
- [ ] **TOKEN-02**: System displays token usage breakdown by post type (research, outline, content, thumbnail)
- [ ] **TOKEN-03**: System shows total input tokens across all post types
- [ ] **TOKEN-04**: System shows total output tokens across all post types
- [ ] **TOKEN-05**: System includes deleted posts in token usage calculations
- [ ] **TOKEN-06**: System calculates token usage on-the-fly from posts collection
- [ ] **TOKEN-07**: Token usage display is always visible when viewing project details

### All Posts Tab (POSTS)

- [ ] **POSTS-01**: User can view "All Posts" tab in each project
- [ ] **POSTS-02**: System displays all WordPress posts (both tool-created and existing)
- [ ] **POSTS-03**: System provides visual distinction between tool-created and existing posts
- [ ] **POSTS-04**: User can click Edit button to open WordPress admin edit page in new tab
- [ ] **POSTS-05**: System displays post name/title
- [ ] **POSTS-06**: System displays post URL
- [ ] **POSTS-07**: System displays post categories
- [ ] **POSTS-08**: System displays post tags
- [ ] **POSTS-09**: System displays post date
- [ ] **POSTS-10**: User can filter posts by status (published, draft, pending, etc.)
- [ ] **POSTS-11**: User can sort posts by date
- [ ] **POSTS-12**: User can search posts by title
- [ ] **POSTS-13**: Backend provides WordPress API method to fetch all posts
- [ ] **POSTS-14**: System tracks post origin in database (tool-created vs existing)

### WordPress Integration (WP)

- [ ] **WP-01**: Backend WordPress service can fetch all posts from WordPress REST API
- [ ] **WP-02**: Backend WordPress service supports pagination for large post lists
- [ ] **WP-03**: Backend WordPress service supports status filtering
- [ ] **WP-04**: Backend WordPress service supports search by title
- [ ] **WP-05**: Backend WordPress service handles API rate limiting gracefully

### Performance (PERF)

- [ ] **PERF-01**: Token usage aggregation completes within 1 second for projects with <100 posts
- [ ] **PERF-02**: All Posts tab loads within 2 seconds for projects with <200 posts
- [ ] **PERF-03**: System implements database indexes for token usage queries
- [ ] **PERF-04**: System implements caching for WordPress post data (optional for MVP)

### Data Integrity (DATA)

- [ ] **DATA-01**: System maintains accurate token usage counts across all post types
- [ ] **DATA-02**: System correctly identifies post origin (tool-created vs existing)
- [ ] **DATA-03**: System handles orphaned post records gracefully
- [ ] **DATA-04**: System prevents duplicate post creation

### User Experience (UX)

- [ ] **UX-01**: Token usage display is visually distinct from existing statistics
- [ ] **UX-02**: All Posts tab provides clear visual indicators for post types
- [ ] **UX-03**: Edit button is clearly visible and accessible
- [ ] **UX-04**: Filter controls are intuitive and responsive
- [ ] **UX-05**: Search functionality provides real-time feedback

## v2 Requirements (Deferred)

- [ ] **TOKEN-V2-01**: System provides historical token usage trends over time
- [ ] **TOKEN-V2-02**: System implements token usage pagination for large projects
- [ ] **POSTS-V2-01**: User can perform bulk operations on multiple posts
- [ ] **POSTS-V2-02**: System provides advanced filtering options
- [ ] **POSTS-V2-03**: User can export post list to CSV
- [ ] **PERF-V2-01**: System implements Redis caching for WordPress post data
- [ ] **PERF-V2-02**: System implements query result caching for token usage

## Out of Scope

- **In-app post editing** — WordPress admin provides excellent editing experience; deep link to WordPress admin instead
- **Full WordPress clone** — Focus on AI generation, leverage WordPress for content management
- **Social media auto-posting** — Use dedicated social media tools or Jetpack Social
- **SEO optimization** — Integrate with existing SEO plugins (Yoast, Rank Math)
- **Content calendar** — Use WordPress editorial calendar plugins
- **Multi-user collaboration** — Requires authentication system (deferred to later)
- **Advanced analytics** — Link to Google Analytics or Jetpack Stats
- **Email notifications** — Use WordPress notification system or defer
- **Version control for posts** — Use WordPress revision system
- **Content syndication** — Use RSS feeds or dedicated syndication tools

## Traceability

| Requirement ID | Phase | Status | Notes |
|---------------|-------|--------|-------|
| TOKEN-01 | Phase 1 | Pending | Display in ProjectDetail.jsx |
| TOKEN-02 | Phase 1 | Pending | Aggregate by token_usage field |
| TOKEN-03 | Phase 1 | Pending | Sum input tokens |
| TOKEN-04 | Phase 1 | Pending | Sum output tokens |
| TOKEN-05 | Phase 1 | Pending | Query all posts, no status filter |
| TOKEN-06 | Phase 1 | Pending | MongoDB aggregation pipeline |
| TOKEN-07 | Phase 1 | Pending | Always render component |
| POSTS-01 | Phase 2 | Pending | Add tab to ProjectDetail.jsx |
| POSTS-02 | Phase 2 | Pending | Merge WordPress API data with database |
| POSTS-03 | Phase 2 | Pending | Visual badge or color coding |
| POSTS-04 | Phase 2 | Pending | target="_blank" attribute |
| POSTS-05 | Phase 2 | Pending | Display post.title.rendered |
| POSTS-06 | Phase 2 | Pending | Display post.link |
| POSTS-07 | Phase 2 | Pending | Display post.categories array |
| POSTS-08 | Phase 2 | Pending | Display post.tags array |
| POSTS-09 | Phase 2 | Pending | Display post.date |
| POSTS-10 | Phase 2 | Pending | Filter dropdown component |
| POSTS-11 | Phase 2 | Pending | Sort by date toggle |
| POSTS-12 | Phase 2 | Pending | Search input with debouncing |
| POSTS-13 | Phase 2 | Pending | Add to wp_service.py |
| POSTS-14 | Phase 2 | Pending | Add origin field to Post model |
| WP-01 | Phase 2 | Pending | Extend wp_service.py |
| WP-02 | Phase 2 | Pending | Implement pagination logic |
| WP-03 | Phase 2 | Pending | Add status parameter to API call |
| WP-04 | Phase 2 | Pending | Add search parameter to API call |
| WP-05 | Phase 2 | Pending | Implement rate limiting |
| PERF-01 | Phase 1 | Pending | Optimize aggregation query |
| PERF-02 | Phase 2 | Pending | Implement virtualization if needed |
| PERF-03 | Phase 1 | Pending | Add database indexes |
| PERF-04 | Phase 2 | Pending | Optional caching layer |
| DATA-01 | Phase 1 | Pending | Validate aggregation logic |
| DATA-02 | Phase 2 | Pending | Implement origin tracking |
| DATA-03 | Phase 2 | Pending | Handle missing WordPress posts |
| DATA-04 | Phase 2 | Pending | Check for duplicates before creation |
| UX-01 | Phase 1 | Pending | Design token usage component |
| UX-02 | Phase 2 | Pending | Design post type indicators |
| UX-03 | Phase 2 | Pending | Style edit button prominently |
| UX-04 | Phase 2 | Pending | Implement filter UI |
| UX-05 | Phase 2 | Pending | Implement search UI |

## Success Criteria

### Token Usage Display
- User can see token usage breakdown when viewing any project
- Token totals are accurate and include all posts (including deleted)
- Display loads quickly (<1 second) for typical projects
- Visual design is clear and easy to understand

### All Posts Tab
- User can view all WordPress posts for a project
- Posts are clearly distinguished by origin (tool-created vs existing)
- Edit functionality works correctly and opens in new tab
- Filtering, sorting, and search work as expected
- Performance is acceptable for typical project sizes

### Overall
- Both features integrate seamlessly with existing codebase
- No breaking changes to existing functionality
- Code follows established patterns and conventions
- Features are testable and maintainable
