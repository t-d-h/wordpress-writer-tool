# Codebase Structure

**Analysis Date:** 2026-04-07

## Directory Layout

```
wordpress-writer-tool/
├── backend/                    # Python FastAPI backend
│   ├── Dockerfile              # Backend container image
│   ├── requirements.txt        # Python dependencies
│   └── app/
│       ├── __init__.py
│       ├── main.py             # FastAPI app entry point
│       ├── config.py           # Environment settings
│       ├── database.py         # MongoDB connection + collections
│       ├── redis_client.py     # Redis pub/sub helpers
│       ├── models/             # Pydantic request/response schemas
│       │   ├── __init__.py
│       │   ├── ai_provider.py  # AIProviderCreate/Update/Response
│       │   ├── wp_site.py      # WPSiteCreate/Update/Response
│       │   ├── project.py      # ProjectCreate/Update/Response
│       │   └── post.py         # PostCreate/BulkPostCreate/Update/Response, Section, JobInfo, TokenUsage
│       ├── routers/            # FastAPI API routers (CRUD endpoints)
│       │   ├── __init__.py
│       │   ├── ai_providers.py # GET/POST/PUT/DELETE /api/ai-providers
│       │   ├── wp_sites.py     # GET/POST/PUT/DELETE /api/wp-sites
│       │   ├── projects.py     # GET/POST/PUT/DELETE /api/projects + /{id}/stats
│       │   ├── posts.py        # CRUD + bulk + action endpoints (publish, outline, content, etc.)
│       │   └── jobs.py         # GET /api/jobs/{id}, /by-post/{id}, /dashboard-stats
│       ├── services/           # Business logic / external integrations
│       │   ├── __init__.py
│       │   ├── ai_service.py   # AI research/outline/content generation (OpenAI, Gemini, Anthropic)
│       │   ├── wp_service.py   # WordPress REST API (publish/update posts, upload media)
│       │   ├── image_service.py # Gemini image generation (thumbnails, section images)
│       │   └── job_service.py  # Helper to create+queue jobs
│       └── workers/            # Background job processing
│           ├── __init__.py
│           ├── redis_worker.py # Redis pub/sub listener + task dispatcher
│           └── tasks.py        # Task implementations (research, outline, content, thumbnail, section_images, publish)
├── frontend/                   # React + Vite SPA
│   ├── Dockerfile              # Frontend container image
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.js          # Vite config (React plugin, /api proxy)
│   ├── eslint.config.js        # ESLint flat config
│   ├── public/                 # Static assets (served as-is)
│   └── src/
│       ├── main.jsx            # React entry point (BrowserRouter + StrictMode)
│       ├── App.jsx             # Route definitions
│       ├── App.css             # Vite default scaffold (unused)
│       ├── index.css           # Complete CSS design system (variables, components, animations)
│       ├── api/
│       │   └── client.js       # Axios instance + all API function exports
│       ├── components/         # React page components (one per route)
│       │   ├── Dashboard.jsx   # Dashboard page (job stats, 5s polling)
│       │   ├── Layout.jsx      # Shell layout (sidebar + main content outlet)
│       │   ├── Sidebar.jsx     # Navigation sidebar with collapsible sections
│       │   ├── Posts/
│       │   │   └── PostView.jsx    # Individual post view (pipeline, actions, preview)
│       │   ├── Projects/
│       │   │   ├── ProjectList.jsx # Projects list + create modal
│       │   │   └── ProjectDetail.jsx # Project detail + posts table + create modal
│       │   └── Settings/
│       │       ├── AIProviders.jsx # AI provider CRUD (OpenAI/Gemini/Anthropic)
│       │       └── WPSites.jsx     # WordPress site CRUD
│       └── assets/             # Static image assets (empty currently)
├── docker-compose.yml          # 3-service compose: backend, worker, frontend
└── .env                        # Environment variables (MongoDB URL, Redis URL, ports)
```

## Directory Purposes

**Backend (`backend/app/`):**
- Purpose: FastAPI application providing the REST API and background worker
- Contains: Routers (HTTP layer), services (business logic), workers (async job processing), models (schemas), database access (direct motor calls)
- Key files:
  - `backend/app/main.py` -- FastAPI app factory
  - `backend/app/config.py` -- Settings from environment variables
  - `backend/app/database.py` -- MongoDB async client and collection references
  - `backend/app/redis_client.py` -- Redis pub/sub and job status caching

**Frontend (`frontend/src/`):**
- Purpose: React SPA for managing the WordPress AI writer tool
- Contains: Route components under `components/`, centralized API client in `api/client.js`, CSS design system in `index.css`
- Key files:
  - `frontend/src/App.jsx` -- Routes for all pages
  - `frontend/src/api/client.js` -- All API calls (48 exports)
  - `frontend/src/index.css` -- 877-line CSS with design tokens and component styles

## Key File Locations

**Entry Points:**
- `backend/app/main.py` -- FastAPI HTTP server entry point
- `backend/app/workers/redis_worker.py` -- Worker process entry point (`python -m app.workers.redis_worker`)
- `frontend/src/main.jsx` -- React browser entry point

