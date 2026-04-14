# Architecture

## Pattern Overview

Two-container architecture with FastAPI backend and React frontend, using MongoDB for persistence and Redis for job queue management.

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

1. **User Action**: Frontend component triggers API call via `client.js`
2. **API Request**: FastAPI router receives request, validates with Pydantic models
3. **Business Logic**: Service layer processes request, calls external APIs (AI, WordPress)
4. **Persistence**: Data stored in MongoDB via Motor
5. **Async Jobs**: Long-running tasks queued to Redis, processed by worker
6. **Response**: Result returned to frontend, UI updates

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

1. Database schema (MongoDB collections)
2. Backend models and services
3. Backend routers and API
4. Frontend API client
5. Frontend components
6. Worker job processing
