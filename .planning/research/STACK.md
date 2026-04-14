# Technology Stack

**Project:** WordPress Writer Tool — All Posts Table View in ProjectDetail
**Researched:** 2026-04-14
**Mode:** Ecosystem (feature-specific stack additions)

## Executive Summary

**No new libraries required.** The existing stack already supports all functionality needed for the table view feature. AllPosts.jsx demonstrates a working table implementation using only existing dependencies. The only changes needed are:

1. **Backend:** Expose existing `search`, `orderby`, and `order` parameters in the router endpoint
2. **Frontend:** Update API client and ProjectDetail.jsx to use table layout with search/sort/filter
3. **Dependencies:** Add `httpx` to requirements.txt (currently used but not listed)

## Recommended Stack

### Core Framework (No Changes)
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| React | 18.3.1 | Frontend UI framework | Already in use, stable, supports all needed features |
| FastAPI | 0.115.0 | Backend REST API framework | Already in use, async support for WordPress API calls |

### Data Layer (No Changes)
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| MongoDB | 7.x | Project and post metadata storage | Already in use, no changes needed |
| Redis | 7.x | Job queue and pub/sub | Already in use, no changes needed |

### HTTP Clients (Add to requirements.txt)
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| httpx | >=0.28.1 | Async HTTP client for WordPress REST API | **Already in use** but missing from requirements.txt. Required for `wp_service.py` to make WordPress API calls. |

### Frontend Libraries (No Changes)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| axios | 1.14.0 | HTTP client for API communication | Already in use, no changes needed |
| react-icons | 5.6.0 | Icon library (HiOutlinePencil, HiOutlineArrowPath) | Already in use, icons needed for table actions |
| react-router-dom | 7.14.0 | Client-side routing | Already in use, no changes needed |

### CSS/Styling (No Changes)
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| CSS Custom Properties | - | Design system with CSS variables | Already in use, table styling exists (lines 558-602) |
| Plain HTML Tables | - | Table layout for posts | No table library needed — plain HTML tables work fine |

## Stack Additions Required

### Backend (Python)

**Add to requirements.txt:**
```txt
httpx>=0.28.1
```

**Rationale:** `httpx` is already imported and used in `wp_service.py` and `image_service.py` but is not listed in requirements.txt. This is a dependency gap that should be fixed.

**Router endpoint changes:**
```python
# backend/app/routers/wp_sites.py
@router.get("/{site_id}/posts")
async def get_site_posts(
    site_id: str,
    per_page: int = 100,
    page: int = 1,
    status: str = None,
    search: str = None,      # NEW
    orderby: str = "date",  # NEW
    order: str = "desc"     # NEW
):
    # Pass new parameters to get_wp_posts
    result = await get_wp_posts(
        str(project["_id"]),
        per_page,
        page,
        status,
        search,   # NEW
        orderby,  # NEW
        order     # NEW
    )
    return result
```

**Rationale:** The `get_wp_posts` function in `wp_service.py` already supports `search`, `orderby`, and `order` parameters (lines 258-295). The router just needs to expose these parameters.

### Frontend (JavaScript)

**API client changes:**
```javascript
// frontend/src/api/client.js
export const getSitePosts = (
  siteId,
  perPage = 100,
  page = 1,
  status = null,
  search = null,      // NEW
  orderby = "date",   // NEW
  order = "desc"      // NEW
) => {
  const params = { per_page: perPage, page: page };
  if (status) params.status = status;
  if (search) params.search = search;      // NEW
  if (orderby) params.orderby = orderby; // NEW
  if (order) params.order = order;        // NEW
  return api.get(`/wp-sites/${siteId}/posts`, { params });
};
```

**Rationale:** Update the API client to pass the new parameters to the backend endpoint.

**Component changes:**
```javascript
// frontend/src/components/Projects/ProjectDetail.jsx
// Replace PostCard grid with table layout
// Add search input field
// Add sort dropdown (date, title, status)
// Add status filter dropdown
// Add manual pagination UI (100 posts per page)
```

**Rationale:** Use the same table structure as AllPosts.jsx (lines 155-224) which already demonstrates the implementation.

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Table Library | Plain HTML tables | react-table, tanstack-table | Over-engineering for MVP. AllPosts.jsx proves plain tables work fine. |
| Icon Library | react-icons 5.6.0 | heroicons, lucide-react | Already in use, has all needed icons (HiOutlinePencil, HiOutlineArrowPath) |
| HTTP Client | httpx | requests, aiohttp | Already in use, async support required for FastAPI |
| State Management | React useState | Redux, Zustand | Over-engineering for simple table state. useState works fine. |

## Installation

### Backend
```bash
# Add httpx to requirements.txt
echo "httpx>=0.28.1" >> backend/requirements.txt

# Rebuild Docker container
docker-compose build backend
```