**Configuration:**
- `backend/app/config.py` -- Backend settings (MONGODB_URL, REDIS_URL, ports)
- `frontend/vite.config.js` -- Vite config with `/api` proxy to backend
- `docker-compose.yml` -- Docker services definition
- `backend/requirements.txt` -- Python dependencies
- `frontend/package.json` -- Node.js dependencies
- `.env` -- Environment variables (present in git; contains secrets)

**Core Logic:**
- `backend/app/services/ai_service.py` -- AI provider routing and prompt templates
- `backend/app/services/wp_service.py` -- WordPress REST API wrapper
- `backend/app/services/image_service.py` -- Gemini image generation
- `backend/app/workers/tasks.py` -- Background task implementations
- `backend/app/routers/posts.py` -- Post CRUD + 5 action endpoints (publish, outline, content, thumbnail, section_images)

**Testing:**
- No test files detected in the codebase

## Naming Conventions

**Files:**
- Backend Python: `snake_case.py` (e.g. `ai_providers.py`, `wp_service.py`, `redis_worker.py`)
- Frontend React: `PascalCase.jsx` (e.g. `PostView.jsx`, `ProjectDetail.jsx`, `AIProviders.jsx`)
- Frontend utility: `camelCase.js` (e.g. `client.js`, `config.js`)
- CSS: `index.css` (single design system file)

**Directories:**
- Backend: `snake_case/` (e.g. `models/`, `routers/`, `services/`, `workers/`)
- Frontend: `PascalCase/` for feature folders (e.g. `Posts/`, `Projects/`, `Settings/`), lowercase for core modules (e.g. `api/`, `assets/`)

**API Routes:**
- RESTful with kebab-case prefixes: `/api/ai-providers`, `/api/wp-sites`, `/api/projects`, `/api/posts`, `/api/jobs`
- Action-based POST routes: `/api/posts/{id}/publish`, `/api/posts/{id}/generate-outline`

**Model Classes:**
- `{Entity}Create`, `{Entity}Update`, `{Entity}Response` (e.g. `PostCreate`, `PostUpdate`, `PostResponse` in `backend/app/models/post.py`)

**CSS Custom Properties:**
- Design tokens: `--bg-primary`, `--text-primary`, `--accent-primary`, `--radius-md`, `--transition-fast`, etc. (defined in `frontend/src/index.css` root)

## Where to Add New Code

**New API Endpoint:**
- Add router handler in `backend/app/routers/<domain>.py`
- If new model needed, add Pydantic class to `backend/app/models/<domain>.py`
- Register router in `backend/app/main.py` via `app.include_router()`

**New Background Task:**
- Add task function in `backend/app/workers/tasks.py`
- Register in `TASK_MAP` in `backend/app/workers/redis_worker.py`
- Add API endpoint in `backend/app/routers/posts.py` to queue the task

**New Frontend Page:**
- Create component in `frontend/src/components/<Feature>/PageName.jsx`
- Add route in `frontend/src/App.jsx` under the `<Route element={<Layout />}>` block
- Add sidebar nav item in `frontend/src/components/Sidebar.jsx`
- Add API functions to `frontend/src/api/client.js`

**New API Client Function:**
- Add named export to `frontend/src/api/client.js` using the existing axios instance
- Pattern: `export const actionName = (id) => api.post(`/resource/${id}/action`);`

**New Service Integration:**
- Add service file in `backend/app/services/<name>.py`
- Import and call from worker tasks in `backend/app/workers/tasks.py` or from routers

**CSS / UI Changes:**
- Add component styles to `frontend/src/index.css` using CSS custom properties for colors/sizing
- Follow existing naming: `.page-*` for pages, `.stat-*` for stats, `.form-*` for forms, `.btn-*` for buttons

## Special Directories

**`__pycache__/` directories:**
- Purpose: Python bytecode cache
- Generated: Yes (by Python interpreter)
- Committed: No (should be in `.gitignore`)

**`backend/app/routers/__pycache__`, `workers/__pycache__`, etc.:**
- Purpose: Cached compiled Python for each submodule
- These are artifacts of running the application locally; not part of the source

## Environment Configuration

**Required environment variables:**
- `MONGODB_URL` -- MongoDB connection string (default: `mongodb://localhost:27017`)
- `MONGODB_DB` -- Database name (default: `wordpress_writer`)
- `REDIS_URL` -- Redis connection string (default: `redis://localhost:6379`)
- `BACKEND_HOST` -- Server bind host (default: `0.0.0.0`)
- `BACKEND_PORT` -- Server port (default: `8000`)
- `FRONTEND_URL` -- Frontend origin (default: `http://localhost:5173`)
- `VITE_API_URL` -- Frontend API base URL (optional; defaults to empty string, using relative proxy)

**Docker port mappings:**
- Backend: container 8000 -> host 8001
- Frontend: container 5173 -> host 5174

---

*Structure analysis: 2026-04-07*