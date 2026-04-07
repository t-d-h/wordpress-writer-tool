# Coding Conventions

**Analysis Date:** 2026-04-07

## Naming Patterns

**Files:**
- Backend Python: `snake_case.py` (e.g., `ai_service.py`, `redis_client.py`, `wp_sites.py`)
- Frontend React: `PascalCase.jsx` (e.g., `Dashboard.jsx`, `ProjectDetail.jsx`, `AIProviders.jsx`)
- Config: `kebab-case.js` (e.g., `eslint.config.js`, `vite.config.js`)

**Functions:**
- Python backend: `snake_case` (e.g., `research_topic()`, `generate_outline()`, `format_post()`)
- Private/protected Python functions prefixed with underscore: `_get_gemini_key()`, `_call_openai()`, `_update_job_status()`
- Frontend handlers: `camelCase` (e.g., `handleSubmit()`, `handleDelete()`, `handleEdit()`, `load()`, `handleAction()`)

**Variables:**
- Both codebases: `camelCase` for state/locals (`api_key`, `is_running()`, `showModal`, `editingId`)
- Constants: `UPPER_SNAKE_CASE` in Python (`JOB_CHANNEL`, `TASK_MAP`) and `ALL_CAPS` in JS (`API_BASE`)
- Database collection names use `snake_case` suffix `_col` (e.g., `posts_col`, `jobs_col`)

**Component names (frontend):**
- React components use `PascalCase` matching filename exactly (e.g., `export default function AIProviders()`)
- Helper sub-components placed in same file with lowercase or PascalCase (e.g., `BoolBadge` in `ProjectDetail.jsx`)

**CSS Classes:**
- BEM-like naming with dashes: `.empty-state`, `.stat-card`, `.page-title`, `.modal-overlay`
- State modifiers: `.stat-card.pending`, `.stat-card.failed`, `.pipeline-step.done`

## Code Style

**Frontend Linting (ESLint):**
- Config: `frontend/eslint.config.js`
- Ruleset: ESLint 9.x flat config with recommended settings
- React plugin: `eslint-plugin-react`, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`
- EcmaVersion: 2020, JSX enabled
- Key rule override: `'react/jsx-no-target-blank': 'off'`
- Exports only: `'react-refresh/only-export-components': 'warn'` with `allowConstantExport: true`
- Run: `npm run lint` -> `eslint .`

**Backend (Python):**
- No explicit linter/config detected (no `.flake8`, `.pylintrc`, `pyproject.toml`, or `ruff.toml`)
- Code follows PEP 8 conventions
- Imports ordered: stdlib first, then third-party, then local `app.*` modules

**No Prettier config detected.** The project uses ESLint's built-in formatting recommendations only.

**No auto-formatters detected for Python.**

## Import Organization

**Backend Python (`backend/app/`):**
1. Standard library imports (`import os`, `import json`, `import uuid`, `import base64`)
2. Third-party imports (`from fastapi import ...`, `from bson import ObjectId`, `from PIL import ...`)
3. Local imports using `app.` prefix (`from app.database import ...`, `from app.config import settings`)

**Local Python import pattern:** Always use absolute `from app.<module> import ...` — never relative imports.
Example from `backend/app/routers/posts.py`:
```python
from app.database import posts_col, projects_col, jobs_col
from app.models.post import PostCreate, BulkPostCreate, PostUpdate, PostResponse
from app.redis_client import publish_job
```

**Frontend JavaScript (`frontend/src/`):**
1. Library imports first (`import React from 'react'`, `import axios from 'axios'`)
2. Route/component imports (`import { Routes, Route } from 'react-router-dom'`)
3. Local imports from `../api/client` or sibling imports (`import Sidebar from './components/Layout'`)

**Path pattern:** Relative imports with `../` for sibling/parent, no path aliases configured.
```javascript
import { getPost, publishPost } from '../../api/client'
import { useParams, useNavigate } from 'react-router-dom'
```

## Component Architecture

**Default exports:** All frontend components use `export default function ComponentName()` — no named exports for components.
**No destructuring props:** Components use inline props or inline destructuring.
**No TypeScript:** Both codebases are plain JS/JSX and Python — no types on the frontend.

**Backend routers pattern:**
- All routers follow identical CRUD structure
- `format_*` helper function converts MongoDB doc to Pydantic model response
- Router prefix set consistently: `APIRouter(prefix="/api/<resource>", tags=["<Tag>"])`

**Backend service layer:**
- Services are stateless async functions
- No class-based services — all functions use `async def`
- Helper functions prefixed with `_` (e.g., `_get_provider()`, `_get_auth_header()`)

**Frontend component pattern:**
- All components are functional (function components)
- No class components
- State management via `useState` only — no Redux, Zustand, or Context API
- Data loading via `useEffect` + `async/await` pattern
- No custom hooks extracted — all logic is inline

## Error Handling

**Backend Python:**
- Validation errors: `HTTPException(status_code=400/404, detail="...")`
- Missing resources: `raise HTTPException(status_code=404, detail="Resource not found")`
- Unexpected exceptions: `raise Exception("...")` (used in services, not routers)
- No custom exception classes — uses FastAPI's built-in `HTTPException`
- No global exception handlers or middleware for error normalization

Example from `backend/app/routers/posts.py`:
```python
@router.get("/{post_id}")
async def get_post(post_id: str):
    doc = await posts_col.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Post not found")
    return format_post(doc)
