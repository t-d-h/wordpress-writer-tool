# Codebase Concerns

**Analysis Date:** 2026-04-07

## Tech Debt

### API Keys Stored as Plain Text in MongoDB

- **Issue:** AI provider API keys and WordPress site credentials are stored unencrypted in MongoDB. The implementation plan explicitly notes "API Keys: Stored as plain text in MongoDB for this MVP."
- **Files:** `backend/app/models/ai_provider.py`, `backend/app/models/wp_site.py`, `backend/app/routers/ai_providers.py`, `backend/app/routers/wp_sites.py`
- **Impact:** If the database is compromised, all API keys and WP credentials are exposed. AI keys can be used to exhaust billing quotas. WP credentials allow full content control of client sites.
- **Fix approach:** Encrypt API keys at rest using a symmetric key (e.g., Fernet/cryptography library). Store the encryption key separately (env var or secrets manager). Decrypt only when making outbound API calls.

### Duplicate Job Creation Logic Between Router and Service

- **Issue:** The job creation pattern (create UUID, insert job record, publish to Redis, update post) is implemented inline in `backend/app/routers/posts.py` across five separate endpoints (`create_post`, `publish_post`, `generate_outline`, `generate_content`, `generate_thumbnail`, `generate_section_images`), while a helper `create_and_queue_job` exists in `backend/app/services/job_service.py` that does the same thing but is never called.
- **Files:** `backend/app/routers/posts.py` (lines 88-121, 183-210, 232-256, 266-290, 299-324, 334-358), `backend/app/services/job_service.py`
- **Impact:** Any fix to job creation must be applied in 6 places. The unused service will drift further from the router code, increasing confusion.
- **Fix approach:** Refactor all 6 endpoints to call `create_and_queue_job` from `job_service.py`. Remove the duplicated code blocks.

### Massive `posts` Router File (358 lines)

- **Issue:** `backend/app/routers/posts.py` contains all post CRUD, bulk creation, and 6 pipeline action endpoints in a single file. Each pipeline endpoint repeats the same 20-line job creation pattern.
- **Files:** `backend/app/routers/posts.py`
- **Impact:** Hard to scan, high cognitive load. Every new pipeline step adds ~25 more lines to this file.
- **Fix approach:** Extract pipeline action endpoints into a separate `backend/app/routers/post_actions.py` or use a service layer method.

### Frontend Package Name Mismatch

- **Issue:** The frontend `package.json` defines `"name": "frontend-temp"`, indicating this was scaffolded as a temporary project and never renamed.
- **Files:** `frontend/package.json`
- **Impact:** Cosmetic only, but indicates incomplete project setup.

### No URL Validation on WordPress Site

- **Issue:** `WPSiteCreate` model accepts any string for `url`. No regex or URL validator is applied. A malformed URL will cause runtime failures when the worker attempts to connect.
- **Files:** `backend/app/models/wp_site.py`
- **Impact:** Users can enter invalid URLs. Failure happens at publish time, not at input time, which is a poor UX and wastes API calls.
- **Fix approach:** Add `HttpUrl` from pydantic or a regex pattern validator on the `url` field.

## Security Considerations

### CORS Allows All Origins and Credentials

- **Issue:** `backend/app/main.py` configures `allow_origins=["*"]` together with `allow_credentials=True`. This is explicitly forbidden by the CORS spec and many browsers will reject it. In production, the wildcard allows any website to make authenticated cross-origin requests.
- **Files:** `backend/app/main.py` (lines 13-19)
- **Impact:** In development this works but masks a security gap. When credentials are added later, any malicious site can make authenticated requests on behalf of users.
- **Fix approach:** Set `allow_origins` to a specific list derived from `settings.FRONTEND_URL`.

### Basic Auth Credentials Sent to WordPress

