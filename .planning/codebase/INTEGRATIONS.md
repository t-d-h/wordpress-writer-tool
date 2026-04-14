# External Integrations

**Analysis Date:** 2026-04-14

## APIs & External Services

**AI Content Generation:**
- OpenAI API - Text generation (GPT-4o model) and image generation (DALL-E 3)
  - SDK/Client: `openai` >=1.60.0
  - Auth: `api_key` stored in MongoDB (`ai_providers` collection)
  - Implementation: `backend/app/services/ai_service.py` (`_call_openai()`)
  - Image generation: `backend/app/services/image_service.py` (`generate_image_with_openai()`)

- Google Gemini API - Text generation (gemini-2.0-flash) and image generation (gemini-2.0-flash-exp-image-generation)
  - SDK/Client: `google-genai` 1.5.0
  - Auth: `api_key` stored in MongoDB (`ai_providers` collection)
  - Implementation: `backend/app/services/ai_service.py` (`_call_gemini()`)
  - Image generation: `backend/app/services/image_service.py` (`generate_image_with_gemini()`)

- Anthropic API - Text generation (claude-sonnet-4-20250514)
  - SDK/Client: `anthropic` 0.39.0
  - Auth: `api_key` stored in MongoDB (`ai_providers` collection)
  - Implementation: `backend/app/services/ai_service.py` (`_call_anthropic()`)

- OpenAI-compatible APIs - Custom endpoints for text generation
  - SDK/Client: `openai` >=1.60.0 (with custom `base_url`)
  - Auth: `api_key` and `api_url` stored in MongoDB
  - Implementation: `backend/app/services/ai_service.py` (`_call_openai()` with `base_url`)

**WordPress REST API:**
- WordPress Sites - Content publishing and media upload
  - SDK/Client: `httpx` >=0.28.1 (async HTTP client)
  - Auth: Basic Auth with username + application password (stored in `wp_sites` collection)
  - Implementation: `backend/app/services/wp_service.py`
  - Endpoints used: `/wp-json/wp/v2/posts`, `/wp-json/wp/v2/media`, `/wp-json/wp/v2/categories`, `/wp-json/wp/v2/tags`

## Data Storage

**Databases:**
- MongoDB
  - Connection: `MONGODB_URL` environment variable
  - Client: `motor` 3.6.0 (async driver) + `pymongo` >=4.7,<4.10
  - Collections: `ai_providers`, `wp_sites`, `projects`, `posts`, `jobs`, `default_models`
  - Implementation: `backend/app/database.py`

**File Storage:**
- Local filesystem only - Generated images stored in `/tmp/wp_images` directory
  - Implementation: `backend/app/services/image_service.py`
  - Images are resized to 150x150 squares using Pillow

**Caching:**
- Redis - Pub/sub messaging and short-lived status caching (TTL 86400s)
  - Connection: `REDIS_URL` environment variable
  - Client: `redis` 5.0.0 (async client)
  - Implementation: `backend/app/redis_client.py`, `worker/app/redis_client.py`
  - Channel: `wp_writer:jobs` for job queue messaging

## Authentication & Identity

**Auth Provider:**
- Custom - No application-level authentication
  - Implementation: Relies on network-level isolation
  - WordPress sites use Basic Auth with username + application password
  - AI providers use API keys stored in MongoDB (masked in responses via `api_key_preview` pattern)

## Monitoring & Observability

**Error Tracking:**
- None - No error tracking service integrated

**Logs:**
- Backend: `print()` statements and `traceback.print_exc()` for stack traces
- Worker: Custom logging via `app.logging_config.setup_logging()`
- Frontend: `console.error()` in catch blocks
- No structured logging or log aggregation service

## CI/CD & Deployment

**Hosting:**
- Docker Compose - Multi-container deployment
  - Services: `backend` (FastAPI), `worker` (Redis consumer), `frontend` (Vite dev server)
  - Configuration: `docker-compose.yml`

**CI Pipeline:**
- None - No CI/CD service configured

## Environment Configuration

**Required env vars:**
- `MONGODB_URL` - MongoDB connection string
- `MONGODB_DB` - Database name (default: `wordpress_writer`)
- `REDIS_URL` - Redis connection string
- `BACKEND_HOST` - Backend bind host (default: `0.0.0.0`)
- `BACKEND_PORT` - Backend port (default: `8000`)
- `FRONTEND_URL` - Frontend URL for CORS (default: `http://localhost:5173`)
- `VITE_API_URL` - Frontend API base URL (default: `http://localhost:8000`)

**Secrets location:**
- `.env` file at project root (loaded by Docker Compose)
- AI provider API keys stored in MongoDB (`ai_providers` collection)
- WordPress credentials stored in MongoDB (`wp_sites` collection)

## Webhooks & Callbacks

**Incoming:**
- None - No webhook endpoints defined

**Outgoing:**
- None - No outgoing webhooks or callbacks

---

*Integration audit: 2026-04-14*
