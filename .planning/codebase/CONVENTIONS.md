# Coding Conventions

**Analysis Date:** 2026-04-14

## Naming Patterns

**Files:**
- Backend Python: `snake_case.py` (e.g., `ai_service.py`, `wp_service.py`, `redis_client.py`)
- Frontend React: `PascalCase.jsx` (e.g., `Dashboard.jsx`, `ProjectDetail.jsx`, `AIProviders.jsx`)
- Config files: `kebab-case.js` (e.g., `eslint.config.js`, `vite.config.js`)

**Functions:**
- Backend Python: `snake_case` (e.g., `research_topic()`, `generate_outline()`, `format_post()`)
- Private/protected Python functions prefixed with underscore: `_get_gemini_key()`, `_call_openai()`, `_update_job_status()`
- Frontend handlers: `camelCase` (e.g., `handleSubmit()`, `handleDelete()`, `handleEdit()`, `load()`, `handleAction()`)

**Variables:**
- Both codebases: `camelCase` for state/locals (`api_key`, `is_running()`, `showModal`, `editingId`)
- Constants: `UPPER_SNAKE_CASE` in Python (`JOB_CHANNEL`, `TASK_MAP`) and `ALL_CAPS` in JS (`API_BASE`)

**Types:**
- Database collection names use `snake_case` suffix `_col` (e.g., `posts_col`, `jobs_col`, `ai_providers_col`)
- React components use `PascalCase` matching filename exactly (e.g., `export default function AIProviders()`)
- Helper sub-components placed in same file with lowercase or PascalCase (e.g., `BoolBadge` in `ProjectDetail.jsx`)

**CSS Classes:**
- BEM-like naming with dashes: `.empty-state`, `.stat-card`, `.page-title`, `.modal-overlay`
- State modifiers: `.stat-card.pending`, `.stat-card.failed`, `.pipeline-step.done`

## Code Style

**Formatting:**
- Frontend: ESLint 9.x flat config with recommended settings
- Backend: No explicit linter/config detected (no `.flake8`, `.pylintrc`, `pyproject.toml`, or `ruff.toml`)
- Code follows PEP 8 conventions

**Linting:**
- Frontend: `frontend/eslint.config.js`
- Ruleset: ESLint 9.x flat config with recommended settings
- React plugin: `eslint-plugin-react`, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`
- EcmaVersion: 2020, JSX enabled
- Key rule override: `'react/jsx-no-target-blank': 'off'`
- Exports only: `'react-refresh/only-export-components': 'warn'` with `allowConstantExport: true`
- Run: `npm run lint` -> `eslint .`

**Backend:**
- No explicit linter configured
- Code follows PEP 8 conventions
- Imports ordered: stdlib first, then third-party, then local `app.*` modules

## Import Organization

**Order:**
1. Python: stdlib imports first, then third-party packages, then local `app.*` modules
2. Frontend: React hooks first, then components, then API functions

**Path Aliases:**
- No path aliases configured
- All imports use relative paths or full module paths

**Example Python import order:**
```python
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from pydantic import BaseModel
from app.database import ai_providers_col
from app.models.ai_provider import (
    AIProviderCreate,
    AIProviderUpdate,
    AIProviderResponse,
)
```

**Example Frontend import order:**
```javascript
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { HiOutlinePlay, HiOutlineClock } from 'react-icons/hi2'
import { getDashboardStats } from '../api/client'
```

## Error Handling

**Patterns:**
- Backend: Validation errors use `HTTPException(status_code=400/404, detail="...")`
- Backend: Missing resources use `raise HTTPException(status_code=404, detail="Resource not found")`
- Backend: Unexpected exceptions use `raise Exception("...")` (used in services, not routers)
- Backend: No custom exception classes — uses FastAPI's built-in `HTTPException`
- Backend: No global exception handlers or middleware for error normalization
- Frontend: All API calls wrapped in `try/catch`
- Frontend: Errors shown with `alert('Error: ' + (e.response?.data?.detail || e.message))`
- Frontend: Loading state managed with `useState(true)`, set to `false` in `finally`
- Frontend: No toast/notification system — native `alert()` and `confirm()` for all user feedback
- Frontend: Graceful degradation: components render empty/error state on failure
- Workers: Each task handler catches with `try/except Exception as e`
- Workers: Failed tasks update status to `"failed"` in MongoDB and Redis
- Workers: Stack traces printed via `traceback.print_exc()`

## Logging

**Framework:**
- Backend: `print()` statements for logging (no logging framework)
- Backend: Format: `[WORKER] message`, `[TASK] message`
- Backend: Uses `traceback.print_exc()` for stack traces
- Frontend: `console.error()` for error logging
- Frontend: No `console.log()` observed in normal operation
- Workers: Python logging module with structured logging (`worker/app/logging_config.py`)
- Workers: Logger format: `[SECTION] message` (e.g., `[RESEARCH] Starting research for post {post_id}`)
- No structured logging in backend API layer

**Patterns:**
- Backend: `print()` for debugging and status messages
- Workers: `logger.info()`, `logger.error()`, `logger.warning()`, `logger.exception()`
- Frontend: `console.error()` in catch blocks
- No centralized logging configuration for backend API

## Comments

**When to Comment:**
- Docstrings on all public functions (triple-quote)
- Module-level docstrings in service files: `"""AI Service — handles research..."""`
- No inline comments in most code, occasional brief notes
- No JSDoc or inline comments in components
- Minimal comments — one observed: `// Auto-refresh while jobs are running` in `PostView.jsx`

