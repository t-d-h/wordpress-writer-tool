# Technology Stack

**Project:** WordPress Writer Tool - Token Usage & All Posts Features
**Researched:** 2026-04-14
**Mode:** Ecosystem research for feature additions

## Recommended Stack

### Core Framework (Existing - No Changes)
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| FastAPI | 0.115.0 | Backend REST API framework | Already in use, async support, Pydantic validation |
| React | 18.3.1 | Frontend UI framework | Already in use, functional components, hooks |
| MongoDB | 7+ | Data store | Already in use, aggregation framework for token usage |
| Redis | 5.0.0 | Pub/sub messaging | Already in use, job processing |

### Token Usage Aggregation
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| MongoDB Aggregation Framework | Native | Calculate token totals | Built-in `$group` and `$sum` operators, no additional libraries needed |
| Motor | 3.6.0 | Async MongoDB driver | Already in use, supports all aggregation operations |
| Pydantic | 2.9.0 | Response validation | Already in use, for token usage response models |

### WordPress Post Listing (All Posts Tab)
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| TanStack Table | 8.20+ | Headless table component | Full control over markup/styles, lightweight, industry standard for 2025 |
| httpx | >=0.28.1 | Async HTTP client | Already in use, WordPress REST API calls |
| WordPress REST API | Native | Fetch posts from WordPress | Built-in filtering, sorting, searching, pagination |

### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Recharts | 2.12+ | Token usage visualization | Only if charts needed later; simple display uses HTML/CSS |
| date-fns | 3.6+ | Date formatting | For post date display in All Posts tab |

## Installation

```bash
# Backend (no new dependencies needed for token usage aggregation)
# Existing requirements.txt already includes motor, pymongo, pydantic

# Frontend - Add TanStack Table for All Posts tab
npm install @tanstack/react-table

# Optional - Add Recharts if token usage charts needed later
npm install recharts

# Optional - Add date-fns for date formatting
npm install date-fns
```

## Detailed Rationale

### Token Usage Aggregation

**Approach: MongoDB Aggregation Pipeline**

The MongoDB aggregation framework is the standard 2025 approach for calculating totals and summaries from document collections. For token usage aggregation, we use:

- **`$group` stage**: Groups documents by project_id and post type (research, outline, content, thumbnail)
- **`$sum` accumulator**: Sums token values within each group
- **`$project` stage**: Shapes the output for the API response

**Example aggregation for token usage by project:**
```python
pipeline = [
    {"$match": {"project_id": ObjectId(project_id)}},
    {"$group": {
        "_id": "$project_id",
        "research_tokens": {"$sum": "$token_usage.research"},
        "outline_tokens": {"$sum": "$token_usage.outline"},
        "content_tokens": {"$sum": "$token_usage.content"},
        "thumbnail_tokens": {"$sum": "$token_usage.thumbnail"},
        "total_tokens": {"$sum": "$token_usage.total"},
        "total_posts": {"$sum": 1}
    }}
]
```

**Why MongoDB Aggregation:**
- **No additional dependencies**: Leverages existing MongoDB installation
- **Server-side computation**: Reduces data transfer, calculates totals in database
- **Flexible**: Can easily add more aggregations (by date, by provider, etc.)
- **Performant**: MongoDB 7+ has optimized aggregation pipeline execution
- **Standard approach**: Well-documented, widely used in production

**Confidence: HIGH** - MongoDB aggregation is the de facto standard for this use case, verified with official MongoDB documentation.

### WordPress Post Listing (All Posts Tab)

**Approach: TanStack Table + WordPress REST API**

TanStack Table (formerly React Table) is the industry-standard headless table library for React in 2025. It provides:

- **Headless architecture**: Full control over markup and styling
- **Built-in sorting, filtering, pagination**: No need to implement from scratch
- **TypeScript support**: Strong typing for table data
- **Lightweight**: Smaller bundle size than component-based alternatives
- **Framework agnostic**: Works with React, Vue, Solid, Svelte

**WordPress REST API Integration:**

The existing `wp_service.py` already has a `get_wp_posts()` function that:
- Fetches posts from WordPress REST API (`/wp-json/wp/v2/posts`)
- Supports pagination (`per_page`, `page` parameters)
- Supports status filtering (`status` parameter)
- Returns total count via `X-WP-Total` header

