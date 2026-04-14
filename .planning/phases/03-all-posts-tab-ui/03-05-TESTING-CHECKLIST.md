# All Posts Tab - Testing Checklist

## Overview
This document provides a comprehensive testing checklist for the All Posts tab functionality in the WordPress Writer Tool. The checklist covers UI testing, filter/sort/search functionality, infinite scroll, API endpoints, performance, and cross-browser compatibility.

## Test Environment
- **Project**: WordPress Writer Tool
- **Phase**: 03-all-posts-tab-ui
- **Plans**: 01-05 (UI, Filter/Sort/Search, Infinite Scroll, Backend API, Testing)
- **Test Date**: 2026-04-14

---

## Task 05-01: Manual UI Testing

### Test Case 05-01-01: Navigate to All Posts Tab
**Steps**:
1. Navigate to a project in the UI
2. Click on "All Posts" tab

**Expected Results**:
- [ ] "All Posts" tab appears in tab navigation
- [ ] Tab is active when clicked
- [ ] Tab follows existing pattern (general, content tabs)

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-01-02: Verify Posts Display
**Steps**:
1. Navigate to All Posts tab
2. Observe post display

**Expected Results**:
- [ ] Posts are displayed in card layout
- [ ] Each card shows: title, status, date, origin badge, edit button
- [ ] Cards are arranged in grid layout
- [ ] Cards use stat-card CSS class

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-01-03: Verify Origin Badge
**Steps**:
1. Navigate to All Posts tab
2. Observe origin badges on post cards

**Expected Results**:
- [ ] Origin badge shows "Tool" for tool-created posts
- [ ] Origin badge shows "Existing" for WordPress posts
- [ ] Badge is positioned on card
- [ ] Badge styling is distinct (origin-tool vs origin-existing)

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-01-04: Verify Edit Button
**Steps**:
1. Navigate to All Posts tab
2. Click edit button on a post card

**Expected Results**:
- [ ] Edit button is clearly visible
- [ ] Edit button opens WordPress admin in new tab
- [ ] WordPress admin URL format: `{wp_site_url}/wp-admin/post.php?post={wp_post_id}&action=edit`
- [ ] Edit button only shows for posts with wp_post_id

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-01-05: Verify Empty State
**Steps**:
1. Navigate to a project with no posts
2. Observe All Posts tab

**Expected Results**:
- [ ] Empty state shows when no posts exist
- [ ] Empty state shows appropriate icon
- [ ] Empty state shows descriptive message
- [ ] Empty state follows existing UI patterns

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-01-06: Verify Loading State
**Steps**:
1. Navigate to All Posts tab
2. Observe initial load

**Expected Results**:
- [ ] Loading spinner shows while fetching posts
- [ ] Loading spinner follows existing UI patterns
- [ ] Loading state is cleared after fetch completes

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-01-07: Verify Error State
**Steps**:
1. Simulate API error (e.g., network failure)
2. Navigate to All Posts tab

**Expected Results**:
- [ ] Error message shows if fetch fails
- [ ] Error message is descriptive
- [ ] Error message follows existing UI patterns
- [ ] User can retry (refresh button or similar)

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

## Task 05-02: Manual Filter Testing

### Test Case 05-02-01: Verify Status Filter Dropdown
**Steps**:
1. Navigate to All Posts tab
2. Observe status filter dropdown

**Expected Results**:
- [ ] Status filter dropdown shows all options
- [ ] Options include: all, published, draft, pending, failed
- [ ] Dropdown is positioned in control bar at top
- [ ] Dropdown follows existing UI patterns

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-02-02: Verify Filter by Status
**Steps**:
1. Navigate to All Posts tab
2. Select "published" from status filter
3. Observe displayed posts
4. Select "draft" from status filter
5. Observe displayed posts
6. Select "all" from status filter
7. Observe displayed posts

**Expected Results**:
- [ ] Posts are filtered correctly by status
- [ ] "published" shows only published posts
- [ ] "draft" shows only draft posts
- [ ] "all" shows all posts
- [ ] Filter updates immediately when selection changes

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-02-03: Verify Empty State with Filter
**Steps**:
1. Navigate to All Posts tab
2. Select a status that has no posts
3. Observe displayed posts

**Expected Results**:
- [ ] Empty state shows if no posts match filter
- [ ] Empty state shows appropriate message
- [ ] User can clear filter to see all posts

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-02-04: Verify Filter with Sort and Search
**Steps**:
1. Navigate to All Posts tab
2. Select a status filter
3. Apply a sort option
4. Type a search query
5. Observe displayed posts

