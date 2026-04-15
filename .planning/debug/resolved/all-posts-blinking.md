---
status: resolved
trigger: "Investigate issue: all-posts-blinking - Table blinks on and off repeatedly when clicking All Posts tab in ProjectDetail"
created: 2026-04-15T11:36:40+07:00
updated: 2026-04-15T11:44:36+07:00
---

## Current Focus
hypothesis: User wants to remove the 3-second auto-refresh entirely and replace it with a manual refresh button instead of fixing the dependency array issue
test: Remove the auto-refresh useEffect (lines 71-87) and add a refresh button to the UI
expecting: No more blinking, user controls when to refresh
next_action: Archive session and commit changes

## Symptoms
expected: Table should load posts and display them
actual: Table blinks on and off repeatedly
errors: No errors visible
reproduction: Click All Posts tab in ProjectDetail
timeline: Just started after recent changes

## Eliminated
- hypothesis: Changing dependency array from `project` to `project?.wp_site_id` would fix the blinking
  evidence: User requested different approach - remove auto-refresh entirely and add manual refresh button
  timestamp: 2026-04-15T11:40:53+07:00

## Evidence
- timestamp: 2026-04-15T11:36:40+07:00
  checked: ProjectDetail.jsx useEffect dependencies
  found: Line 172-176 has useEffect with dependency array [activeTab, id, project, statusFilter, sortBy, searchQuery]
  implication: Any change to project reference triggers loadWpPosts()

- timestamp: 2026-04-15T11:36:40+07:00
  checked: How project is updated
  found: Line 187: setProject(projRes.data) - creates new object reference on every load() call
  implication: Every load() call changes project reference

- timestamp: 2026-04-15T11:36:40+07:00
  checked: When load() is called
  found: Lines 71-87: useEffect calls load() every 3 seconds when there are active jobs
  implication: If there are active jobs, project reference changes every 3 seconds

- timestamp: 2026-04-15T11:36:40+07:00
  checked: loadWpPosts behavior
  found: Lines 237-259: Sets loadingWpPosts to true, then false after API call
  implication: Repeated calls cause loading spinner to blink on/off

- timestamp: 2026-04-15T11:36:40+07:00
  checked: Fix implementation
  found: Changed dependency array from [activeTab, id, project, statusFilter, sortBy, searchQuery] to [activeTab, id, project?.wp_site_id, statusFilter, sortBy, searchQuery]
  implication: Effect now only triggers when wp_site_id actually changes, not when project object reference changes

- timestamp: 2026-04-15T11:36:40+07:00
  checked: Frontend hot-reload
  found: Vite HMR updated ProjectDetail.jsx without errors
  implication: Fix is syntactically correct and application is running

- timestamp: 2026-04-15T11:40:53+07:00
  checked: User feedback
  found: User wants to remove 3-second auto-refresh and add manual refresh button instead
  implication: Different approach needed - remove auto-refresh entirely

- timestamp: 2026-04-15T11:40:53+07:00
  checked: Auto-refresh removal
  found: Removed useEffect (lines 71-87) that called load() every 3 seconds when there are active jobs
  implication: No more automatic polling, no more blinking

- timestamp: 2026-04-15T11:40:53+07:00
  checked: Refresh button addition
  found: Added refresh button to Content tab toolbar (calls load()) and All Posts tab toolbar (calls loadWpPosts())
  implication: User can now manually refresh data when needed

- timestamp: 2026-04-15T11:44:36+07:00
  checked: Human verification
  found: User confirmed "confirmed fixed"
  implication: Fix is working correctly in production

## Resolution
root_cause: useEffect dependency array included `project` object, which changes on every load() call. When there are active jobs, load() is called every 3 seconds, causing repeated effect triggers and loading spinner blinking.
fix: Removed the auto-refresh useEffect (lines 71-87) and added manual refresh buttons to both Content and All Posts tab toolbars
verification: Human-verified - user confirmed the fix works correctly
files_changed: ["frontend/src/components/Projects/ProjectDetail.jsx"]