**Additional WordPress REST API parameters for All Posts tab:**
- `search`: Filter by post title
- `orderby`: Sort by date, title, modified, etc.
- `order`: Ascending or descending
- `after`/`before`: Filter by date range

**Why TanStack Table:**
- **Headless UI**: Matches existing project pattern of custom styling
- **Industry standard**: Most popular React table library in 2025
- **Future-proof**: Actively maintained, regular updates
- **No lock-in**: Can be replaced if needed, unlike component-based libraries
- **Performance**: Virtual scrolling support for large datasets

**Confidence: HIGH** - TanStack Table is the recommended choice for React tables in 2025, verified with official documentation and ecosystem research.

### Token Usage Display

**Approach: Simple HTML/CSS (No Charting Library)**

For the MVP, token usage display should use simple HTML/CSS:
- Breakdown by post type (research, outline, content, thumbnail)
- Total input tokens and total output tokens
- Simple bar indicators or progress bars

**Why No Charting Library:**
- **Overkill for MVP**: Simple display doesn't need full charting library
- **Bundle size concern**: Charting libraries add significant weight
- **Existing patterns**: Project uses simple HTML/CSS for statistics display
- **Can add later**: Recharts can be added if visualization needs grow

**If Charts Needed Later:**

Recharts is the standard choice for React charting in 2025:
- **Declarative API**: React component-based
- **Responsive**: Works on all screen sizes
- **Lightweight**: Smaller than Chart.js or D3
- **Good documentation**: Well-maintained, active community

**Confidence: HIGH** - Simple HTML/CSS is appropriate for MVP; Recharts is the standard choice if charts needed later.

## Alternatives Considered

### Token Usage Aggregation

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Aggregation | MongoDB Aggregation | Application-level aggregation | Slower, more data transfer, reinventing the wheel |
| Aggregation | MongoDB Aggregation | Redis aggregation | Redis is for pub/sub, not persistent aggregation |
| Aggregation | MongoDB Aggregation | Separate analytics DB | Overkill for MVP, adds complexity |

### WordPress Post Listing

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Table Library | TanStack Table | AG Grid | Component-based, larger bundle, less control over markup |
| Table Library | TanStack Table | React-Table v7 | Deprecated, replaced by TanStack Table |
| Table Library | TanStack Table | MUI DataGrid | Component-based, requires MUI dependency |
| Table Library | TanStack Table | Custom implementation | Reinventing the wheel, no sorting/filtering/pagination |

### Token Usage Display

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Display | HTML/CSS | Chart.js | Overkill for simple display, larger bundle |
| Display | HTML/CSS | D3.js | Overkill, steep learning curve |
| Display | HTML/CSS | Recharts | Unnecessary for MVP, can add later |

## Implementation Notes

### Backend: Token Usage Aggregation

**New API Endpoint:**
```python
@router.get("/projects/{project_id}/token-usage")
async def get_project_token_usage(project_id: str):
    """Get aggregated token usage for a project."""
    pipeline = [
        {"$match": {"project_id": ObjectId(project_id)}},
        {"$group": {
            "_id": "$project_id",
            "research_tokens": {"$sum": "$token_usage.research"},
            "outline_tokens": {"$sum": "$token_usage.outline"},
            "content_tokens": {"$sum": "$token_usage.content"},
            "thumbnail_tokens": {"$sum": "$token_usage.thumbnail"},
            "total_tokens": {"$sum": "$token_usage.total"},
            "total_posts": {"$sum": 1}
        }}
    ]
    result = await posts_col.aggregate(pipeline).to_list(length=1)
    return result[0] if result else {"total_tokens": 0, "total_posts": 0}
```

**No new dependencies needed** - Uses existing `motor` and `pymongo`.

### Backend: WordPress Post Listing

