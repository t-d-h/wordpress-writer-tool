# Architecture

**Analysis Date:** 2026-04-07

## Pattern Overview

**Overall:** Layered monorepo with two independently deployed services (backend API + worker) and a frontend SPA, communicating via shared Redis pub/sub for async job processing.

**Key Characteristics:**
- Two Docker containers for the backend: one FastAPI HTTP server (`backend`) + one Redis pub/sub consumer worker (`worker`)
- MongoDB as the single data store (both direct documents via motor and job records)
- Redis used purely for pub/sub messaging and short-lived status caching (TTL 86400s), not as a persistent queue
- Frontend SPA proxies API requests through Vite dev server
- No authentication layer on the app itself; relies on network-level isolation

## Layers

**Frontend (React SPA):**
- Purpose: User interface for managing AI providers, WordPress sites, projects, posts, and monitoring job progress
- Location: `frontend/src/`
- Contains: React components (`.jsx`), API client module, CSS design system in `frontend/src/index.css`
- Depends on: Backend REST API at `POST /api/*`

**API Layer (FastAPI Routers):**
- Purpose: HTTP request handling, input validation, CRUD operations
- Location: `backend/app/routers/`
- Contains: 5 routers -- `ai_providers.py`, `wp_sites.py`, `projects.py`, `posts.py`, `jobs.py`
- Depends on: Models layer, database module, Redis client, services layer
- All routers use `prefix="/api/..."` and return Pydantic-validated response dicts

**Service Layer:**
- Purpose: External system integration and business logic
- Location: `backend/app/services/`
- Contains:
  - `ai_service.py` -- research, outline, content generation (supports OpenAI GPT-4o, Gemini, Anthropic Claude)
  - `wp_service.py` -- WordPress REST API integration (publish/update posts, upload media)
  - `image_service.py` -- Gemini image generation for thumbnails and section images
  - `job_service.py` -- helper to create and queue job records

**Worker Layer:**
- Purpose: Background job processing via Redis pub/sub
- Location: `backend/app/workers/`
- Contains:
  - `redis_worker.py` -- subscribes to `wp_writer:jobs` channel, dispatches to task handlers
  - `tasks.py` -- 6 task types: `research`, `outline`, `content`, `thumbnail`, `section_images`, `publish`

**Model Layer (Pydantic):**
- Purpose: Request/response schemas and validation
- Location: `backend/app/models/`
- Contains: `wp_site.py`, `project.py`, `ai_provider.py`, `post.py`
- Pattern: Each module exports `XCreate`, `XUpdate`, `XResponse` classes

**Data Access (Direct MongoDB):**
- Purpose: Raw async MongoDB operations via motor
- Location: `backend/app/database.py`
- Contains: 5 collection references -- `ai_providers_col`, `wp_sites_col`, `projects_col`, `posts_col`, `jobs_col`
- No ORM or repository pattern; routers call motor methods directly

## Data Flow

**Post Creation Pipeline:**

1. User submits a topic via `POST /api/posts` at `backend/app/routers/posts.py`
2. Router creates a post document in `posts_col`, creates an initial `research` job in `jobs_col`, pushes job info into the post's embedded `jobs` array
3. Router publishes the job payload to Redis channel `wp_writer:jobs` via `backend/app/redis_client.py`
4. Worker in `backend/app/workers/redis_worker.py` receives the message on the pub/sub channel
5. Worker dispatches to the appropriate handler via `TASK_MAP` in `backend/app/workers/redis_worker.py`
6. Task handler (e.g. `run_research` in `backend/app/workers/tasks.py`) calls `ai_service.research_topic()`
7. `ai_service.py` reads the first available AI provider from `ai_providers_col`, routes to the correct SDK (OpenAI, Gemini, Anthropic)
8. Task writes results back to `posts_col`, updates the embedded job status, and caches status in Redis via `set_job_status()`
9. Subsequent steps (outline, content, thumbnail, publish) are triggered via separate API calls (`POST /api/posts/{id}/generate-outline`, etc.) -- the pipeline is NOT automatic; each step is manually queued

**Data Publishing to WordPress:**

1. User clicks "Publish" on a post, triggering `POST /api/posts/{id}/publish` at `backend/app/routers/posts.py`
2. Router queues a `publish` job to Redis
3. `run_publish` in `backend/app/workers/tasks.py` processes the job
4. `wp_service.upload_media()` uploads the thumbnail to WordPress media library
5. `wp_service.create_wp_post()` creates the post via `wp-json/wp/v2/posts` with Basic Auth
6. The `wp_post_id` is stored back on the post document