**Expected Results**:
- [ ] Filter works in combination with sort
- [ ] Filter works in combination with search
- [ ] Filter, sort, and search work together
- [ ] Results are correct for all three applied

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

## Task 05-03: Manual Sort Testing

### Test Case 05-03-01: Verify Sort Dropdown
**Steps**:
1. Navigate to All Posts tab
2. Observe sort dropdown

**Expected Results**:
- [ ] Sort dropdown shows all options
- [ ] Options include: date-desc, date-asc, title-asc, title-desc, status
- [ ] Dropdown is positioned in control bar at top
- [ ] Dropdown follows existing UI patterns

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-03-02: Verify Sort by Date (Newest First)
**Steps**:
1. Navigate to All Posts tab
2. Select "date-desc" from sort dropdown
3. Observe displayed posts

**Expected Results**:
- [ ] Posts are sorted by date (newest first)
- [ ] Sorting uses created_at or updated_at field
- [ ] Sort updates immediately when selection changes

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-03-03: Verify Sort by Date (Oldest First)
**Steps**:
1. Navigate to All Posts tab
2. Select "date-asc" from sort dropdown
3. Observe displayed posts

**Expected Results**:
- [ ] Posts are sorted by date (oldest first)
- [ ] Sorting uses created_at or updated_at field
- [ ] Sort updates immediately when selection changes

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-03-04: Verify Sort by Title (A-Z)
**Steps**:
1. Navigate to All Posts tab
2. Select "title-asc" from sort dropdown
3. Observe displayed posts

**Expected Results**:
- [ ] Posts are sorted by title (A-Z)
- [ ] Sorting is case-insensitive
- [ ] Sort updates immediately when selection changes

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-03-05: Verify Sort by Title (Z-A)
**Steps**:
1. Navigate to All Posts tab
2. Select "title-desc" from sort dropdown
3. Observe displayed posts

**Expected Results**:
- [ ] Posts are sorted by title (Z-A)
- [ ] Sorting is case-insensitive
- [ ] Sort updates immediately when selection changes

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-03-06: Verify Sort by Status
**Steps**:
1. Navigate to All Posts tab
2. Select "status" from sort dropdown
3. Observe displayed posts

**Expected Results**:
- [ ] Posts are sorted by status (alphabetical)
- [ ] Sort updates immediately when selection changes

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-03-07: Verify Sort with Filter and Search
**Steps**:
1. Navigate to All Posts tab
2. Apply a status filter
3. Select a sort option
4. Type a search query
5. Observe displayed posts

**Expected Results**:
- [ ] Sort works in combination with filter
- [ ] Sort works in combination with search
- [ ] Filter, sort, and search work together
- [ ] Results are correctly sorted for all three applied

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

## Task 05-04: Manual Search Testing

### Test Case 05-04-01: Verify Search Input
**Steps**:
1. Navigate to All Posts tab
2. Observe search input

**Expected Results**:
- [ ] Search input is visible
- [ ] Search input is positioned in control bar at top
- [ ] Search input follows existing UI patterns
- [ ] Search input has placeholder text

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-04-02: Verify Search by Title
**Steps**:
1. Navigate to All Posts tab
2. Type a search query in search input
3. Observe displayed posts

**Expected Results**:
- [ ] Posts are filtered by title
- [ ] Search is case-insensitive
- [ ] Search updates as user types (real-time feedback)
- [ ] Empty search shows all posts

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-04-03: Verify Empty State with Search
**Steps**:
1. Navigate to All Posts tab
2. Type a search query that matches no posts
3. Observe displayed posts

**Expected Results**:
- [ ] Empty state shows if no posts match search
- [ ] Empty state shows appropriate message
- [ ] User can clear search to see all posts

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-04-04: Verify Search with Filter and Sort
**Steps**:
1. Navigate to All Posts tab
2. Apply a status filter
3. Select a sort option
4. Type a search query
5. Observe displayed posts

**Expected Results**:
- [ ] Search works in combination with filter
- [ ] Search works in combination with sort
- [ ] Filter, sort, and search work together
- [ ] Results are correct for all three applied

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-04-05: Verify Real-time Search
**Steps**:
1. Navigate to All Posts tab
2. Type search query character by character
3. Observe displayed posts after each character