- **Issue:** WordPress Basic Auth header is built using the application password. While WP application passwords are designed for this pattern, the password is transmitted with every request and held in memory for the duration of the upload. There are no request retries with backoff, so transient failures cause full re-authentication.
- **Files:** `backend/app/services/wp_service.py`
- **Impact:** Low risk for Basic Auth to WP (this is WP's recommended approach), but the `username` field is also stored in the database and exposed in API responses via `WPSiteResponse`.
- **Fix approach:** Remove `username` from the `WPSiteResponse` model to avoid exposing it to the frontend.

### No Input Sanitization on Topic/Content Fields

- **Issue:** User-supplied `topic` and `additional_requests` strings are interpolated directly into AI prompts without escaping. While not a traditional injection attack, a malicious prompt could attempt prompt injection to manipulate AI behavior.
- **Files:** `backend/app/services/ai_service.py` (lines 84-96, 115-120), `backend/app/services/image_service.py` (lines 50-76)
- **Impact:** Prompt injection could bypass system instructions, cause data exfiltration in responses, or generate unintended content.
- **Fix approach:** Apply input length limits and consider prompt template escaping. For an MVP, at minimum add a max-length validation on `topic` (e.g., 500 chars) and `additional_requests`.

### No Rate Limiting on API Endpoints

- **Issue:** All endpoints are publicly accessible with no rate limiting. An attacker could spam the `/api/posts` endpoint to create hundreds of AI jobs, draining API token budgets.
- **Files:** `backend/app/main.py`, all router files
- **Impact:** Unbounded cost exposure. Each job triggers at least one expensive AI API call.
- **Fix approach:** Add `slowapi` or a similar FastAPI rate limiter. Configure reasonable limits per endpoint.

### Health and Root Endpoints Return Service Info

- **Issue:** `/` endpoint returns internal service information including docs location. Combined with no authentication, this exposes the full API surface via Swagger UI.
- **Files:** `backend/app/main.py` (lines 34-40)
- **Impact:** Anyone who discovers the API URL can see every endpoint, request shape, and data model via `/docs`.
- **Fix approach:** Disable Swagger UI in production (`docs_url=None`, `redoc_url=None`) or protect it behind authentication.

## Performance Bottlenecks

### Extra MongoDB Read After Every Write for Token Calculation

- **Issue:** In `backend/app/workers/tasks.py`, every task (`run_research`, `run_outline`, `run_content`) performs a redundant `find_one` query immediately after updating to recalculate total tokens. This is 2 DB round-trips where 1 would suffice if the value was computed before the update.
- **Files:** `backend/app/workers/tasks.py` (lines 72-78, 118-124, 169-176)
- **Impact:** 50% unnecessary database load on every pipeline step. At scale with many concurrent jobs, this compounds.
- **Fix approach:** Calculate `total` before the update and include it in the same `$set` operation.

### N+1 Query Pattern in Project List

- **Issue:** `backend/app/routers/projects.py` fetches all projects, then loops through each to do a separate `wp_sites_col.find_one()` query for the WP site name. For N projects, this is N+1 MongoDB queries.
- **Files:** `backend/app/routers/projects.py` (lines 21-28)
- **Impact:** Gets worse linearly with number of projects. With 20 projects, 21 separate DB calls for a single request.
- **Fix approach:** Use MongoDB aggregation with `$lookup` to join projects with wp_sites in a single query, or cache site names.

### Sequential Section Content Generation (No Parallelism)

- **Issue:** `backend/app/services/ai_service.py`'s `generate_full_content` processes sections sequentially in a `for` loop. Each section waits for the previous one to complete before starting.
- **Files:** `backend/app/services/ai_service.py` (lines 206-219)
- **Impact:** A post with 6 sections requires 7 sequential AI calls (intro + 6 sections). If each takes 10 seconds, the user waits 70 seconds. Could be reduced to ~10-15 seconds with `asyncio.gather`.
- **Fix approach:** Use `asyncio.gather` to generate intro and all sections concurrently.

### No Job Retry Mechanism

- **Issue:** When a job fails (AI timeout, network error, etc.), it is marked as `failed` with no automatic retry. The user must manually trigger the step again.
- **Files:** `backend/app/workers/tasks.py` (all task handlers)
- **Impact:** Transient failures (e.g., AI API rate limiting, brief network blip) require manual intervention, degrading user experience.
- **Fix approach:** Implement exponential backoff retry (2-3 attempts) before marking a job as permanently failed.

### Image Filesystem Storage on Local /tmp

- **Issue:** Generated images are saved to `/tmp/wp_images` on the worker container's filesystem (`backend/app/services/image_service.py`). This is not persistent across container restarts, and the `/tmp` mount is shared between all containers.
- **Files:** `backend/app/services/image_service.py` (line 18), `backend/app/workers/tasks.py` (lines 199, 236)
- **Impact:** Images are lost on container restart. The stored `thumbnail_url` path becomes stale and WordPress upload will fail with a file-not-found error.
- **Fix approach:** Store images in persistent volume or cloud storage (S3, GCS). Update URL references accordingly.

### Section Image Generation Uploads Local Paths to WP

- **Issue:** `run_publish` in `backend/app/workers/tasks.py` only uploads the thumbnail image. Section images are generated and stored on disk but their `image_url` fields contain local `/tmp` paths that are never uploaded to WordPress.
- **Files:** `backend/app/workers/tasks.py` (lines 268-299)
- **Impact:** Section images are generated but never included in the published WordPress post. The content HTML does not reference them.
- **Fix approach:** Upload section images to WP media library before publishing, and embed the URLs into the content HTML.

### Concurrency Risk in Redis Worker

- **Issue:** `backend/app/workers/redis_worker.py` uses `asyncio.create_task(process_job(job_data))` to handle jobs, creating tasks that run independently. If the worker receives jobs faster than it can process them, there is no back-pressure mechanism. Failed tasks silently lose the exception (only print).
- **Files:** `backend/app/workers/redis_worker.py` (line 66)
- **Impact:** Under burst load, unbounded task creation can exhaust memory. Failed tasks leave jobs in `running` state forever.
- **Fix approach:** Use an `asyncio.Semaphore` to limit concurrent job processing, or switch to a proper queue (Celery, ARQ).

## Fragile Areas

### Bulk Post Creation Calls `create_post` in a Loop

- **Issue:** `backend/app/routers/posts.py` `create_bulk_posts` calls `create_post` sequentially in a Python `for` loop. Each call triggers a MongoDB insert, job creation, and Redis publish -- all sequentially.
- **Files:** `backend/app/routers/posts.py` (lines 134-144)
- **Impact:** Creating 50 bulk posts blocks the request thread for the entire duration. If request timeout is hit partway, some posts exist and others don't, with no transactional guarantee.
- **Fix approach:** Use MongoDB bulk operations or queue only (return 202 Accepted, create jobs asynchronously).

### No Cascade Handling for Deleted WP Sites

- **Issue:** Deleting a WordPress site (`DELETE /api/wp-sites/{site_id}`) only removes the site record. Any projects that reference this `wp_site_id` become broken -- every attempt to create a post or publish will fail with "WordPress site not found."
- **Files:** `backend/app/routers/wp_sites.py` (lines 62-67), `backend/app/models/wp_site.py`
- **Impact:** Orphaned projects silently break. User must manually fix or delete each affected project.
- **Fix approach:** Add a check for referencing projects before deletion, and either reject the deletion or cascade-delete dependent projects/posts.

### ObjectId Parsing Without Validation

- **Issue:** Routes accept `provider_id`, `site_id`, `project_id`, `post_id`, `job_id` as bare strings and pass them directly to `ObjectId()`. An invalid ObjectId string (not 24 hex chars) raises `bson.errors.InvalidId`, which propagates as a 500 Internal Server Error instead of 400/404.
- **Files:** All router files (`backend/app/routers/posts.py`, `backend/app/routers/projects.py`, `backend/app/routers/wp_sites.py`, `backend/app/routers/ai_providers.py`)
- **Impact:** Every endpoint with an ID parameter can return a 500 error on malformed input.
- **Fix approach:** Add a FastAPI exception handler for `InvalidId` or validate ObjectId format at the route parameter level.

### Dockerfile Uses `--reload` in Production

- **Issue:** `backend/Dockerfile` runs uvicorn with `--reload` flag. This is a development flag that watches filesystem for changes. In Docker, file changes do not occur (code is baked into the image), so the polling is wasted overhead.
- **Files:** `backend/Dockerfile` (line 10)
- **Impact:** Minor CPU/memory waste. Not suitable for production.
- **Fix approach:** Remove `--reload` from the Dockerfile CMD. Use docker-compose override or an env var to conditionally enable it for development only.

### Frontend Dockerfile Mismatch with package.json

- **Issue:** `frontend/Dockerfile` uses `node:18-alpine` but `package.json` and `package-lock.json` were generated with a newer Node version (lockfileVersion 3 indicates npm 9+). This can cause install version mismatches or missing packages.
- **Files:** `frontend/Dockerfile` (line 1)
- **Impact:** Build failures or subtle dependency resolution differences.
- **Fix approach:** Align the Dockerfile base image with the Node version used for development.

### Hardcoded Model Names

- **Issue:** AI service hardcodes model names: `gpt-4o`, `gemini-2.0-flash`, `claude-sonnet-4-20250514`. When these models are deprecated or new versions released, code changes are required.
- **Files:** `backend/app/services/ai_service.py` (lines 27, 40, 54)
- **Impact:** Every model update requires a code change and redeploy.
- **Fix approach:** Make model names configurable via environment variables or store them in the AI provider model (add a `model_name` field).

## Missing Critical Features

### No Authentication or Authorization

- **Issue:** The application has no login, no auth middleware, and no access control. Anyone with the API URL can read, create, and delete all data including AI keys and WP credentials.
- **Files:** `backend/app/main.py` (no auth middleware on any router)
- **Impact:** Complete lack of access control. If deployed to any network-accessible host, the application is fully exposed.
- **Fix approach:** Add API key auth, JWT, or session-based auth as a middleware. Protect all CRUD routes.

### No Test Coverage

- **Issue:** There are zero test files anywhere in the codebase. No unit tests, no integration tests, no E2E tests. The verification plan in `implementation_plan.md` relies entirely on manual browser testing and health checks.
- **Files:** N/A (no `*.test.*` or `*.spec.*` files found)
- **Impact:** Any refactoring or new feature risks breaking existing functionality undetected. No regression protection.
- **Fix approach:** Start with API route tests using `httpx.AsyncClient` and `pytest`. Add tests for critical paths: post creation, job processing, WP publishing.

### No Error Boundary on Frontend

- **Issue:** Frontend components catch errors in `try/catch` and log to `console.error`, but there is no React error boundary. A render-time error in any component crashes the entire app.
- **Files:** `frontend/src/components/Dashboard.jsx`, `frontend/src/components/Sidebar.jsx`, `frontend/src/components/Projects/ProjectDetail.jsx`, `frontend/src/components/Settings/AIProviders.jsx`, `frontend/src/components/Settings/WPSites.jsx`, `frontend/src/components/Projects/ProjectList.jsx`, `frontend/src/components/Posts/PostView.jsx`
- **Impact:** A single component crash takes down the entire SPA.
- **Fix approach:** Add a top-level React error boundary component that displays a fallback UI.

### No Pagination on List Endpoints

- **Issue:** `GET /api/posts/by-project/{project_id}`, `GET /api/projects`, and `GET /api/wp-sites` return all records with no pagination.
- **Files:** `backend/app/routers/posts.py` (line 43), `backend/app/routers/projects.py` (line 24), `backend/app/routers/wp_sites.py` (line 24)
- **Impact:** Performance degrades linearly with data volume. Large projects with hundreds of posts will make the frontend load very slowly.
- **Fix approach:** Add `skip` and `limit` query parameters with a default page size (e.g., 50).

## Scaling Limits

### Redis Pub/Sub Is Not a Job Queue

- **Issue:** The worker uses Redis pub/sub for job dispatch. Pub/sub is fire-and-forget: if the worker is not running or crashes while a message is published, that message is lost permanently.
- **Files:** `backend/app/redis_client.py`, `backend/app/workers/redis_worker.py`
- **Impact:** Jobs are lost if the worker restarts or is temporarily unavailable. No job persistence, no retry, no dead-letter queue.
- **Fix approach:** Migrate to Redis Streams, RQ, Celery, or ARQ for durable job queues with retry and persistence.

### No Indexing on MongoDB Collections

- **Issue:** No explicit indexes are created on any collection. Queries on `project_id` in the `posts` collection, `job_id` in the `jobs` collection, and `provider_type` in `ai_providers` will all perform full collection scans.
- **Files:** `backend/app/database.py`
- **Impact:** Performance degrades significantly as data grows.
- **Fix approach:** Add indexes: `posts.project_id`, `jobs.job_id`, `jobs.post_id`, `ai_providers.provider_type`. Can be done via pymongo `create_index` at startup or migration.

## Dependencies at Risk

### Pinned Pymongo Upper Bound

- **Issue:** `requirements.txt` pins `pymongo>=4.7,<4.10`. This upper constraint could block updates to `motor` (which depends on pymongo) and introduces a dependency ceiling that may conflict with future MongoDB driver releases.
- **Files:** `backend/requirements.txt`
- **Impact:** Dependency resolution failures when mongo or motor updates require newer pymongo versions.
- **Fix approach:** Relax the constraint or use a compatible release operator (`pymongo>=4.7`).

## Test Coverage Gaps

**Entire Codebase:**
- **What is not tested:** Every backend endpoint, every service function, every worker task, every frontend component, the job pipeline, the WordPress publishing flow, the image generation, error handling paths.
- **Risk:** Any change could introduce regressions in AI integration, job processing, or WP publishing that go unnoticed.
- **Priority:** High -- this is the most critical gap for an MVP-to-production transition.

---

*Concerns audit: 2026-04-07*