**Frontend Data Fetching:**

1. Vite dev server proxies `/api/*` requests to `http://localhost:8000`
2. `frontend/src/api/client.js` provides named exports for all REST endpoints (e.g. `getPostsByProject()`, `publishPost()`)
3. Components use `useEffect` + `useState` to load data; polling is used for job status (5-second interval on Dashboard, 3-second on PostView when jobs are pending)

**State Management:**
- Frontend: Local component state via `useState`; no global state management library (no Redux, no Zustand, no Context providers)
- Backend: MongoDB is the source of truth; Redis provides short-term caching (24h TTL) and pub/sub messaging

## Key Abstractions

**AI Provider Abstraction:**
- Purpose: Route AI calls through a pluggable provider system
- Examples: `backend/app/services/ai_service.py` -- `_call_openai()`, `_call_gemini()`, `_call_anthropic()` all called through `_call_ai()` dispatcher
- Pattern: Reads first available provider from DB, dispatches by `provider_type` field; each function returns `(text, token_count)` tuple

**Job Pipeline Abstraction:**
- Purpose: Track async multi-step content generation
- Examples: `backend/app/workers/tasks.py` -- `TASK_MAP` maps job types to handler functions
- Pattern: Each task follows the same structure: update status to `running` -> do work -> update post with results -> update status to `completed`/`failed`

**Post Model:**
- Purpose: Tracks the complete lifecycle of an AI-generated article
- Example: `backend/app/models/post.py` -- `PostResponse` model embeds `research_data`, `outline`, `sections`, `content`, `token_usage`, `jobs` array
- Pattern: Flat document with boolean flags (`research_done`, `content_done`, `thumbnail_done`, `sections_done`) to track pipeline progress

## Entry Points

**FastAPI Server (`backend`):**
- Location: `backend/app/main.py`
- Triggers: HTTP requests (mounted via Docker on port 8000, exposed as 8001)
- Responsibilities: Serves REST API, includes 5 routers, provides `/health` and `/` endpoints, enables CORS for `*` origins
- Run via: `uvicorn` (implicit; dependencies installed in `backend/requirements.txt`)

**Redis Worker (`worker`):**
- Location: `backend/app/workers/redis_worker.py`
- Triggers: Messages on Redis pub/sub channel `wp_writer:jobs`
- Responsibilities: Listens for jobs, dispatches to task handlers via `TASK_MAP`, runs each job as a separate `asyncio` task
- Run via: `python -m app.workers.redis_worker`

**React Frontend:**
- Location: `frontend/src/main.jsx`
- Triggers: Browser navigation
- Responsibilities: Renders `BrowserRouter` -> `App` (routes) -> `Layout` (sidebar + outlet)
- Pages: `/` (Dashboard), `/settings/ai-providers`, `/settings/wp-sites`, `/projects`, `/projects/:id`, `/posts/:id`

## Error Handling

**Strategy:** Try/except per-task with status updates to MongoDB + Redis; client errors via `alert()` in frontend.

**Backend API:**
- Uses FastAPI `HTTPException` with 400/404 status codes for validation and not-found cases
- Routers use `ObjectId()` casts which raise `bson.errors.InvalidId` if invalid (uncaught)

**Worker Tasks:**
- Each task in `backend/app/workers/tasks.py` wraps logic in try/except
- On failure: updates job status to `"failed"`, stores error message in both MongoDB (jobs collection + embedded post job) and Redis
- Error output goes to `print()` and `traceback.print_exc()` -- no structured logging or error aggregation

**Frontend:**
- All async operations wrapped in try/catch with `alert('Error: ' + error.message)`
- `console.error` for non-user-facing errors
- No error boundaries defined

## Cross-Cutting Concerns

**Logging:**
- Backend: `print()` statements and `traceback.print_exc()` in workers (`backend/app/workers/tasks.py`, `backend/app/workers/redis_worker.py`)
- Frontend: `console.error()` in catch blocks

**Validation:**
- Backend: Pydantic models for request bodies (e.g. `backend/app/models/post.py`); provider_type validated via regex pattern `^(openai|gemini|anthropic)$`
- Frontend: Form validation via HTML `required` attributes; no programmatic validation

**Authentication:**
- No application-level authentication
- WordPress sites store credentials (username + application password); used with Basic Auth in `backend/app/services/wp_service.py`
- AI provider API keys stored in MongoDB; responses mask keys via `api_key_preview` pattern (`***` + last 4 chars)

**CORS:**
- FastAPI configured with `allow_origins=["*"]` in `backend/app/main.py`

---

*Architecture analysis: 2026-04-07*