**Expected Results**:
- [ ] Search updates in real-time as user types
- [ ] Results update immediately after each character
- [ ] No noticeable lag when typing
- [ ] Debouncing is applied if needed for performance

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

## Task 05-05: Manual Infinite Scroll Testing

### Test Case 05-05-01: Verify Infinite Scroll Load
**Steps**:
1. Navigate to All Posts tab with many posts (>20)
2. Scroll down to bottom of page
3. Observe post list

**Expected Results**:
- [ ] More posts load when scrolling near bottom
- [ ] Loading indicator shows while loading more posts
- [ ] New posts are appended to existing posts
- [ ] Scroll position is maintained

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-05-02: Verify Loading Indicator
**Steps**:
1. Navigate to All Posts tab with many posts (>20)
2. Scroll down to trigger load more
3. Observe loading indicator

**Expected Results**:
- [ ] Loading indicator shows while loading more posts
- [ ] Loading indicator shows "Loading more posts..." text or spinner
- [ ] Loading indicator is positioned at bottom of post list
- [ ] Loading indicator follows existing UI patterns

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-05-03: Verify Load Stop
**Steps**:
1. Navigate to All Posts tab with many posts (>20)
2. Scroll down to load all posts
3. Continue scrolling past all posts
4. Observe post list

**Expected Results**:
- [ ] Loading stops when no more posts available
- [ ] Loading indicator is hidden when not loading
- [ ] No more posts are loaded
- [ ] hasMore flag is set to false

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-05-04: Verify Pagination Reset on Filter Change
**Steps**:
1. Navigate to All Posts tab with many posts (>20)
2. Scroll down to load multiple pages
3. Change status filter
4. Observe post list

**Expected Results**:
- [ ] Pagination resets when filter changes
- [ ] Page is reset to 1
- [ ] Posts are reloaded with new filter parameters
- [ ] User sees updated results immediately

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-05-05: Verify Pagination Reset on Sort Change
**Steps**:
1. Navigate to All Posts tab with many posts (>20)
2. Scroll down to load multiple pages
3. Change sort option
4. Observe post list

**Expected Results**:
- [ ] Pagination resets when sort changes
- [ ] Page is reset to 1
- [ ] Posts are reloaded with new sort parameters
- [ ] User sees updated results immediately

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-05-06: Verify Pagination Reset on Search Change
**Steps**:
1. Navigate to All Posts tab with many posts (>20)
2. Scroll down to load multiple pages
3. Type a search query
4. Observe post list

**Expected Results**:
- [ ] Pagination resets when search changes
- [ ] Page is reset to 1
- [ ] Posts are reloaded with new search parameters
- [ ] User sees updated results immediately

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-05-07: Verify No Simultaneous Loads
**Steps**:
1. Navigate to All Posts tab with many posts (>20)
2. Scroll down rapidly to trigger multiple loads
3. Observe post list

**Expected Results**:
- [ ] Multiple simultaneous loads are prevented
- [ ] Only one load request is active at a time
- [ ] loadingMore flag prevents duplicate loads
- [ ] Posts are loaded correctly without duplicates

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

## Task 05-06: API Endpoint Testing

### Test Case 05-06-01: Verify GET /api/projects/{project_id}/posts Endpoint
**Steps**:
1. Use curl or Postman to call GET /api/projects/{project_id}/posts
2. Observe response

**Expected Results**:
- [ ] API endpoint returns 200 OK
- [ ] Response includes posts array
- [ ] Response includes total count
- [ ] Response format is correct

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-06-02: Verify Pagination Parameters
**Steps**:
1. Call GET /api/projects/{project_id}/posts?page=1&limit=20
2. Call GET /api/projects/{project_id}/posts?page=2&limit=20
3. Observe responses

**Expected Results**:
- [ ] Pagination works correctly (page, limit)
- [ ] Page 1 returns first 20 posts
- [ ] Page 2 returns next 20 posts
- [ ] Total count is consistent across pages

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-06-03: Verify Status Filter Parameter
**Steps**:
1. Call GET /api/projects/{project_id}/posts?status=published
2. Call GET /api/projects/{project_id}/posts?status=draft
3. Observe responses

**Expected Results**:
- [ ] Filter works correctly (status)
- [ ] status=published returns only published posts
- [ ] status=draft returns only draft posts
- [ ] No status parameter returns all posts

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-06-04: Verify Sort Parameter
**Steps**:
1. Call GET /api/projects/{project_id}/posts?sort_by=date-desc
2. Call GET /api/projects/{project_id}/posts?sort_by=date-asc
3. Call GET /api/projects/{project_id}/posts?sort_by=title-asc
4. Observe responses