```

**Frontend JavaScript:**
- All API calls wrapped in `try/catch`
- Errors shown with `alert('Error: ' + (e.response?.data?.detail || e.message))`
- Loading state managed with `useState(true)`, set to `false` in `finally`
- No toast/notification system — native `alert()` and `confirm()` for all user feedback
- Graceful degradation: components render empty/error state on failure

```javascript
const load = async () => {
  try {
    const { data } = await getDashboardStats()
    setStats(data)
  } catch (e) {
    console.error('Failed to load stats', e)
  } finally {
    setLoading(false)
  }
}
```

**Worker error handling:**
- Each task handler catches with `try/except Exception as e`
- Failed tasks update status to `"failed"` in MongoDB and Redis
- Stack traces printed via `traceback.print_exc()`

## Logging

**Backend:**
- `print()` statements for logging (no logging framework)
- Format: `[WORKER] message`, `[TASK] message`
- Uses `traceback.print_exc()` for stack traces

**Frontend:**
- `console.error()` for error logging
- No `console.log()` observed in normal operation
- No structured logging

## Comments

**Backend Python:**
- Docstrings on all public functions (triple-quote)
- Module-level docstrings in service files: `"""AI Service — handles research..."""`
- No inline comments in most code, occasional brief notes

**Frontend JavaScript:**
- No JSDoc or inline comments in components
- Minimal comments — one observed: `// Auto-refresh while jobs are running` in `PostView.jsx`

## Function Design

**Backend Python:**
- Services use many parameters, not data classes (e.g., `create_wp_post(project_id, title, content, meta_description, thumbnail_media_id, status)`)
- Return tuples for multi-return values: `tuple[str, int]` for `(response, tokens)`
- Pydantic models used only for request/response validation (Create/Update/Response pattern)

**Pydantic model naming pattern:**
- `<Model>Create` — creation payload
- `<Model>Update` — partial update (`Optional` fields)
- `<Model>Response` — response with computed/derived fields

**Frontend JavaScript:**
- Components use multiple `useState` hooks for form state
- Form state as object: `setForm({ ...form, field: value })`
- No useReducer, no form libraries (react-hook-form, formik)

## Module Design

**Exports:**
- Python modules export functions directly (no `__all__` defined except in `__init__.py` files which are mostly empty)
- Frontend: all components are default exports, API functions are named exports in `frontend/src/api/client.js`
- Frontend `api/client.js` assembles all API methods and exports them individually plus default axios instance

**Barrel files:**
- `__init__.py` files exist in all packages but are empty or contain only `pass`
- Explicit imports used, not star imports from packages

## CSS/Styling Conventions

**Single global stylesheet:** `frontend/src/index.css` contains all styles (877 lines)
**Default Vite CSS:** `frontend/src/App.css` is the stock Vite boilerplate and appears mostly unused/overridden by `index.css`

**CSS custom properties (design tokens):** All colors, shadows, radii, transitions defined as CSS variables in `:root`.

**Pattern:** CSS classes follow semantic naming (`.page-header`, `.stat-card`, `.empty-state`) — not utility CSS like Tailwind.

**Status badges:** Color mapping via `<status-badge status-{value}>` classes (e.g., `.status-draft`, `.status-published`) tied to backend status strings.

---

*Convention analysis: 2026-04-07*
