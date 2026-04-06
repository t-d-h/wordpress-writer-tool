# WordPress AI Writer Tool - Implementation Plan

A full-stack web application for writing WordPress posts using AI. The app features a sidebar menu with General, Settings, and Projects tabs, and supports AI-powered research, content generation, image generation, and WordPress publishing.

## User Review Required

> [!NOTE]
> **AI Image Generation**: Using Gemini for image generation (thumbnails and section pictures).

> [!NOTE]
> **Job Queue**: Using Redis pub/sub for background job processing (no Celery). Each step (research, outline, content, thumbnail, section images, publish) will be a separate task that can run in parallel where possible.

> [!NOTE]
> **API Keys**: Stored as plain text in MongoDB for this MVP.

## Proposed Changes

### Project Structure

```
wordpress-writer-tool/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings/env config
│   │   ├── redis_client.py      # Redis connection + pub/sub
│   │   ├── database.py          # MongoDB connection
│   │   ├── models/
│   │   │   ├── ai_provider.py   # AI provider model
│   │   │   ├── wp_site.py       # WordPress site model
│   │   │   ├── project.py       # Project model
│   │   │   └── post.py          # Post model + job status
│   │   ├── routers/
│   │   │   ├── ai_providers.py  # CRUD for AI providers
│   │   │   ├── wp_sites.py      # CRUD for WP sites
│   │   │   ├── projects.py      # CRUD for projects
│   │   │   ├── posts.py         # CRUD + publish for posts
│   │   │   └── jobs.py          # Job status endpoints
│   │   ├── services/
│   │   │   ├── ai_service.py    # AI research + content gen
│   │   │   ├── image_service.py # AI image generation
│   │   │   ├── wp_service.py    # WordPress API integration
│   │   │   └── job_service.py   # Job queue management
│   │   └── workers/
│   │       ├── redis_worker.py  # Redis pub/sub worker
│   │       └── tasks.py         # Job task definitions
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   ├── api/
│   │   │   └── client.js        # Axios API client
│   │   ├── components/
│   │   │   ├── Layout.jsx       # Sidebar + main board
│   │   │   ├── Sidebar.jsx      # Navigation menu
│   │   │   ├── Dashboard.jsx    # General tab - job stats
│   │   │   ├── Settings/
│   │   │   │   ├── AIProviders.jsx
│   │   │   │   └── WPSites.jsx
│   │   │   ├── Projects/
│   │   │   │   ├── ProjectList.jsx
│   │   │   │   ├── CreateProjectModal.jsx
│   │   │   │   ├── ProjectDetail.jsx
│   │   │   │   ├── ProjectGeneral.jsx
│   │   │   │   └── ProjectContent.jsx
│   │   │   └── Posts/
│   │   │       ├── CreatePostModal.jsx
│   │   │       ├── SinglePost.jsx
│   │   │       ├── BulkPost.jsx
│   │   │       ├── PostPreview.jsx
│   │   │       └── PostTable.jsx
│   │   └── hooks/
│   │       └── useApi.js        # Custom API hooks
```

---

### Infrastructure

#### [NEW] [docker-compose.yml](file:///home/naoh/codes/wordpress-writer-tool/docker-compose.yml)
- Services: `backend` (FastAPI + Uvicorn), `worker` (Redis worker), `frontend` (React/Vite dev), `mongodb`, `redis`
- Network and volume configuration
- Environment variables

---

### Backend (FastAPI)

#### [NEW] [Dockerfile](file:///home/naoh/codes/wordpress-writer-tool/backend/Dockerfile)
- Python 3.11, install requirements, run with uvicorn

#### [NEW] [requirements.txt](file:///home/naoh/codes/wordpress-writer-tool/backend/requirements.txt)
- `fastapi`, `uvicorn`, `motor` (async MongoDB), `redis`, `google-genai`, `anthropic`, `openai`, `httpx`, `python-multipart`, `Pillow`

#### [NEW] [main.py](file:///home/naoh/codes/wordpress-writer-tool/backend/app/main.py)
- FastAPI app with CORS, include all routers