**Expected Results**:
- [ ] Sort works correctly (sort_by)
- [ ] sort_by=date-desc returns newest first
- [ ] sort_by=date-asc returns oldest first
- [ ] sort_by=title-asc returns A-Z order

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-06-05: Verify Search Parameter
**Steps**:
1. Call GET /api/projects/{project_id}/posts?search=test
2. Call GET /api/projects/{project_id}/posts?search=example
3. Observe responses

**Expected Results**:
- [ ] Search works correctly (search)
- [ ] Search filters by title
- [ ] Search is case-insensitive
- [ ] Empty search returns all posts

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-06-06: Verify Combined Parameters
**Steps**:
1. Call GET /api/projects/{project_id}/posts?page=1&limit=20&status=published&sort_by=date-desc&search=test
2. Observe response

**Expected Results**:
- [ ] All parameters work together
- [ ] Results are filtered by status
- [ ] Results are sorted by date-desc
- [ ] Results are searched by title
- [ ] Pagination is applied

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-06-07: Verify Error Handling
**Steps**:
1. Call GET /api/projects/{invalid_id}/posts
2. Call GET /api/projects/{project_id}/posts with invalid parameters
3. Observe responses

**Expected Results**:
- [ ] Errors are handled correctly
- [ ] Invalid project_id returns 404
- [ ] Invalid parameters return 400
- [ ] Error messages are descriptive

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

## Task 05-07: Performance Testing

### Test Case 05-07-01: Verify Load Time for Small Project
**Steps**:
1. Navigate to a project with <200 posts
2. Measure load time for All Posts tab
3. Observe performance

**Expected Results**:
- [ ] All Posts tab loads within 2 seconds for projects with <200 posts
- [ ] Initial load is fast
- [ ] No noticeable lag

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-07-02: Verify Infinite Scroll Performance
**Steps**:
1. Navigate to All Posts tab with many posts (>20)
2. Scroll down to load multiple pages
3. Observe performance

**Expected Results**:
- [ ] Infinite scroll is smooth with no noticeable lag
- [ ] Loading indicator appears quickly
- [ ] Posts load without blocking UI
- [ ] Scroll performance is maintained

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-07-03: Verify Filter/Sort/Search Performance
**Steps**:
1. Navigate to All Posts tab with many posts (>20)
2. Apply different filters
3. Apply different sorts
4. Type search queries
5. Observe performance

**Expected Results**:
- [ ] Filter operations are fast
- [ ] Sort operations are fast
- [ ] Search operations are fast
- [ ] No noticeable lag when changing filters/sorts/search

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

## Task 05-08: Cross-Browser Testing

### Test Case 05-08-01: Verify Chrome Compatibility
**Steps**:
1. Open application in Chrome
2. Navigate to All Posts tab
3. Test all functionality

**Expected Results**:
- [ ] All functionality works in Chrome
- [ ] UI renders correctly
- [ ] All interactions work as expected
- [ ] No console errors

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-08-02: Verify Firefox Compatibility
**Steps**:
1. Open application in Firefox
2. Navigate to All Posts tab
3. Test all functionality

**Expected Results**:
- [ ] All functionality works in Firefox
- [ ] UI renders correctly
- [ ] All interactions work as expected
- [ ] No console errors

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-08-03: Verify Safari Compatibility
**Steps**:
1. Open application in Safari (if available)
2. Navigate to All Posts tab
3. Test all functionality

**Expected Results**:
- [ ] All functionality works in Safari
- [ ] UI renders correctly
- [ ] All interactions work as expected
- [ ] No console errors

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

### Test Case 05-08-04: Verify Edge Compatibility
**Steps**:
1. Open application in Edge (if available)
2. Navigate to All Posts tab
3. Test all functionality

**Expected Results**:
- [ ] All functionality works in Edge
- [ ] UI renders correctly
- [ ] All interactions work as expected
- [ ] No console errors

**Actual Results**: _To be filled during testing_

**Status**: _Pending_

---

## Summary

### Test Results Overview
- **Total Test Cases**: 37
- **Passed**: _To be filled_
- **Failed**: _To be filled_
- **Pending**: _To be filled_

### Issues Found
_List any issues found during testing_

### Recommendations
_List any recommendations for improvements_

### Notes
_Add any additional notes or observations_
