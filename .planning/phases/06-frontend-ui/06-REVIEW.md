---
phase: 06-frontend-ui
reviewed: 2026-04-15T09:56:46+07:00
depth: standard
files_reviewed: 3
files_reviewed_list:
  - frontend/src/api/client.js
  - frontend/src/components/AllPosts.jsx
  - frontend/src/index.css
findings:
  critical: 0
  warning: 8
  info: 2
  total: 10
status: issues_found
---

# Phase 06: Code Review Report

**Reviewed:** 2026-04-15T09:56:46+07:00
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Reviewed three frontend source files: API client, AllPosts component, and CSS design system. The codebase follows React best practices with proper error handling in most areas. However, several issues were identified including missing null checks, hardcoded values, and potential runtime errors from invalid date parsing. No critical security vulnerabilities were found, but there are areas where defensive programming could prevent crashes.

## Warnings

### WR-01: Missing null check in getEditUrl function

**File:** `frontend/src/components/AllPosts.jsx:86-89`
**Issue:** The `getEditUrl` function accesses `selectedSite.url` without checking if `selectedSite` is null or if `url` property exists. This will throw an error if called when no site is selected.
**Fix:**
```javascript
const getEditUrl = (postId) => {
  if (!selectedSite?.url) return '#'
  const baseUrl = selectedSite.url.replace(/\/$/, '')
  return `${baseUrl}/wp-admin/post.php?post=${postId}&action=edit`
}
```

### WR-02: Invalid date parsing without error handling

**File:** `frontend/src/components/AllPosts.jsx:82-84`
**Issue:** The `formatDate` function creates a Date object without validating the input. If `dateString` is invalid or null, this will throw an error and crash the component.
**Fix:**
```javascript
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '-'
  return date.toLocaleDateString()
}
```

### WR-03: Unhandled undefined site selection

**File:** `frontend/src/components/AllPosts.jsx:119-120`
**Issue:** When a site is not found in the sites array, `find()` returns `undefined`, which is then set as `selectedSite`. This could cause issues downstream when accessing `selectedSite.id` or `selectedSite.url`.
**Fix:**
```javascript
onChange={(e) => {
  const site = sites.find(s => s.id === e.target.value)
  if (site) {
    setSelectedSite(site)
    setPage(1)
  }
}}
```

### WR-04: Hardcoded pagination value

**File:** `frontend/src/components/AllPosts.jsx:52, 255, 265, 270`
**Issue:** The value `100` is hardcoded in multiple places for pagination (perPage parameter, pagination display, and page calculation). This should be a constant to ensure consistency and make it easier to change.
**Fix:**
```javascript
const POSTS_PER_PAGE = 100

// Then use POSTS_PER_PAGE instead of 100 in:
// - getSitePosts call (line 52)
// - Pagination display (line 255, 265, 270)
```

### WR-05: Missing error handling in getProjectTokenUsage

**File:** `frontend/src/api/client.js:42`
**Issue:** The `getProjectTokenUsage` function assumes `res.data.token_usage` exists without error handling. If the API response structure changes or returns an error, this will fail.
**Fix:**
```javascript
export const getProjectTokenUsage = (id) =>
  api.get(`/projects/${id}/stats`)
    .then(res => res.data?.token_usage || {})
    .catch(err => {
      console.error('Failed to get token usage:', err)
      return {}
    })
```

### WR-06: Inconsistent parameter naming in publishPost

**File:** `frontend/src/api/client.js:60`
**Issue:** The function parameter uses camelCase `forcePublish` but the API payload uses snake_case `force_publish`. This inconsistency is confusing and error-prone.
**Fix:**
```javascript
// Either change the parameter name to match the API:
export const publishPost = (id, force_publish = false) =>
  api.post(`/posts/${id}/publish`, { force_publish })

// Or document the transformation clearly:
export const publishPost = (id, forcePublish = false) =>
  api.post(`/posts/${id}/publish`, { force_publish: forcePublish })
```

### WR-07: Unsafe HTML rendering in post title

**File:** `frontend/src/components/AllPosts.jsx:223`
**Issue:** The `post.title.rendered` field from WordPress API may contain HTML. Rendering it directly without sanitization could lead to XSS if the WordPress site is compromised.
**Fix:**
```javascript
// Option 1: Use dangerouslySetInnerHTML with caution
<td style={{ fontWeight: 600 }} dangerouslySetInnerHTML={{ __html: post.title.rendered || '(Untitled)' }}></td>

// Option 2: Strip HTML and use plain text (safer)
<td style={{ fontWeight: 600 }}>{post.title.rendered?.replace(/<[^>]*>/g, '') || '(Untitled)'}</td>
```

### WR-08: Assumption about WordPress API response structure

**File:** `frontend/src/components/AllPosts.jsx:229-230`
**Issue:** The code assumes `post._embedded['wp:term'][0]` contains categories and `[1]` contains tags. This structure may vary depending on WordPress API version or configuration.
**Fix:**
```javascript
const getCategoryNames = (categories) => {
  if (!categories || !Array.isArray(categories) || categories.length === 0) return '-'
  return categories.map(c => c.name).join(', ')
}

const getTagNames = (tags) => {
  if (!tags || !Array.isArray(tags) || tags.length === 0) return '-'
  return tags.map(t => t.name).join(', ')
}

// In the render, add defensive checks:
<td style={{ fontSize: '13px' }}>{getCategoryNames(post._embedded?.['wp:term']?.[0])}</td>
<td style={{ fontSize: '13px' }}>{getTagNames(post._embedded?.['wp:term']?.[1])}</td>
```

## Info

### IN-01: Duplicate animation keyframe definition

**File:** `frontend/src/index.css:1158-1166`
**Issue:** The `@keyframes pulse` animation is defined twice (lines 1158-1161 and 1163-1166) with identical content. This is redundant code.
**Fix:** Remove the duplicate definition at lines 1163-1166.

### IN-02: Unused CSS class

**File:** `frontend/src/index.css:807-814`
**Issue:** The `.file-upload` class is defined with hover and active states, but this class is not used in any of the reviewed components. It may be dead code or used in components not in this review scope.
**Fix:** If unused, remove the class definition. If used in other components, consider moving it to a component-specific CSS file.

---

_Reviewed: 2026-04-15T09:56:46+07:00_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
