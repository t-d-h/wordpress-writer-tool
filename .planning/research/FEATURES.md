# Feature Landscape

**Domain:** WordPress Writer Tool - All Posts Table View
**Researched:** 2026-04-14

## Table Stakes

Features users expect in a table view. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Table Layout** | Standard data presentation for post lists | Low | Replace PostCard grid with table layout using existing CSS |
| **Column Headers** | Users need to know what each column represents | Low | Title, URL, Categories, Tags, Date, Status, Actions |
| **Status Filter** | Users need to filter posts by publication status | Low | All, Published, Draft, Pending, Failed (existing in ProjectDetail) |
| **Sort by Date** | Users need to see newest/oldest posts first | Low | Newest First, Oldest First (existing in ProjectDetail) |
| **Sort by Title** | Users need to find posts alphabetically | Low | Title A-Z, Title Z-A (existing in ProjectDetail) |
| **Sort by Status** | Users need to group posts by status | Low | Status sort (existing in ProjectDetail) |
| **Search by Title** | Users need to find specific posts quickly | Low | Search input with debounced filtering (existing in ProjectDetail) |
| **Manual Pagination** | Users need to navigate large post lists | Medium | 100 posts per page, Previous/Next buttons, page indicator |
| **Post URL Display** | Users need to see and access post URLs | Low | Clickable link with security attributes (existing in AllPosts) |
| **Categories Display** | Users need to see post categories | Low | Comma-separated list or badges (existing in AllPosts) |
| **Tags Display** | Users need to see post tags | Low | Comma-separated list or badges (existing in AllPosts) |
| **Date Display** | Users need to see post creation date | Low | Formatted date string (existing in AllPosts) |
| **Status Badge** | Users need to see post status at a glance | Low | Color-coded badge (existing in AllPosts) |
| **Edit Action** | Users need to edit posts in WordPress | Low | Opens WordPress admin in new tab (existing in AllPosts) |
| **Loading State** | Users need to know data is loading | Low | Spinner during API fetch (existing in ProjectDetail) |
| **Empty State** | Users need to know when no posts exist | Low | Message when no results (existing in ProjectDetail) |
| **Error State** | Users need to know when fetch fails | Low | Error message display (existing in ProjectDetail) |
| **Responsive Table** | Users need to view table on mobile | Medium | Horizontal scroll for overflow (existing CSS) |

## Differentiators

Features that set product apart. Not expected, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Project-Scoped View** | Shows only posts for current project, not all sites | Low | No site selection dropdown (simpler UX) |
| **100 Posts Per Page** | Better balance between performance and usability | Low | More posts per page than default 10-20 |
| **Real-time Search** | Instant feedback as user types | Low | Debounced search input (existing pattern) |
| **Multi-Column Sort** | Sort by multiple criteria (date + status) | High | Not in MVP, defer to future |
| **Bulk Actions** | Select multiple posts for batch operations | High | Not in MVP, defer to future |
| **Advanced Filters** | Filter by category, tag, date range | High | Not in MVP, defer to future |
| **Export to CSV** | Download post list for offline analysis | High | Not in MVP, defer to future |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Infinite Scroll** | Difficult to navigate large lists, no page context | Use manual pagination with page numbers |
| **Origin Badges** | Not needed in project-scoped view (all posts are from same site) | Remove origin badges from table view |
| **Site Selection Dropdown** | Project is already scoped to one WordPress site | Use project's wp_site_id directly |
| **PostCard Grid** | Less efficient for viewing many posts | Replace with table layout |
| **Client-side Sorting** | Inefficient for large datasets, inconsistent with server-side | Use WordPress REST API sorting |
| **Client-side Filtering** | Inefficient for large datasets, inconsistent with server-side | Use WordPress REST API filtering |
| **Client-side Search** | Inefficient for large datasets, inconsistent with server-side | Use WordPress REST API search |

## Feature Dependencies

