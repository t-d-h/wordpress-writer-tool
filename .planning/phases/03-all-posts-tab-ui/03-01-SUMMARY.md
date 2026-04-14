---
phase: 03-all-posts-tab-ui
plan: 01
subsystem: frontend
tags: [react, tabs, ui]
dependency_graph:
  requires:
    - phase: 02
      plan: WordPress Integration Backend
      reason: Provides post sync endpoints and origin field
  provides:
    - component: PostCard
      description: Reusable card component for displaying WordPress posts
    - feature: All Posts Tab
      description: Third tab in ProjectDetail showing all WordPress posts
  affects:
    - file: frontend/src/components/Projects/ProjectDetail.jsx
      description: Added All Posts tab and integration
    - file: frontend/src/components/Projects/PostCard.jsx
      description: New component for post display
    - file: frontend/src/index.css
      description: Added styling for PostCard component
tech_stack:
  added: []
  patterns:
    - Card-based layout for post display
    - Grid layout for post cards
    - Badge pattern for origin distinction
    - Loading/error/empty state pattern
key_files:
  created:
    - frontend/src/components/Projects/PostCard.jsx
  modified:
    - frontend/src/components/Projects/ProjectDetail.jsx
    - frontend/src/index.css
decisions:
  - decision: Use existing stat-card CSS class for PostCard styling
    rationale: Maintains consistency with existing UI patterns
  - decision: Fetch posts when tab becomes active (not on component mount)
    rationale: Avoids unnecessary API calls when tab is not viewed
  - decision: Use window.open() for WordPress admin edit link
    rationale: Opens in new tab, keeping user context in the app
metrics:
  duration: PT10M
  completed_date: 2026-04-14T16:05:18+07:00
---

# Phase 03 Plan 01: Add All Posts Tab to ProjectDetail Summary

Implemented "All Posts" tab in ProjectDetail component to display all WordPress posts for a project with visual distinction between tool-created and existing posts.

## What Was Built

### 1. All Posts Tab Integration
Added "All Posts" as the third tab in ProjectDetail component (after General and Content tabs). The tab follows the existing tab pattern and displays all WordPress posts associated with the project.

### 2. PostCard Component
Created a reusable PostCard component that displays essential post information:
- Post title with truncation for long titles
- Status badge (draft, published, etc.)
- Formatted date (created_at or updated_at)
- Origin badge distinguishing "Tool" vs "Existing" posts
- Edit button that opens WordPress admin edit page in new tab

### 3. Post Fetching and State Management
Implemented state management for the All Posts tab:
- `allPosts` state for storing fetched posts
- `loadingAllPosts` state for loading indicator
- `allPostsError` state for error handling
- `loadAllPosts()` function to fetch posts from backend
- useEffect hook to load posts when tab becomes active

### 4. UI States
Implemented comprehensive UI states for the All Posts tab:
- Loading spinner while fetching posts
- Error message display if fetch fails
- "No posts yet" message when no posts exist
- Grid layout of PostCard components when posts are available

## Deviations from Plan

None - plan executed exactly as written.

## Implementation Details

### Tab Navigation
The "All Posts" button was added to the existing tab navigation in ProjectDetail.jsx, following the same pattern as the General and Content tabs.

### PostCard Component
The PostCard component uses the existing `stat-card` CSS class for consistent styling. Additional CSS classes were added for:
- `post-card` - Main card layout
- `post-card-header` - Header section with origin badge and status
- `origin-badge` - Badge for tool vs existing distinction
- `post-card-title` - Post title with truncation
- `post-card-meta` - Metadata section with date

### Data Fetching
Posts are fetched using the existing `getPostsByProject` API endpoint, which returns all posts for a project including both tool-created and existing WordPress posts. The `origin` field distinguishes between the two types.

### Edit Functionality
The Edit button opens the WordPress admin edit page in a new tab using `window.open()`. The URL format is: `{wp_site_url}/wp-admin/post.php?post={wp_post_id}&action=edit`

## Success Criteria Met

- [x] User can view "All Posts" tab in each project
- [x] System displays all WordPress posts (both tool-created and existing)
- [x] System provides visual distinction between tool-created and existing posts (badge)
- [x] User can click Edit button to open WordPress admin edit page in new tab
- [x] System displays post name/title, status, date
- [x] Tab follows existing pattern and styling

## Known Limitations

The following features are listed in requirements but not implemented in this plan (deferred to future plans):
- POSTS-06: System displays post URL
- POSTS-07: System displays post categories
- POSTS-08: System displays post tags

These were not included in the task list or success criteria for this plan.

## Files Modified

1. **frontend/src/components/Projects/ProjectDetail.jsx**
   - Added "All Posts" tab button to navigation
   - Added All Posts tab section with PostCard grid
   - Added state for posts, loading, and error
   - Added loadAllPosts() function
   - Added useEffect to load posts when tab is active

2. **frontend/src/components/Projects/PostCard.jsx** (new file)
   - Created PostCard component with title, status, date, origin badge, edit button
   - Implemented null/undefined post handling
   - Added PropTypes for component props

3. **frontend/src/index.css**
   - Added post-card CSS classes
   - Added origin-badge styling for tool vs existing distinction
   - Added post-card-title, post-card-meta, post-card-date styling

## Testing Notes

The implementation can be tested by:
1. Navigating to a project detail page
2. Clicking the "All Posts" tab
3. Verifying that posts are displayed in a grid layout
4. Checking that tool-created posts show "Tool" badge
5. Checking that existing posts show "Existing" badge
6. Clicking the Edit button to verify it opens WordPress admin in new tab
7. Testing loading state by refreshing the tab
8. Testing error state by simulating API failure
9. Testing empty state by viewing a project with no posts

## Self-Check: PASSED

All files created and commits verified:
- ✅ .planning/phases/03-all-posts-tab-ui/03-01-SUMMARY.md
- ✅ frontend/src/components/Projects/PostCard.jsx
- ✅ Commit e985906: feat(03-01): add All Posts tab to ProjectDetail component
- ✅ Commit 3c0a170: feat(03-01): create PostCard component
- ✅ Commit f5777b7: feat(03-01): integrate PostCard into All Posts tab
- ✅ Commit 115e99a: feat(03-01): add CSS styling for PostCard component
