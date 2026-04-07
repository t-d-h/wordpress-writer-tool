# External Integrations

**Analysis Date:** 2026-04-07

## APIs & External Services

**AI Providers (multi-provider, configurable via database):**
- **OpenAI** - Text generation (chat completions)
  - SDK: `openai` package (`AsyncOpenAI` client)
  - Model: `gpt-4o`
  - Auth: `api_key` stored in MongoDB `ai_providers` collection
  - Used in: `backend/app/services/ai_service.py`

- **Google Gemini** - Text generation + image generation
  - SDK: `google-genai` package
  - Models: `gemini-2.0-flash` (text), `gemini-2.0-flash-preview-image-generation` (images)
  - Auth: `api_key` stored in MongoDB `ai_providers` collection
  - Used in: `backend/app/services/ai_service.py`, `backend/app/services/image_service.py`

- **Anthropic** - Text generation
  - SDK: `anthropic` package (`AsyncAnthropic` client)
  - Model: `claude-sonnet-4-20250514`
  - Auth: `api_key` stored in MongoDB `ai_providers` collection
  - Used in: `backend/app/services/ai_service.py`

**WordPress REST API:**
- External WordPress sites publish posts via their REST API
  - SDK/Client: `httpx` async HTTP client
  - Auth: Basic Auth (username + WordPress application password), header: `Authorization: Basic {base64}`
  - Endpoints used:
    - `{site_url}/wp-json/wp/v2/posts` - Create/update posts
    - `{site_url}/wp-json/wp/v2/media` - Upload media (featured images)
  - Used in: `backend/app/services/wp_service.py`

## Data Storage

**Databases:**
- **MongoDB** (motor/async driver)
  - Connection: `MONGODB_URL` env var
  - Database: configured via `MONGODB_DB` env var (default: `wordpress_writer`)
  - Client: `AsyncIOMotorClient` (`backend/app/database.py`)
  - Collections:
    - `ai_providers` - AI provider configurations
    - `wp_sites` - WordPress site configurations
    - `projects` - Writing projects
    - `posts` - Generated blog posts and their metadata
    - `jobs` - Background job records

- **Redis** (redis.asyncio/async driver)
  - Connection: `REDIS_URL` env var
  - Client: `redis.asyncio.from_url` (`backend/app/redis_client.py`)
  - Usage:
    - Pub/Sub channel `wp_writer:jobs` - Job queue for async processing
    - Key pattern `job:{job_id}` - Job status cache (24h TTL)
  - Used in: `backend/app/redis_client.py`, `backend/app/workers/redis_worker.py`

**File Storage:**
- Local filesystem only (`/tmp/wp_images`)
- Generated images (thumbnails, section images) saved locally via `image_service.py`
- No cloud storage integration detected

**Caching:**
- Redis is used for job status caching (TTL: 86400 seconds / 24 hours)
- No general-purpose HTTP caching layer

## Authentication & Identity

**App Auth:**
- No user authentication system detected
- CORS is wide open (`allow_origins: ["*"]`) in `backend/app/main.py`

**Service Auth:**
- WordPress: Basic Auth with application passwords, stored per WP site record
- AI providers: API keys stored in MongoDB `ai_providers` collection (only last 4 chars exposed in responses via `api_key_preview` field)

## Monitoring & Observability

**Error Tracking:**
- None detected

**Logs:**
- stdout via `print()` statements in worker (`backend/app/workers/redis_worker.py`, `backend/app/workers/tasks.py`)
- No structured logging framework
- No log levels or log rotation configured

## CI/CD & Deployment

**Hosting:**
- Self-hosted via Docker Compose

**CI Pipeline:**
- None detected

**Docker Compose Services:**
| Service | Port | Purpose |
|---------|------|---------|
| `backend` | 8001:8000 | FastAPI REST API |
| `worker` | none | Redis pub/sub job processor |
| `frontend` | 5174:5173 | React Vite dev server |

## Environment Configuration

**Required env vars:**
- `MONGODB_URL` - MongoDB connection string
- `MONGODB_DB` - Database name
- `REDIS_URL` - Redis connection string
- `BACKEND_HOST` - Backend bind host
- `BACKEND_PORT` - Backend port
- `FRONTEND_URL` - Frontend URL (CORS)
- `VITE_API_URL` - Frontend API proxy target

**Secrets location:**
- `.env` file at project root (git-tracked per git status showing `M .env`)
- AI API keys stored in MongoDB
- WordPress application passwords stored in MongoDB

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- WordPress REST API calls (posts and media uploads) initiated by the publish job
  - Target: configurable WordPress site URLs
  - Initiated from: `backend/app/services/wp_service.py`

## API Routes Summary

**Backend API (`backend/app/routers/`):**
| Router | Purpose | Key endpoints |
|--------|---------|---------------|
| `ai_providers.py` | Manage AI provider configs | CRUD for providers |
| `wp_sites.py` | Manage WordPress site configs | CRUD for WP sites |
| `projects.py` | Manage writing projects | CRUD + stats |
| `posts.py` | Manage blog posts | CRUD + generate/publish actions |
| `jobs.py` | Query job status | Dashboard stats, job details |
| `main.py` | Root | `/health`, `/` |

**Frontend API Client (`frontend/src/api/client.js`):**
- Axios-based client with base URL from `VITE_API_URL`
- Dev proxy configured: `/api` -> `http://localhost:8000` (via `frontend/vite.config.js`)

---

*Integration audit: 2026-04-07*
