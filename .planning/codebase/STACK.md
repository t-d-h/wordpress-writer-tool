# Technology Stack

**Analysis Date:** 2026-04-07

## Languages

**Primary:**
- **Python 3.11** - Backend API, AI services, async workers
- **JavaScript (ES2020)** with JSX - React frontend application

**Secondary:**
- **HTML/CSS** - Frontend styling

## Runtime

**Environment:**
- Python 3.11-slim (Docker container) - Backend runtime
- Node.js with Vite 5.4 - Frontend dev/build server

**Package Manager:**
- Backend: `pip` via `requirements.txt`
- Frontend: `npm` via `package.json`
- Lockfile: Not detected (no `package-lock.json` or `requirements.lock`)

## Frameworks

**Core:**
- **FastAPI 0.115.0** - Backend REST API framework (`backend/app/main.py`)
- **React 18.3** - Frontend UI framework
- **Vite 5.4** - Frontend build tool and dev server
- **React Router 7.14** - Frontend client-side routing

**Data/Async:**
- **Motor 3.6 + PyMongo 4.7-4.9** - Async MongoDB driver
- **Redis 5.0** - Async Redis pub/sub job queue
- **Uvicorn 0.30** - ASGI server for FastAPI

**Testing:**
- Not detected

**Build/Dev:**
- **ESLint 9.13** - Frontend linting (`frontend/eslint.config.js`)
- **Docker Compose** - Multi-container orchestration (backend, worker, frontend)

## Key Dependencies

**Critical:**
- `openai` 1.50.0 - OpenAI API client (GPT-4o model used)
- `google-genai` 1.5.0 - Google Gemini API client (content + image generation)
- `anthropic` 0.39.0 - Anthropic API client (Claude Sonnet 4 model used)
- `httpx` >=0.28.1 - Async HTTP client for WordPress REST API calls
- `axios` 1.14.0 - Frontend HTTP client for API communication

**Infrastructure:**
- `pydantic` 2.9.0 - Request/response validation and serialization
- `python-multipart` 0.0.9 - File upload handling
- `Pillow` 10.4.0 - Image processing
- `react-icons` 5.6.0 - Icon library
- `@vitejs/plugin-react` 4.3.3 - React/JSX compilation

## Configuration

**Environment:**
- Backend config via environment variables (`backend/app/config.py`)
- Frontend config via `VITE_API_URL` env var (`frontend/src/api/client.js`)
- `.env` file present at project root (loaded by Docker Compose)

**Required environment variables:**
- `MONGODB_URL` - MongoDB connection URL
- `MONGODB_DB` - Database name (`wordpress_writer`)
- `REDIS_URL` - Redis connection URL
- `BACKEND_HOST` / `BACKEND_PORT` - Backend bind address (default `0.0.0.0:8000`)
- `FRONTEND_URL` - Frontend URL for CORS (default `http://localhost:5173`)
- `VITE_API_URL` - Frontend API base URL (default `http://localhost:8001`)

**Build:**
- `backend/Dockerfile` - Python 3.11-slim, installs requirements, runs uvicorn
- Frontend has a `Dockerfile` (path: `frontend/Dockerfile`)
- `docker-compose.yml` - Defines three services: `backend` (port 8001), `worker`, `frontend` (port 5174)

## Platform Requirements

**Development:**
- Docker and Docker Compose
- Python 3.11
- Node.js (for frontend dev)
- External MongoDB and Redis servers (configured via env vars, not containerized in current docker-compose)

**Production:**
- Targets Docker deployment via docker-compose
- MongoDB and Redis must be provisioned separately (MongoDB 7 and Redis 7 commented out in docker-compose)
- External WordPress site(s) with REST API and application passwords enabled
- AI provider API keys (OpenAI, Gemini, or Anthropic)

---

*Stack analysis: 2026-04-07*
