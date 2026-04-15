---
phase: 05-data-transformation
plan: 01
subsystem: WordPress Integration
tags: [backend, data-transformation, wordpress-api]
dependency_graph:
  requires: []
  provides: [transformed-posts-data]
  affects: [frontend-all-posts-table]
tech_stack:
  added: []
  patterns: [data-transformation-layer, graceful-degradation]
key_files:
  created: []
  modified:
    - backend/app/services/wp_service.py
decisions: []
metrics:
  duration: "1m 7s"
  completed_date: "2026-04-14T16:41:25Z"
  tasks_completed: 4
  files_modified: 1
  lines_added: 127
  lines_removed: 0
requirements-completed:
  - DATA-01: WordPress REST API response is transformed to table format
  - DATA-02: Nested categories and tags from _embedded['wp:term'] are handled correctly
  - DATA-03: Dates are formatted for display
  - DATA-04: Edit URLs are generated for WordPress admin
---

# Phase 05 Plan 01: WordPress REST API Data Transformation Summary

Transform WordPress REST API responses into table-ready format in backend service layer, including extracting nested categories/tags, formatting dates, and generating edit URLs.

## One-Liner

Enhanced `get_wp_posts()` function with data transformation layer that extracts categories/tags from `_embedded`, formats dates to DD MMMM YYYY, and generates WordPress admin edit URLs, simplifying frontend by returning table-ready data.

## Implementation Summary

### Task 1: Add Transformation Helper Functions

Added four helper functions to `backend/app/services/wp_service.py`:

- **`_format_date(date_string: str) -> str`**: Formats WordPress ISO 8601 dates to DD MMMM YYYY format (e.g., "14 April 2026"). Handles invalid dates gracefully by returning empty string.

- **`_extract_categories(embedded: dict) -> list`**: Extracts category names from `_embedded['wp:term'][0]`. Returns empty array if `_embedded` is missing or structure is invalid.

- **`_extract_tags(embedded: dict) -> list`**: Extracts tag names from `_embedded['wp:term'][1]`. Returns empty array if `_embedded` is missing or structure is invalid.

- **`_generate_edit_url(site_url: str, post_id: int) -> str`**: Constructs full WordPress admin edit URL (e.g., `https://example.com/wp-admin/post.php?post=123&action=edit`). Returns empty string if parameters are invalid.

All helper functions include comprehensive error handling with try/except blocks and print() logging for debugging.

### Task 2: Transform Posts Data in get_wp_posts Function

Updated `get_wp_posts()` function to transform each post after fetching from WordPress API:

- Extracts categories using `_extract_categories(post._embedded)`
- Extracts tags using `_extract_tags(post._embedded)`
- Formats date using `_format_date(post.date)`
- Generates edit URL using `_generate_edit_url(wp_site['url'], post.id)`

Adds transformed fields to each post object:
- `categories`: array of category names
- `tags`: array of tag names
- `formatted_date`: formatted date string
- `edit_url`: full edit URL string

Original WordPress fields remain intact for backward compatibility. Returns transformed posts with total count.

### Task 3: Add Error Handling for Missing or Invalid Data

Enhanced error handling across all transformation functions:

- **`_format_date()`**: Validates input is not None/empty, handles parsing errors with try/except
- **`_extract_categories()`**: Validates `_embedded` exists, checks `wp:term` has at least 1 element, validates `wp:term[0]` exists
- **`_extract_tags()`**: Validates `_embedded` exists, checks `wp:term` has at least 2 elements, validates `wp:term[1]` exists
- **`_generate_edit_url()`**: Validates `site_url` and `post_id` are not None/empty

Wrapped transformation loop in `get_wp_posts()` with try/except block. Logs errors with print() for debugging. Returns original posts if transformation fails (graceful degradation).

### Task 4: Verify Transformation Output Structure

Verified transformation output structure matches frontend expectations:

- Each transformed post has required fields: `categories`, `tags`, `formatted_date`, `edit_url`
- Response structure remains compatible: dict with `'posts'` list and `'total'` count
- Original WordPress fields retained (title.rendered, link, status, etc.)
- New fields added alongside existing fields (not replacing)

Tested edge cases:
- Post with categories and tags: data extracted correctly
- Post with missing `_embedded`: empty arrays returned
- Post with invalid date: empty string returned
- Post with missing post_id: empty string returned

## Deviations from Plan

None - plan executed exactly as written.

## Threat Flags

None - no new security-relevant surface introduced beyond what was documented in the threat model.

## Commits