**Enhanced `get_wp_posts()` function:**
```python
async def get_wp_posts(
    project_id: str,
    per_page: int = 100,
    page: int = 1,
    status: str = None,
    search: str = None,
    orderby: str = "date",
    order: str = "desc"
) -> dict:
    """Fetch posts from WordPress REST API with filtering and sorting."""
    wp_site = await _get_wp_site(project_id)
    headers = _get_auth_header(wp_site["username"], wp_site["api_key"])

    url = f"{wp_site['url'].rstrip('/')}/wp-json/wp/v2/posts"
    params = {
        "per_page": per_page,
        "page": page,
        "_embed": True,
        "orderby": orderby,
        "order": order
    }
    if status:
        params["status"] = status
    if search:
        params["search"] = search

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()

        posts = response.json()
        total = int(response.headers.get("X-WP-Total", len(posts)))

        return {"posts": posts, "total": total}
```

**No new dependencies needed** - Uses existing `httpx`.

### Frontend: All Posts Tab with TanStack Table

**Example implementation:**
```jsx
import { useReactTable, getCoreRowModel, getSortedRowModel, getFilteredRowModel } from '@tanstack/react-table'

function AllPostsTab({ project }) {
  const [posts, setPosts] = useState([])
  const [sorting, setSorting] = useState([])
  const [globalFilter, setGlobalFilter] = useState('')

  const columns = [
    { accessorKey: 'title.rendered', header: 'Title' },
    { accessorKey: 'status', header: 'Status' },
    { accessorKey: 'date', header: 'Date' },
    { accessorKey: 'link', header: 'Actions' }
  ]

  const table = useReactTable({
    data: posts,
    columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel()
  })

  // Render table with custom markup
}
```

**New dependency:** `@tanstack/react-table`

### Frontend: Token Usage Display

**Simple HTML/CSS implementation:**
```jsx
function TokenUsageDisplay({ tokenUsage }) {
  return (
    <div className="token-usage">
      <div className="token-row">
        <span>Research:</span>
        <span>{tokenUsage.research_tokens}</span>
      </div>
      <div className="token-row">
        <span>Outline:</span>
        <span>{tokenUsage.outline_tokens}</span>
      </div>
      <div className="token-row">
        <span>Content:</span>
        <span>{tokenUsage.content_tokens}</span>
      </div>
      <div className="token-row">
        <span>Thumbnail:</span>
        <span>{tokenUsage.thumbnail_tokens}</span>
      </div>
      <div className="token-row total">
        <span>Total:</span>
        <span>{tokenUsage.total_tokens}</span>
      </div>
    </div>
  )
}
```

**No new dependencies needed** - Uses existing React patterns.

## Sources

### MongoDB Aggregation
- MongoDB Aggregation Pipeline Documentation (HIGH confidence)
  - URL: https://www.mongodb.com/docs/manual/core/aggregation-pipeline/
  - Verified: 2026-04-14
- MongoDB $group Operator Documentation (HIGH confidence)
  - URL: https://www.mongodb.com/docs/manual/reference/operator/aggregation/group/
  - Verified: 2026-04-14
- MongoDB $sum Operator Documentation (HIGH confidence)
  - URL: https://www.mongodb.com/docs/manual/reference/operator/aggregation/sum/
  - Verified: 2026-04-14

### TanStack Table
- TanStack Table Official Documentation (HIGH confidence)
  - URL: https://tanstack.com/table/latest/docs/introduction
  - Verified: 2026-04-14
- TanStack Table Quick Start Guide (HIGH confidence)
  - URL: https://tanstack.com/table/latest/docs/guide/quick-start
  - Verified: 2026-04-14

### WordPress REST API
- WordPress REST API Posts Reference (HIGH confidence)
  - URL: https://developer.wordpress.org/rest-api/reference/posts/
  - Verified: 2026-04-14
- WordPress REST API Authentication (HIGH confidence)
  - URL: https://developer.wordpress.org/rest-api/using-the-rest-api/authentication/
  - Verified: 2026-04-14

### Recharts (Future Consideration)
- Recharts Official Documentation (MEDIUM confidence)
  - URL: https://recharts.org/
  - Verified: 2026-04-14

### Existing Codebase
- backend/requirements.txt (HIGH confidence)
- frontend/package.json (HIGH confidence)
- backend/app/services/wp_service.py (HIGH confidence)
- backend/app/models/post.py (HIGH confidence)
- frontend/src/components/Projects/ProjectDetail.jsx (HIGH confidence)

---

*Stack research: 2026-04-14*