**JSDoc/TSDoc:**
- Not used in frontend
- No type annotations in JavaScript/JSX files
- PropTypes used for component prop validation (e.g., `BoolBadge.propTypes`, `JobStatusBadge.propTypes`)

## Function Design

**Size:**
- Backend services: Functions can be long (e.g., `run_publish()` is 100+ lines)
- Frontend components: Can be large (e.g., `ProjectDetail.jsx` is 775 lines)
- No strict size guidelines enforced

**Parameters:**
- Backend: Services use many parameters, not data classes (e.g., `create_wp_post(project_id, title, content, meta_description, thumbnail_media_id, status)`)
- Backend: Return tuples for multi-return values: `tuple[str, int]` for `(response, tokens)`
- Frontend: Components use multiple `useState` hooks for form state
- Frontend: Form state as object: `setForm({ ...form, field: value })`
- Frontend: No useReducer, no form libraries (react-hook-form, formik)

**Return Values:**
- Backend: Pydantic models used for request/response validation
- Backend: Pattern: `<Model>Create` — creation payload, `<ModelUpdate>` — partial update (`Optional` fields), `<ModelResponse>` — response with computed/derived fields
- Frontend: API functions return axios response objects
- Frontend: Components render JSX directly

## Module Design

**Exports:**
- Python modules export functions directly (no `__all__` defined except in `__init__.py` files which are mostly empty)
- Frontend: All components are default exports, API functions are named exports in `frontend/src/api/client.js`
- Frontend: `api/client.js` assembles all API methods and exports them individually plus default axios instance
- `__init__.py` files exist in all packages but are empty or contain only `pass`
- Explicit imports used, not star imports from packages

**Barrel Files:**
- Frontend: `frontend/src/api/client.js` acts as a barrel file for API functions
- Backend: `__init__.py` files are mostly empty, not used as barrel files

## CSS/Styling Conventions

**CSS Variables:**
- Design system defined in `frontend/src/index.css` with CSS custom properties
- Color variables: `--bg-primary`, `--text-primary`, `--accent-primary`, etc.
- Size variables: `--sidebar-width`, `--radius-sm`, `--radius-md`, etc.
- Transition variables: `--transition-fast`, `--transition-normal`, `--transition-slow`
- Shadow variables: `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-glow`

**Class Naming:**
- BEM-like naming with dashes: `.empty-state`, `.stat-card`, `.page-title`, `.modal-overlay`
- State modifiers: `.stat-card.pending`, `.stat-card.failed`, `.pipeline-step.done`
- Utility classes: `.loading-page`, `.loading-spinner`, `.btn`, `.btn-primary`, `.btn-secondary`

**Component Styling:**
- Components use inline styles for dynamic values (e.g., `style={{ marginBottom: 20 }}`)
- CSS classes for static styling
- No CSS-in-JS library used
- No styled-components or emotion

**Responsive Design:**
- Not explicitly observed in code
- No media queries in the CSS files reviewed

---

*Convention analysis: 2026-04-14*
