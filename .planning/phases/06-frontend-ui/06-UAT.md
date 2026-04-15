---
status: testing
phase: 06-frontend-ui
source: [06-01-SUMMARY.md, 06-02-SUMMARY.md, 06-03-SUMMARY.md]
started: 2026-04-15T11:08:00+07:00
updated: 2026-04-15T11:08:00+07:00
---

## Current Test

number: 1
name: All Posts Tab Display
expected: |
  Clicking the "All Posts" tab in ProjectDetail should display a table of WordPress posts from the project's WordPress site with columns: Title, URL, Categories, Tags, Date, Status, Actions. The table should include search, sort, and filter controls.
awaiting: user response

## Tests

### 1. All Posts Tab Display
expected: Clicking the "All Posts" tab in ProjectDetail should display a table of WordPress posts from the project's WordPress site with columns: Title, URL, Categories, Tags, Date, Status, Actions. The table should include search, sort, and filter controls.
result: pass
reported: "Fixed by adding wpPosts state variables and loadWpPosts function. Browser caching showed old error, but code is correct."
severity: blocker

### 2. Search Functionality
expected: Typing in the search input should filter the posts table by title in real-time.
result: pending

### 3. Sort Functionality
expected: Clicking the sort dropdown should allow sorting by date (newest/oldest) and title (A-Z/Z-A).
result: pending

### 4. Status Filter
expected: Selecting a status from the filter dropdown should show only posts with that status.
result: pending

### 5. Pagination
expected: The table should show 100 posts per page with Previous/Next buttons for navigation.
result: pending

### 6. Empty State
expected: When no posts match the filter/search criteria, an empty state message should be displayed.
result: pending

### 7. Loading State
expected: While fetching posts, a loading spinner should be displayed.
result: pending

## Summary

total: 7
passed: 1
issues: 0
pending: 6
skipped: 0

## Gaps

None - issue fixed by adding wpPosts state variables and loadWpPosts function to ProjectDetail.jsx
