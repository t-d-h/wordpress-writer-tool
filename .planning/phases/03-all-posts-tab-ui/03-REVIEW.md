---
phase: 03-all-posts-tab-ui
reviewed: 2026-04-14T20:17:55+07:00
depth: standard
files_reviewed: 8
files_reviewed_list:
  - backend/app/models/post.py
  - backend/app/routers/posts.py
  - backend/app/routers/projects.py
  - backend/app/services/post_sync_service.py
  - frontend/src/api/client.js
  - frontend/src/components/Projects/PostCard.jsx
  - frontend/src/components/Projects/ProjectDetail.jsx
  - frontend/src/index.css
findings:
  critical: 2
  warning: 5
  info: 3
  total: 10
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-04-14T20:17:55+07:00
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed 8 source files implementing the "All Posts" tab UI feature. The implementation adds filtering, sorting, search, and pagination for posts within a project. Overall code quality is acceptable, but several issues were identified including incorrect pagination logic, potential security vulnerabilities, and missing error handling.

## Critical Issues

### CR-01: Incorrect total count in pagination response

**File:** `backend/app/routers/posts.py:71`
**Issue:** The `total` field in the response returns the count of posts on the current page, not the total count of all posts matching the query. This breaks pagination UI logic that relies on accurate total counts.

**Fix:**
```python
@router.get("/by-project/{project_id}")
async def list_posts_by_project(
    project_id: str, page: int = Query(1, ge=1), limit: int = Query(100, ge=1, le=100)
):
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get total count first
    total = await posts_col.count_documents({"project_id": project_id})

    posts = []
    skip = (page - 1) * limit
    async for doc in (
        posts_col.find({"project_id": project_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    ):
        posts.append(format_post(doc))
    return {"posts": posts, "total": total}
```

### CR-02: Regex injection vulnerability in search

**File:** `backend/app/routers/projects.py:177`
**Issue:** The search filter directly passes user input to MongoDB regex without escaping. This allows users to inject arbitrary regex patterns, potentially causing denial of service through catastrophic backtracking or exposing sensitive data.

**Fix:**
```python
# Apply search filter if provided (case-insensitive title search)
if search:
    # Escape special regex characters to prevent injection
    import re
    escaped_search = re.escape(search)
    query_filter["title"] = {"$regex": escaped_search, "$options": "i"}
```

## Warnings

### WR-01: Missing ObjectId validation could cause crashes

**File:** `backend/app/routers/projects.py:164`
**Issue:** The `ObjectId(project_id)` conversion is not wrapped in a try/except block. If an invalid ObjectId string is passed, the application will crash with an unhandled exception.

**Fix:**
```python
@router.get("/{project_id}/posts")
async def get_all_posts(
    project_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    sort_by: str = Query(
        "date-desc", regex="^(date-desc|date-asc|title-asc|title-desc|status)$"
    ),
    search: Optional[str] = Query(None),
):
    """Get all posts for a project with filter, sort, and search support."""
    try:
        project_id_obj = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project ID")

    # Verify project exists
    project = await projects_col.find_one({"_id": project_id_obj})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # ... rest of the function
```

### WR-02: Unhandled promise rejection in getProjectTokenUsage

**File:** `frontend/src/api/client.js:41`
**Issue:** The `getProjectTokenUsage` function uses `.then()` without error handling. If the request fails, the promise rejection will be unhandled, potentially causing runtime errors.

**Fix:**
```javascript
export const getProjectTokenUsage = (id) =>
  getProjectStats(id)
    .then(res => {
      if (!res.data || !res.data.token_usage) {
        throw new Error('Invalid response format');
      }
      return res.data.token_usage;
    })
    .catch(err => {
      console.error('Failed to get token usage:', err);
      throw err; // Re-throw to allow caller to handle
    });
```

### WR-03: Missing null check in PostCard date formatting

**File:** `frontend/src/components/Projects/PostCard.jsx:37`
**Issue:** The `formatDate` function is called with `post.created_at || post.updated_at`, but if both are null/undefined, it will pass `undefined` to `new Date()`, which results in "Invalid Date" being displayed.

**Fix:**
```javascript
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return 'N/A'
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch (e) {
    return 'N/A'
  }
}
```

### WR-04: Exposing internal error details to clients

**File:** `backend/app/routers/posts.py:602`
**Issue:** The exception handler returns `str(e)` directly to the client, which may expose internal implementation details, file paths, or other sensitive information.

**Fix:**
```python
except Exception as e:
    # Log the full error for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to update thumbnail to WordPress: {e}", exc_info=True)
    raise HTTPException(
        status_code=500,
        detail="Failed to upload thumbnail to WordPress"
    )
```

### WR-05: Potential null reference in ProjectDetail

**File:** `frontend/src/components/Projects/ProjectDetail.jsx:690`
**Issue:** The `onEdit` callback checks `post.wp_post_id && project.wp_site_url` but doesn't validate that `project` is defined before accessing `project.wp_site_url`. If `project` is null, this will cause a runtime error.

**Fix:**
```javascript
onEdit={(post) => {
  if (post?.wp_post_id && project?.wp_site_url) {
    window.open(`${project.wp_site_url}/wp-admin/post.php?post=${post.wp_post_id}&action=edit`, '_blank')
  }
}}
```

## Info

### IN-01: Inconsistent error handling pattern

**File:** `backend/app/routers/posts.py:328`
**Issue:** Using `print()` for logging instead of a proper logging framework. The codebase uses `print()` in some places and `logger` in others, making it inconsistent.

**Fix:** Replace with proper logging:
```python
import logging
logger = logging.getLogger(__name__)

# In the catch block:
logger.warning(f"Failed to update WordPress post: {e}")
```

### IN-02: Unused import in PostCard

**File:** `frontend/src/components/Projects/PostCard.jsx:1`
**Issue:** The `PropTypes` import is used at the bottom of the file for prop validation, which is good practice. However, this is noted for completeness as the import is actually used.

**Fix:** No action needed - this is correct usage.

### IN-03: Magic number for pagination limit

**File:** `frontend/src/components/Projects/ProjectDetail.jsx:284`
**Issue:** The pagination limit of 20 is hardcoded in multiple places. This should be a constant for maintainability.

**Fix:**
```javascript
const POSTS_PER_PAGE = 20

// Then use:
const response = await getProjectPosts(id, pageNum, POSTS_PER_PAGE, statusFilter === 'all' ? null : statusFilter, sortBy, searchQuery || null)
// And:
setHasMore(newPosts.length >= POSTS_PER_PAGE)
```

---

_Reviewed: 2026-04-14T20:17:55+07:00_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