#### [NEW] [database.py](file:///home/naoh/codes/wordpress-writer-tool/backend/app/database.py)
- Motor async client connecting to MongoDB

#### [NEW] Models (`models/`)
- `ai_provider.py`: `{id, name, provider_type (openai|gemini|anthropic), api_key, created_at}`
- `wp_site.py`: `{id, name, url, api_key, created_at}`
- `project.py`: `{id, title, description, wp_site_id, created_at}`
- `post.py`: `{id, project_id, topic, additional_requests, title, meta_description, outline, sections[], content, thumbnail_url, section_images[], status (draft|waiting_approve|published|failed), research_data, research_done, content_done, thumbnail_done, sections_done, token_usage{}, jobs[], created_at}`

#### [NEW] Routers (`routers/`)
- Standard CRUD for AI providers, WP sites, projects
- Posts router: create single/bulk, list by project, get detail, update, delete, publish, unpublish
- Jobs router: list jobs, get job status, dashboard stats

#### [NEW] Services (`services/`)
- `ai_service.py`: Research topic (audience, keywords, key points), generate outline (SEO title, meta, intro hook/problem/promise, sections), generate section content, uses configured AI provider
- `image_service.py`: Generate thumbnails and section images via Gemini
- `wp_service.py`: Create/update WordPress posts via REST API, upload media
- `job_service.py`: Create and manage Redis-based job tasks

#### [NEW] Workers (`workers/`)
- `redis_worker.py`: Redis pub/sub worker that listens for job messages
- `tasks.py`: Task definitions for research, outline, content generation, image generation, publish — each as separate tasks that can run in parallel

---

### Frontend (React + Vite)

#### [NEW] [Dockerfile](file:///home/naoh/codes/wordpress-writer-tool/frontend/Dockerfile)
- Node 20, install deps, run vite dev server

#### [NEW] Core files
- `index.html`, `main.jsx`, `App.jsx` with React Router
- `index.css` with design system (dark theme, glassmorphism, Inter font)
- `App.css` with component-level styles

#### [NEW] Layout components
- `Layout.jsx`: Sidebar + main content area
- `Sidebar.jsx`: Collapsible navigation with General, Settings (AI Providers, WP Sites), Projects

#### [NEW] Dashboard
- `Dashboard.jsx`: Cards showing running/waiting/completed/failed job counts with animated counters

#### [NEW] Settings pages
- `AIProviders.jsx`: List, add, edit, delete AI provider configs
- `WPSites.jsx`: List, add, edit, delete WordPress site configs

#### [NEW] Projects pages
- `ProjectList.jsx`: Grid/list of projects with create button
- `CreateProjectModal.jsx`: Modal form with title, description, WP site selector
- `ProjectDetail.jsx`: Tabbed view (General, Content)
- `ProjectGeneral.jsx`: Stats cards (published, waiting, failed, draft)
- `ProjectContent.jsx`: Posts table with status indicators + action buttons

#### [NEW] Posts components
- `CreatePostModal.jsx`: Single/Bulk post creation with step-by-step pipeline visualization
- `PostPreview.jsx`: Full post preview before publishing with token usage
- `PostTable.jsx`: Table of posts with boolean indicators (research, content, thumbnail, section) and action buttons

---

## Verification Plan

### Automated Tests
1. **Docker Compose Build**: `docker compose build` — verify all images build successfully
2. **Docker Compose Up**: `docker compose up -d` — verify all services start and are healthy
3. **Backend Health Check**: `curl http://localhost:8000/health` — verify FastAPI is running
4. **Frontend Access**: Browser test to verify React app loads at `http://localhost:5173`

### Browser Verification
1. Navigate to the app, verify sidebar renders with all tabs
2. Add an AI provider, verify it appears in the list
3. Add a WordPress site, verify it appears in the list
4. Create a project, verify it appears in the project list
5. Open a project, verify General and Content tabs work
6. Create a single post, verify the pipeline steps are shown
7. Verify the dashboard shows job statistics

### Manual Verification
- User should test with their own API keys for AI providers and WordPress sites
- User should verify actual post publishing to a test WordPress site