```
Table Layout → Manual Pagination (table needs pagination for large datasets)
Search/Sort/Filter → Backend API Support (WordPress REST API parameters)
Manual Pagination → Total Count Display (users need to know total pages)
Status Filter → WordPress REST API status parameter
Sort Options → WordPress REST API orderby/order parameters
Search → WordPress REST API search parameter
```

## MVP Recommendation

Prioritize:
1. **Table Layout** - Replace PostCard grid with table (existing AllPosts.jsx pattern)
2. **Manual Pagination** - 100 posts per page with Previous/Next buttons
3. **Status Filter** - Keep existing filter functionality
4. **Sort by Date/Title/Status** - Keep existing sort functionality
5. **Search by Title** - Keep existing search functionality
6. **Post URL Display** - Clickable link with security attributes
7. **Categories/Tags Display** - Comma-separated lists or badges
8. **Date Display** - Formatted date string
9. **Status Badge** - Color-coded badge
10. **Edit Action** - Opens WordPress admin in new tab

Defer:
- **Multi-Column Sort**: Complexity high, not essential for MVP
- **Bulk Actions**: Complexity high, not essential for MVP
- **Advanced Filters**: Complexity high, not essential for MVP
- **Export to CSV**: Complexity high, not essential for MVP

## Implementation Notes

### Backend API Requirements
- **Existing**: `get_site_posts` endpoint supports `per_page`, `page`, `status`
- **Needed**: Add support for `search`, `orderby`, `order` parameters
- **WordPress REST API**: Already supports all required parameters

### Frontend Implementation
- **Reuse**: AllPosts.jsx table layout pattern
- **Reuse**: Existing CSS styles for table, status badges, action buttons
- **Reuse**: Existing search/sort/filter state management from ProjectDetail
- **Change**: Replace PostCard grid with table layout
- **Change**: Switch from infinite scroll to manual pagination
- **Remove**: PostCard component usage in All Posts tab
- **Remove**: Origin badges (not needed in project-scoped view)

### WordPress REST API Parameters
- **page**: Page number (default: 1)
- **per_page**: Posts per page (default: 10, max: 100)
- **status**: Filter by status (publish, draft, pending, private, future, any)
- **search**: Search by title/content
- **orderby**: Sort by field (date, title, modified, relevance, etc.)
- **order**: Sort direction (asc, desc)

### Expected Behavior
1. **Initial Load**: Fetch first page (100 posts) with default sort (newest first)
2. **Search**: Debounced search input (300-500ms) triggers API call with search parameter
3. **Sort**: Clicking column header or changing sort dropdown triggers API call with orderby/order
4. **Filter**: Changing status filter triggers API call with status parameter
5. **Pagination**: Clicking Previous/Next triggers API call with page parameter
6. **Loading**: Show spinner during API fetch
7. **Empty**: Show message when no results match criteria
8. **Error**: Show error message when API fetch fails
9. **Edit**: Clicking Edit button opens WordPress admin in new tab

## Sources

- **WordPress REST API Documentation**: https://developer.wordpress.org/rest-api/reference/posts/ (HIGH confidence)
- **W3C Tables Tutorial**: https://www.w3.org/WAI/tutorials/tables/ (HIGH confidence)
- **Existing AllPosts.jsx Implementation**: /root/vscode/wordpress-writer-tool/frontend/src/components/AllPosts.jsx (HIGH confidence)
- **Existing ProjectDetail.jsx Implementation**: /root/vscode/wordpress-writer-tool/frontend/src/components/Projects/ProjectDetail.jsx (HIGH confidence)
- **Existing CSS Styles**: /root/vscode/wordpress-writer-tool/frontend/src/index.css (HIGH confidence)
- **Backend wp_service.py**: /root/vscode/wordpress-writer-tool/backend/app/services/wp_service.py (HIGH confidence)
- **Backend wp_sites.py Router**: /root/vscode/wordpress-writer-tool/backend/app/routers/wp_sites.py (HIGH confidence)