| Commit | Hash | Message |
|--------|------|---------|
| Task 1 | d0b737c | feat(05-01): add transformation helper functions to wp_service.py |
| Task 2 | 0f199e2 | feat(05-01): transform posts data in get_wp_posts function |
| Task 3 | 0d28afc | feat(05-01): add error handling for transformation logic |

## Files Modified

- `backend/app/services/wp_service.py` (127 lines added)

## Key Changes

### Added Helper Functions

```python
def _format_date(date_string: str) -> str:
    """Format WordPress date string to DD MMMM YYYY format."""
    if not date_string:
        return ""
    try:
        dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        return dt.strftime("%d %B %Y")
    except Exception as e:
        print(f"[FORMAT_DATE_ERROR] Failed to format date '{date_string}': {str(e)}")
        return ""

def _extract_categories(embedded: dict) -> list:
    """Extract category names from WordPress _embedded data."""
    if not embedded:
        return []
    try:
        wp_terms = embedded.get("wp:term", [])
        if len(wp_terms) < 1 or not wp_terms[0]:
            return []
        return [term.get("name", "") for term in wp_terms[0] if term.get("name")]
    except Exception as e:
        print(f"[EXTRACT_CATEGORIES_ERROR] Failed to extract categories: {str(e)}")
        return []

def _extract_tags(embedded: dict) -> list:
    """Extract tag names from WordPress _embedded data."""
    if not embedded:
        return []
    try:
        wp_terms = embedded.get("wp:term", [])
        if len(wp_terms) < 2 or not wp_terms[1]:
            return []
        return [term.get("name", "") for term in wp_terms[1] if term.get("name")]
    except Exception as e:
        print(f"[EXTRACT_TAGS_ERROR] Failed to extract tags: {str(e)}")
        return []

def _generate_edit_url(site_url: str, post_id: int) -> str:
    """Generate WordPress admin edit URL for a post."""
    if not site_url or not post_id:
        return ""
    try:
        base_url = site_url.rstrip("/")
        return f"{base_url}/wp-admin/post.php?post={post_id}&action=edit"
    except Exception as e:
        print(f"[GENERATE_EDIT_URL_ERROR] Failed to generate edit URL: {str(e)}")
        return ""
```

### Updated get_wp_posts Function

```python
async def get_wp_posts(
    project_id: str,
    per_page: int = 100,
    page: int = 1,
    status: str = None,
    search: str = None,
    orderby: str = "date",
    order: str = "desc",
) -> dict:
    """Fetch posts from WordPress REST API with filtering and search."""
    # ... existing code ...

    result = await fetch_with_retry(url, headers, params)

    # Transform posts data for frontend consumption
    transformed_posts = []
    try:
        for post in result.get("posts", []):
            # Extract nested data from _embedded
            embedded = post.get("_embedded", {})
            categories = _extract_categories(embedded)
            tags = _extract_tags(embedded)

            # Format date and generate edit URL
            formatted_date = _format_date(post.get("date"))
            edit_url = _generate_edit_url(wp_site["url"], post.get("id"))

            # Add transformed fields to post (keep original fields intact)
            post["categories"] = categories
            post["tags"] = tags
            post["formatted_date"] = formatted_date
            post["edit_url"] = edit_url

            transformed_posts.append(post)
    except Exception as e:
        print(f"[TRANSFORM_ERROR] Failed to transform posts: {str(e)}")
        # Return original posts if transformation fails
        transformed_posts = result.get("posts", [])

    return {"posts": transformed_posts, "total": result.get("total", 0)}
```

## Success Criteria

- [x] WordPress REST API response is transformed to table format with all required fields
- [x] Nested categories and tags from `_embedded['wp:term']` are extracted correctly
- [x] Dates are formatted for display in table (DD MMMM YYYY format)
- [x] Edit URLs are generated for WordPress admin
- [x] Error handling provides graceful degradation for missing data

## Next Steps

The transformed data is now ready for consumption by the frontend All Posts table component. The next phase should update the frontend to use the new transformed fields instead of performing transformation logic in the React components.

## Self-Check: PASSED

- [x] SUMMARY.md file created at `.planning/phases/05-data-transformation/05-01-SUMMARY.md`
- [x] Commit d0b737c exists (Task 1: transformation helper functions)
- [x] Commit 0f199e2 exists (Task 2: transform posts data)
- [x] Commit 0d28afc exists (Task 3: error handling)
- [x] Modified file `backend/app/services/wp_service.py` exists
- [x] Helper functions (_format_date, _extract_categories, _extract_tags, _generate_edit_url) present
- [x] Transformation logic present in get_wp_posts function
- [x] Error handling present with TRANSFORM_ERROR logging
