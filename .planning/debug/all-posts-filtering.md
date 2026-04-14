---
status: investigating
trigger: "Investigate issue: all-posts-filtering"
created: 2026-04-14T22:03:58+07:00
updated: 2026-04-14T22:04:00+07:00
---

## Current Focus
hypothesis: The endpoint requires a project to exist for the site, but the get_wp_posts function actually fetches ALL posts from WordPress (not filtered by project)
test: Verify that get_wp_posts fetches all posts from WordPress REST API without project filtering
expecting: Confirm that the function correctly fetches all posts, and the issue is the router's project requirement
next_action: Check if there are any other filters or if the issue is different

## Symptoms
expected: The All Posts view should display all posts from the WordPress site, including posts created outside of this tool
actual: Only posts created through the WordPress Writer Tool are visible in the All Posts view
errors: No errors shown - the view loads but shows incomplete data
reproduction: Navigate to the All Posts section and observe the post list
started: This feature has never worked correctly since I started using the tool

## Eliminated

## Evidence
- timestamp: 2026-04-14T22:04:00+07:00
  checked: Frontend AllPosts.jsx component
  found: Component calls getSitePosts(siteId, 100, page, statusFilter) from API client
  implication: Frontend correctly requests posts by site ID

- timestamp: 2026-04-14T22:04:00+07:00
  checked: API client getSitePosts function
  found: Calls /api/wp-sites/${siteId}/posts endpoint
  implication: Backend endpoint is responsible for fetching posts

- timestamp: 2026-04-14T22:04:00+07:00
  checked: Backend router wp_sites.py get_site_posts endpoint
  found: Endpoint requires a project to exist: `project = await projects_col.find_one({"wp_site_id": site_id})`
  implication: If no project exists for the site, returns 404 error

- timestamp: 2026-04-14T22:04:00+07:00
  checked: wp_service.py get_wp_posts function
  found: Function fetches ALL posts from WordPress REST API: `url = f"{wp_site['url'].rstrip('/')}/wp-json/wp/v2/posts"`
  implication: The service function correctly fetches all posts, not filtered by project

## Resolution
root_cause:
fix:
verification:
files_changed: []
