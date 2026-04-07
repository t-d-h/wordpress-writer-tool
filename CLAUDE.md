<!-- GSD:project-start source:PROJECT.md -->
## Project

**WordPress Writer Tool**

A full-stack AI content generation tool for WordPress sites. Users configure AI providers and WordPress sites, create projects with AI-assisted content pipelines (outlines, full articles, thumbnails, section images), and publish posts to WordPress. Backend is Python/FastAPI with MongoDB + Redis; frontend is React SPA.

**Core Value:** Validate WordPress site connectivity and credentials before saving, so users know immediately if their site is configured correctly — not after wasting time creating content that can't be published.

### Constraints

- **Tech stack**: Python/FastAPI backend, MongoDB, Redis, React frontend — these won't change for this project
- **MVP stage**: This is an early MVP; solutions should be pragmatic, not over-engineered
- **No app-level auth**: Relies on network-level isolation
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- **Python 3.11** - Backend API, AI services, async workers
- **JavaScript (ES2020)** with JSX - React frontend application
- **HTML/CSS** - Frontend styling
## Runtime
- Python 3.11-slim (Docker container) - Backend runtime
- Node.js with Vite 5.4 - Frontend dev/build server
- Backend: `pip` via `requirements.txt`
- Frontend: `npm` via `package.json`
- Lockfile: Not detected (no `package-lock.json` or `requirements.lock`)
## Frameworks
- **FastAPI 0.115.0** - Backend REST API framework (`backend/app/main.py`)
- **React 18.3** - Frontend UI framework
- **Vite 5.4** - Frontend build tool and dev server
- **React Router 7.14** - Frontend client-side routing
- **Motor 3.6 + PyMongo 4.7-4.9** - Async MongoDB driver
- **Redis 5.0** - Async Redis pub/sub job queue
- **Uvicorn 0.30** - ASGI server for FastAPI
- Not detected
- **ESLint 9.13** - Frontend linting (`frontend/eslint.config.js`)
- **Docker Compose** - Multi-container orchestration (backend, worker, frontend)
## Key Dependencies
- `openai` 1.50.0 - OpenAI API client (GPT-4o model used)
- `google-genai` 1.5.0 - Google Gemini API client (content + image generation)
- `anthropic` 0.39.0 - Anthropic API client (Claude Sonnet 4 model used)
- `httpx` >=0.28.1 - Async HTTP client for WordPress REST API calls
- `axios` 1.14.0 - Frontend HTTP client for API communication
- `pydantic` 2.9.0 - Request/response validation and serialization
- `python-multipart` 0.0.9 - File upload handling
- `Pillow` 10.4.0 - Image processing
- `react-icons` 5.6.0 - Icon library
- `@vitejs/plugin-react` 4.3.3 - React/JSX compilation
## Configuration
- Backend config via environment variables (`backend/app/config.py`)
- Frontend config via `VITE_API_URL` env var (`frontend/src/api/client.js`)
- `.env` file present at project root (loaded by Docker Compose)
- `MONGODB_URL` - MongoDB connection URL
- `MONGODB_DB` - Database name (`wordpress_writer`)
- `REDIS_URL` - Redis connection URL
- `BACKEND_HOST` / `BACKEND_PORT` - Backend bind address (default `0.0.0.0:8000`)
- `FRONTEND_URL` - Frontend URL for CORS (default `http://localhost:5173`)
- `VITE_API_URL` - Frontend API base URL (default `http://localhost:8001`)
- `backend/Dockerfile` - Python 3.11-slim, installs requirements, runs uvicorn
- Frontend has a `Dockerfile` (path: `frontend/Dockerfile`)
- `docker-compose.yml` - Defines three services: `backend` (port 8001), `worker`, `frontend` (port 5174)
## Platform Requirements
- Docker and Docker Compose
- Python 3.11
- Node.js (for frontend dev)
- External MongoDB and Redis servers (configured via env vars, not containerized in current docker-compose)
- Targets Docker deployment via docker-compose
- MongoDB and Redis must be provisioned separately (MongoDB 7 and Redis 7 commented out in docker-compose)
- External WordPress site(s) with REST API and application passwords enabled
- AI provider API keys (OpenAI, Gemini, or Anthropic)
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Backend Python: `snake_case.py` (e.g., `ai_service.py`, `redis_client.py`, `wp_sites.py`)
- Frontend React: `PascalCase.jsx` (e.g., `Dashboard.jsx`, `ProjectDetail.jsx`, `AIProviders.jsx`)
- Config: `kebab-case.js` (e.g., `eslint.config.js`, `vite.config.js`)
- Python backend: `snake_case` (e.g., `research_topic()`, `generate_outline()`, `format_post()`)
- Private/protected Python functions prefixed with underscore: `_get_gemini_key()`, `_call_openai()`, `_update_job_status()`
- Frontend handlers: `camelCase` (e.g., `handleSubmit()`, `handleDelete()`, `handleEdit()`, `load()`, `handleAction()`)
- Both codebases: `camelCase` for state/locals (`api_key`, `is_running()`, `showModal`, `editingId`)
- Constants: `UPPER_SNAKE_CASE` in Python (`JOB_CHANNEL`, `TASK_MAP`) and `ALL_CAPS` in JS (`API_BASE`)
- Database collection names use `snake_case` suffix `_col` (e.g., `posts_col`, `jobs_col`)
- React components use `PascalCase` matching filename exactly (e.g., `export default function AIProviders()`)
- Helper sub-components placed in same file with lowercase or PascalCase (e.g., `BoolBadge` in `ProjectDetail.jsx`)
- BEM-like naming with dashes: `.empty-state`, `.stat-card`, `.page-title`, `.modal-overlay`
- State modifiers: `.stat-card.pending`, `.stat-card.failed`, `.pipeline-step.done`
## Code Style
- Config: `frontend/eslint.config.js`
- Ruleset: ESLint 9.x flat config with recommended settings
- React plugin: `eslint-plugin-react`, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`
- EcmaVersion: 2020, JSX enabled
- Key rule override: `'react/jsx-no-target-blank': 'off'`
- Exports only: `'react-refresh/only-export-components': 'warn'` with `allowConstantExport: true`
- Run: `npm run lint` -> `eslint .`
- No explicit linter/config detected (no `.flake8`, `.pylintrc`, `pyproject.toml`, or `ruff.toml`)
- Code follows PEP 8 conventions
- Imports ordered: stdlib first, then third-party, then local `app.*` modules
## Import Organization
## Component Architecture
- All routers follow identical CRUD structure
- `format_*` helper function converts MongoDB doc to Pydantic model response
- Router prefix set consistently: `APIRouter(prefix="/api/<resource>", tags=["<Tag>"])`
- Services are stateless async functions
- No class-based services — all functions use `async def`
- Helper functions prefixed with `_` (e.g., `_get_provider()`, `_get_auth_header()`)
- All components are functional (function components)
- No class components
- State management via `useState` only — no Redux, Zustand, or Context API
- Data loading via `useEffect` + `async/await` pattern
- No custom hooks extracted — all logic is inline
## Error Handling
- Validation errors: `HTTPException(status_code=400/404, detail="...")`
- Missing resources: `raise HTTPException(status_code=404, detail="Resource not found")`
- Unexpected exceptions: `raise Exception("...")` (used in services, not routers)
- No custom exception classes — uses FastAPI's built-in `HTTPException`
- No global exception handlers or middleware for error normalization
- All API calls wrapped in `try/catch`
- Errors shown with `alert('Error: ' + (e.response?.data?.detail || e.message))`
- Loading state managed with `useState(true)`, set to `false` in `finally`
- No toast/notification system — native `alert()` and `confirm()` for all user feedback
- Graceful degradation: components render empty/error state on failure
- Each task handler catches with `try/except Exception as e`
- Failed tasks update status to `"failed"` in MongoDB and Redis
- Stack traces printed via `traceback.print_exc()`
## Logging
- `print()` statements for logging (no logging framework)
- Format: `[WORKER] message`, `[TASK] message`
- Uses `traceback.print_exc()` for stack traces
- `console.error()` for error logging
- No `console.log()` observed in normal operation
- No structured logging
## Comments
- Docstrings on all public functions (triple-quote)
- Module-level docstrings in service files: `"""AI Service — handles research..."""`
- No inline comments in most code, occasional brief notes
- No JSDoc or inline comments in components
- Minimal comments — one observed: `// Auto-refresh while jobs are running` in `PostView.jsx`
## Function Design
- Services use many parameters, not data classes (e.g., `create_wp_post(project_id, title, content, meta_description, thumbnail_media_id, status)`)
- Return tuples for multi-return values: `tuple[str, int]` for `(response, tokens)`
- Pydantic models used only for request/response validation (Create/Update/Response pattern)
- `<Model>Create` — creation payload
- `<Model>Update` — partial update (`Optional` fields)
- `<Model>Response` — response with computed/derived fields
- Components use multiple `useState` hooks for form state
- Form state as object: `setForm({ ...form, field: value })`
- No useReducer, no form libraries (react-hook-form, formik)
## Module Design
- Python modules export functions directly (no `__all__` defined except in `__init__.py` files which are mostly empty)
- Frontend: all components are default exports, API functions are named exports in `frontend/src/api/client.js`
- Frontend `api/client.js` assembles all API methods and exports them individually plus default axios instance
- `__init__.py` files exist in all packages but are empty or contain only `pass`
- Explicit imports used, not star imports from packages
## CSS/Styling Conventions
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Two Docker containers for the backend: one FastAPI HTTP server (`backend`) + one Redis pub/sub consumer worker (`worker`)
- MongoDB as the single data store (both direct documents via motor and job records)
- Redis used purely for pub/sub messaging and short-lived status caching (TTL 86400s), not as a persistent queue
- Frontend SPA proxies API requests through Vite dev server
- No authentication layer on the app itself; relies on network-level isolation
## Layers
- Purpose: User interface for managing AI providers, WordPress sites, projects, posts, and monitoring job progress
- Location: `frontend/src/`
- Contains: React components (`.jsx`), API client module, CSS design system in `frontend/src/index.css`
- Depends on: Backend REST API at `POST /api/*`
- Purpose: HTTP request handling, input validation, CRUD operations
- Location: `backend/app/routers/`
- Contains: 5 routers -- `ai_providers.py`, `wp_sites.py`, `projects.py`, `posts.py`, `jobs.py`
- Depends on: Models layer, database module, Redis client, services layer
- All routers use `prefix="/api/..."` and return Pydantic-validated response dicts
- Purpose: External system integration and business logic
- Location: `backend/app/services/`
- Contains:
- Purpose: Background job processing via Redis pub/sub
- Location: `backend/app/workers/`
- Contains:
- Purpose: Request/response schemas and validation
- Location: `backend/app/models/`
- Contains: `wp_site.py`, `project.py`, `ai_provider.py`, `post.py`
- Pattern: Each module exports `XCreate`, `XUpdate`, `XResponse` classes
- Purpose: Raw async MongoDB operations via motor
- Location: `backend/app/database.py`
- Contains: 5 collection references -- `ai_providers_col`, `wp_sites_col`, `projects_col`, `posts_col`, `jobs_col`
- No ORM or repository pattern; routers call motor methods directly
## Data Flow
- Frontend: Local component state via `useState`; no global state management library (no Redux, no Zustand, no Context providers)
- Backend: MongoDB is the source of truth; Redis provides short-term caching (24h TTL) and pub/sub messaging
## Key Abstractions
- Purpose: Route AI calls through a pluggable provider system
- Examples: `backend/app/services/ai_service.py` -- `_call_openai()`, `_call_gemini()`, `_call_anthropic()` all called through `_call_ai()` dispatcher
- Pattern: Reads first available provider from DB, dispatches by `provider_type` field; each function returns `(text, token_count)` tuple
- Purpose: Track async multi-step content generation
- Examples: `backend/app/workers/tasks.py` -- `TASK_MAP` maps job types to handler functions
- Pattern: Each task follows the same structure: update status to `running` -> do work -> update post with results -> update status to `completed`/`failed`
- Purpose: Tracks the complete lifecycle of an AI-generated article
- Example: `backend/app/models/post.py` -- `PostResponse` model embeds `research_data`, `outline`, `sections`, `content`, `token_usage`, `jobs` array
- Pattern: Flat document with boolean flags (`research_done`, `content_done`, `thumbnail_done`, `sections_done`) to track pipeline progress
## Entry Points
- Location: `backend/app/main.py`
- Triggers: HTTP requests (mounted via Docker on port 8000, exposed as 8001)
- Responsibilities: Serves REST API, includes 5 routers, provides `/health` and `/` endpoints, enables CORS for `*` origins
- Run via: `uvicorn` (implicit; dependencies installed in `backend/requirements.txt`)
- Location: `backend/app/workers/redis_worker.py`
- Triggers: Messages on Redis pub/sub channel `wp_writer:jobs`
- Responsibilities: Listens for jobs, dispatches to task handlers via `TASK_MAP`, runs each job as a separate `asyncio` task
- Run via: `python -m app.workers.redis_worker`
- Location: `frontend/src/main.jsx`
- Triggers: Browser navigation
- Responsibilities: Renders `BrowserRouter` -> `App` (routes) -> `Layout` (sidebar + outlet)
- Pages: `/` (Dashboard), `/settings/ai-providers`, `/settings/wp-sites`, `/projects`, `/projects/:id`, `/posts/:id`
## Error Handling
- Uses FastAPI `HTTPException` with 400/404 status codes for validation and not-found cases
- Routers use `ObjectId()` casts which raise `bson.errors.InvalidId` if invalid (uncaught)
- Each task in `backend/app/workers/tasks.py` wraps logic in try/except
- On failure: updates job status to `"failed"`, stores error message in both MongoDB (jobs collection + embedded post job) and Redis
- Error output goes to `print()` and `traceback.print_exc()` -- no structured logging or error aggregation
- All async operations wrapped in try/catch with `alert('Error: ' + error.message)`
- `console.error` for non-user-facing errors
- No error boundaries defined
## Cross-Cutting Concerns
- Backend: `print()` statements and `traceback.print_exc()` in workers (`backend/app/workers/tasks.py`, `backend/app/workers/redis_worker.py`)
- Frontend: `console.error()` in catch blocks
- Backend: Pydantic models for request bodies (e.g. `backend/app/models/post.py`); provider_type validated via regex pattern `^(openai|gemini|anthropic)$`
- Frontend: Form validation via HTML `required` attributes; no programmatic validation
- No application-level authentication
- WordPress sites store credentials (username + application password); used with Basic Auth in `backend/app/services/wp_service.py`
- AI provider API keys stored in MongoDB; responses mask keys via `api_key_preview` pattern (`***` + last 4 chars)
- FastAPI configured with `allow_origins=["*"]` in `backend/app/main.py`
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