### Frontend
```bash
# No new packages needed
# All dependencies already installed
```

## Integration Points

### Backend Integration
1. **Router endpoint:** `backend/app/routers/wp_sites.py` line 102-119
   - Add `search`, `orderby`, `order` parameters to function signature
   - Pass parameters to `get_wp_posts` function

2. **Service layer:** `backend/app/services/wp_service.py` line 258-295
   - Already supports all needed parameters
   - No changes needed

3. **WordPress REST API:** Uses standard WordPress REST API parameters
   - `search`: Search by post title/content
   - `orderby`: Order by field (date, title, modified, etc.)
   - `order`: ASC or DESC

### Frontend Integration
1. **API client:** `frontend/src/api/client.js` line 31-35
   - Update `getSitePosts` function signature
   - Add new parameters to request

2. **Component:** `frontend/src/components/Projects/ProjectDetail.jsx`
   - Replace PostCard grid with table layout
   - Add search input field
   - Add sort dropdown
   - Add status filter dropdown
   - Add manual pagination UI

3. **CSS:** `frontend/src/index.css`
   - Table styling already exists (lines 558-602)
   - Status badge styling already exists (lines 605-647)
   - Action button styling already exists (lines 1077-1108)
   - Pagination styling already exists (lines 1166-1173)

## What NOT to Add

### Do NOT Add These Libraries

| Library | Why Not |
|---------|---------|
| react-table | Over-engineering for MVP. Plain HTML tables work fine. |
| tanstack-table | Over-engineering for MVP. Plain HTML tables work fine. |
| material-ui | Not needed. Custom CSS already provides all styling. |
| ant-design | Not needed. Custom CSS already provides all styling. |
| redux | Over-engineering for simple table state. useState works fine. |
| zustand | Over-engineering for simple table state. useState works fine. |
| react-query | Over-engineering for simple API calls. axios works fine. |

### Do NOT Add These Features

| Feature | Why Not |
|---------|---------|
| Infinite scroll | Requirement specifies manual pagination (100 posts per page) |
| Site selection dropdown | Scope is project's WordPress site only |
| Origin badges | Not needed in table view (requirement says discard) |
| Bulk operations | Not in requirements for this milestone |
| Advanced filtering | Not in requirements for this milestone |

## CSS Classes Already Available

### Table Styling
- `.table-container` - Wrapper with overflow and border
- `table` - Table element with collapse
- `thead th` - Table headers with styling
- `tbody td` - Table cells with padding and borders
- `tbody tr:hover` - Row hover effect

### Status Badges
- `.status-badge` - Base badge class
- `.status-badge.publish` - Published status
- `.status-badge.draft` - Draft status
- `.status-badge.pending` - Pending status
- `.status-badge.private` - Private status

### Action Buttons
- `.action-buttons` - Container for action buttons
- `.action-btn` - Base action button class
- `.action-btn:hover` - Hover effect
- `.action-btn.danger:hover` - Danger button hover effect

### Pagination
- `.pagination` - Pagination container with flex layout

### Utility Classes
- `.loading-page` - Full-page loading state
- `.loading-spinner` - Spinner animation
- `.empty-state` - Empty state container
- `.error-banner` - Error message banner
- `.toolbar` - Toolbar container
- `.toolbar-group` - Toolbar group container

## Sources

- **Context7:** Not used (no library-specific questions)
- **Official Docs:**
  - WordPress REST API: https://developer.wordpress.org/rest-api/reference/posts/
  - React 18.3: https://react.dev/
  - FastAPI 0.115.0: https://fastapi.tiangolo.com/
  - httpx: https://www.python-httpx.org/
- **Codebase Analysis:**
  - `frontend/src/components/AllPosts.jsx` - Working table implementation
  - `frontend/src/components/Projects/ProjectDetail.jsx` - Current implementation
  - `backend/app/routers/wp_sites.py` - Current router endpoint
  - `backend/app/services/wp_service.py` - WordPress service with existing parameters
  - `frontend/src/api/client.js` - API client
  - `frontend/src/index.css` - CSS styling
  - `frontend/package.json` - Frontend dependencies
  - `backend/requirements.txt` - Backend dependencies

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | AllPosts.jsx proves existing stack works. No new libraries needed. |
| Backend Changes | HIGH | `get_wp_posts` already supports all parameters. Just need to expose in router. |
| Frontend Changes | HIGH | AllPosts.jsx provides working reference implementation. |
| CSS/Styling | HIGH | All required CSS classes already exist in index.css. |
| Integration | HIGH | Clear integration points identified. |
| httpx Dependency | HIGH | Verified it's used in codebase but missing from requirements.txt. |

## Gaps to Address

- **httpx in requirements.txt:** Currently used but not listed. Should be added to ensure reproducible builds.
- **No other gaps:** All other functionality is already supported by existing stack.
