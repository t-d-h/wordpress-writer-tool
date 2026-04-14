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
- Python 3.11 - Backend API, AI services, async workers
- JavaScript (ES2020) with JSX - React frontend application
- HTML/CSS - Frontend styling
- None detected
## Runtime
- Python 3.11-slim (Docker container) - Backend runtime
- Node.js with Vite 5.4 - Frontend dev/build server
- Backend: `pip` via `requirements.txt`
- Frontend: `npm` via `package.json`
- Lockfile: `package-lock.json` present (frontend), no `requirements.lock` (backend)
## Frameworks
- FastAPI 0.115.0 - Backend REST API framework (`backend/app/main.py`)
- React 18.3 - Frontend UI framework
- Vite 5.4 - Frontend build tool and dev server
- React Router 7.14 - Frontend client-side routing
- Not detected
- Uvicorn 0.30 - ASGI server for FastAPI
- Docker Compose - Multi-container orchestration (backend, worker, frontend)
- ESLint 9.13 - Frontend linting (`frontend/eslint.config.js`)
## Key Dependencies
- `openai` >=1.60.0 - OpenAI API client (GPT-4o model used)
- `google-genai` 1.5.0 - Google Gemini API client (content + image generation)
- `anthropic` 0.39.0 - Anthropic API client (Claude Sonnet 4 model used)
- `httpx` >=0.28.1 - Async HTTP client for WordPress REST API calls
- `axios` 1.14.0 - Frontend HTTP client for API communication
- `motor` 3.6.0 - Async MongoDB driver
- `pymongo` >=4.7,<4.10 - MongoDB client library
- `redis` 5.0.0 - Async Redis client for pub/sub messaging
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
- `VITE_API_URL` - Frontend API base URL (default `http://localhost:8000`)
- `backend/Dockerfile` - Python 3.11-slim, installs requirements, runs uvicorn
- `frontend/Dockerfile` - Node.js 18-alpine, installs deps, runs Vite dev server
- `worker/Dockerfile` - Python 3.11-slim, installs requirements, runs worker
- `docker-compose.yml` - Defines three services: `backend` (port 8001), `worker`, `frontend` (port 5174)
- `frontend/vite.config.js` - Vite config with React plugin and API proxy
- `frontend/eslint.config.js` - ESLint 9.x flat config with React plugins
## Platform Requirements
- Docker and Docker Compose
- Python 3.11
- Node.js (for frontend dev)
- Targets Docker deployment via docker-compose
- MongoDB and Redis must be provisioned separately (MongoDB 7 and Redis 7 commented out in docker-compose)
- External WordPress site(s) with REST API and application passwords enabled
- AI provider API keys (OpenAI, Gemini, or Anthropic)
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Backend Python: `snake_case.py` (e.g., `ai_service.py`, `wp_service.py`, `redis_client.py`)
- Frontend React: `PascalCase.jsx` (e.g., `Dashboard.jsx`, `ProjectDetail.jsx`, `AIProviders.jsx`)
- Config files: `kebab-case.js` (e.g., `eslint.config.js`, `vite.config.js`)
- Backend Python: `snake_case` (e.g., `research_topic()`, `generate_outline()`, `format_post()`)
- Private/protected Python functions prefixed with underscore: `_get_gemini_key()`, `_call_openai()`, `_update_job_status()`
- Frontend handlers: `camelCase` (e.g., `handleSubmit()`, `handleDelete()`, `handleEdit()`, `load()`, `handleAction()`)
- Both codebases: `camelCase` for state/locals (`api_key`, `is_running()`, `showModal`, `editingId`)
- Constants: `UPPER_SNAKE_CASE` in Python (`JOB_CHANNEL`, `TASK_MAP`) and `ALL_CAPS` in JS (`API_BASE`)
- Database collection names use `snake_case` suffix `_col` (e.g., `posts_col`, `jobs_col`, `ai_providers_col`)
- React components use `PascalCase` matching filename exactly (e.g., `export default function AIProviders()`)
- Helper sub-components placed in same file with lowercase or PascalCase (e.g., `BoolBadge` in `ProjectDetail.jsx`)
- BEM-like naming with dashes: `.empty-state`, `.stat-card`, `.page-title`, `.modal-overlay`
- State modifiers: `.stat-card.pending`, `.stat-card.failed`, `.pipeline-step.done`
## Code Style
- Frontend: ESLint 9.x flat config with recommended settings
- Backend: No explicit linter/config detected (no `.flake8`, `.pylintrc`, `pyproject.toml`, or `ruff.toml`)
- Code follows PEP 8 conventions
- Frontend: `frontend/eslint.config.js`
- Ruleset: ESLint 9.x flat config with recommended settings
- React plugin: `eslint-plugin-react`, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`
- EcmaVersion: 2020, JSX enabled
- Key rule override: `'react/jsx-no-target-blank': 'off'`
- Exports only: `'react-refresh/only-export-components': 'warn'` with `allowConstantExport: true`
- Run: `npm run lint` -> `eslint .`
- No explicit linter configured
- Code follows PEP 8 conventions
- Imports ordered: stdlib first, then third-party, then local `app.*` modules
## Import Organization
- No path aliases configured
- All imports use relative paths or full module paths
## Error Handling
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
- Backend: `print()` statements for logging (no logging framework)
- Backend: Format: `[WORKER] message`, `[TASK] message`
- Backend: Uses `traceback.print_exc()` for stack traces
- Frontend: `console.error()` for error logging
- Frontend: No `console.log()` observed in normal operation
- Workers: Python logging module with structured logging (`worker/app/logging_config.py`)
- Workers: Logger format: `[SECTION] message` (e.g., `[RESEARCH] Starting research for post {post_id}`)
- No structured logging in backend API layer
- Backend: `print()` for debugging and status messages
- Workers: `logger.info()`, `logger.error()`, `logger.warning()`, `logger.exception()`
- Frontend: `console.error()` in catch blocks
- No centralized logging configuration for backend API
## Comments
- Docstrings on all public functions (triple-quote)
- Module-level docstrings in service files: `"""AI Service — handles research..."""`
- No inline comments in most code, occasional brief notes
- No JSDoc or inline comments in components
- Minimal comments — one observed: `// Auto-refresh while jobs are running` in `PostView.jsx`
- Not used in frontend
- No type annotations in JavaScript/JSX files
- PropTypes used for component prop validation (e.g., `BoolBadge.propTypes`, `JobStatusBadge.propTypes`)
## Function Design
- Backend services: Functions can be long (e.g., `run_publish()` is 100+ lines)
- Frontend components: Can be large (e.g., `ProjectDetail.jsx` is 775 lines)
- No strict size guidelines enforced
- Backend: Services use many parameters, not data classes (e.g., `create_wp_post(project_id, title, content, meta_description, thumbnail_media_id, status)`)
- Backend: Return tuples for multi-return values: `tuple[str, int]` for `(response, tokens)`
- Frontend: Components use multiple `useState` hooks for form state
- Frontend: Form state as object: `setForm({ ...form, field: value })`
- Frontend: No useReducer, no form libraries (react-hook-form, formik)
- Backend: Pydantic models used for request/response validation
- Backend: Pattern: `<Model>Create` — creation payload, `<ModelUpdate>` — partial update (`Optional` fields), `<ModelResponse>` — response with computed/derived fields
- Frontend: API functions return axios response objects
- Frontend: Components render JSX directly
## Module Design
- Python modules export functions directly (no `__all__` defined except in `__init__.py` files which are mostly empty)
- Frontend: All components are default exports, API functions are named exports in `frontend/src/api/client.js`
- Frontend: `api/client.js` assembles all API methods and exports them individually plus default axios instance
- `__init__.py` files exist in all packages but are empty or contain only `pass`
- Explicit imports used, not star imports from packages
- Frontend: `frontend/src/api/client.js` acts as a barrel file for API functions
- Backend: `__init__.py` files are mostly empty, not used as barrel files
## CSS/Styling Conventions
- Design system defined in `frontend/src/index.css` with CSS custom properties
- Color variables: `--bg-primary`, `--text-primary`, `--accent-primary`, etc.
- Size variables: `--sidebar-width`, `--radius-sm`, `--radius-md`, etc.
- Transition variables: `--transition-fast`, `--transition-normal`, `--transition-slow`
- Shadow variables: `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-glow`
- BEM-like naming with dashes: `.empty-state`, `.stat-card`, `.page-title`, `.modal-overlay`
- State modifiers: `.stat-card.pending`, `.stat-card.failed`, `.pipeline-step.done`
- Utility classes: `.loading-page`, `.loading-spinner`, `.btn`, `.btn-primary`, `.btn-secondary`
- Components use inline styles for dynamic values (e.g., `style={{ marginBottom: 20 }}`)
- CSS classes for static styling
- No CSS-in-JS library used
- No styled-components or emotion
- Not explicitly observed in code
- No media queries in the CSS files reviewed
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
## Layers
### Backend Layer (`backend/`)
- **API Layer**: FastAPI routers in `backend/app/routers/` handle HTTP requests
- **Service Layer**: Business logic in `backend/app/services/` (AI, WordPress, job management)
- **Model Layer**: Pydantic models in `backend/app/models/` for request/response validation
- **Data Layer**: MongoDB access via Motor async driver in `backend/app/database.py`
### Frontend Layer (`frontend/`)
- **UI Layer**: React components in `frontend/src/components/`
- **API Layer**: Axios client in `frontend/src/api/client.js`
- **Routing**: React Router for client-side navigation
### Worker Layer (`worker/`)
- **Job Processing**: Redis pub/sub consumer in `backend/app/workers/`
- **Task Execution**: Async task handlers in `backend/app/workers/tasks.py`
## Data Flow
## Key Abstractions
### Job System
- Redis pub/sub for job distribution
- Job types: research, outline, content, thumbnail, section_images, publish
- Status tracking: pending, running, completed, failed
- Token usage tracking per job type
### AI Provider Abstraction
- Pluggable provider system (OpenAI, Gemini, Anthropic)
- Unified interface via `ai_service.py`
- Provider-specific implementations in `_call_openai()`, `_call_gemini()`, `_call_anthropic()`
### WordPress Integration
- REST API client in `wp_service.py`
- Application password authentication
- Media upload and post publishing
## Entry Points
### Backend
- `backend/app/main.py` - FastAPI application entry point
- `backend/app/workers/redis_worker.py` - Redis worker entry point
### Frontend
- `frontend/src/main.jsx` - React application entry point
- `frontend/src/App.jsx` - Root component with routing
## Component Boundaries
### Backend Components
- **Routers**: HTTP endpoint handlers, no business logic
- **Services**: Business logic, external API calls
- **Models**: Request/response validation
- **Database**: MongoDB operations only
### Frontend Components
- **Layout**: Sidebar navigation and page structure
- **Dashboard**: Overview and statistics
- **Projects**: Project management and post creation
- **Posts**: Post viewing and job monitoring
- **Settings**: AI provider and WordPress site configuration
## Build Order Dependencies
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
