---
status: testing
phase: 03-all-posts-tab-ui
source: [03-01-SUMMARY.md, 03-02-SUMMARY.md]
started: 2026-04-14T16:21:53+07:00
updated: 2026-04-14T20:39:00+07:00
---

## Current Test

number: 2
name: Post Card Display
expected: |
  Posts are displayed in a grid layout using PostCard components. Each card shows the post title, status badge, formatted date, origin badge (Tool or Existing), and an Edit button.
awaiting: user response

## Tests

### 1. All Posts Tab Navigation
expected: Navigate to a project detail page. Click the "All Posts" tab button. The tab becomes active and displays the All Posts section. The tab follows the same pattern as General and Content tabs.
result: pass

### 2. Post Card Display
expected: Posts are displayed in a grid layout using PostCard components. Each card shows the post title, status badge, formatted date, origin badge (Tool or Existing), and an Edit button.
result: pending

### 3. Origin Badge Rendering
expected: Tool-created posts show a "Tool" badge. Existing WordPress posts show an "Existing" badge. The badge is positioned on the card and clearly distinguishes post types.
result: pending

### 4. Edit Button Functionality
expected: Clicking the Edit button on a post card opens the WordPress admin edit page in a new tab. The URL format is {wp_site_url}/wp-admin/post.php?post={wp_post_id}&action=edit.
result: pending

### 5. Loading State
expected: When the All Posts tab is first opened or refreshed, a loading spinner is displayed while posts are being fetched from the backend.
result: pending

### 6. Error State
expected: If the post fetch fails, an error message is displayed to the user. The error message indicates that posts could not be loaded.
result: pending

### 7. Empty State
expected: When a project has no posts, a "No posts yet" message with an icon is displayed in the All Posts tab.
result: pending

### 8. Status Filter Dropdown
expected: A status filter dropdown is displayed at the top of the All Posts tab. The dropdown shows options: all, published, draft, pending, failed.
result: pending

### 9. Status Filter Functionality
expected: Selecting a status from the dropdown filters the displayed posts. "all" shows all posts. Specific status options show only posts with that status. The filter updates immediately.
result: pending

### 10. Sort Dropdown
expected: A sort dropdown is displayed at the top of the All Posts tab next to the filter. The dropdown shows options: date-desc, date-asc, title-asc, title-desc, status.
result: pending

### 11. Sort by Date (Newest First)
expected: Selecting "date-desc" sorts posts by date with the newest posts appearing first.
result: pending

### 12. Sort by Date (Oldest First)
expected: Selecting "date-asc" sorts posts by date with the oldest posts appearing first.
result: pending

### 13. Sort by Title (A-Z)
expected: Selecting "title-asc" sorts posts by title in alphabetical order (A-Z).
result: pending

### 14. Sort by Title (Z-A)
expected: Selecting "title-desc" sorts posts by title in reverse alphabetical order (Z-A).
result: pending

### 15. Sort by Status
expected: Selecting "status" sorts posts alphabetically by their status.
result: pending

### 16. Search Input
expected: A search input field is displayed at the top of the All Posts tab next to the filter and sort dropdowns.
result: pending

### 17. Search by Title
expected: Typing in the search input filters posts by title. The search is case-insensitive and matches partial titles.
result: pending

### 18. Real-time Search
expected: Search results update in real-time as the user types. No need to press Enter or click a search button.
result: pending

### 19. Combined Filter and Sort
expected: Status filter and sort dropdown work together. Posts are first filtered by status, then sorted by the selected criteria.
result: pending

### 20. Combined Filter, Sort, and Search
expected: Status filter, sort dropdown, and search input all work together. Posts are filtered by status, sorted by criteria, and searched by title in that order.
result: pending

## Summary

total: 20
passed: 1
issues: 0
pending: 19
skipped: 0

## Gaps

none yet
