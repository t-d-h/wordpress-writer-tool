# Structure

## Directory Layout

```
wordpress-writer-tool/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── config.py          # Configuration from environment variables
│   │   ├── database.py        # MongoDB connection and collections
│   │   ├── redis_client.py    # Redis client for job queue
│   │   ├── models/            # Pydantic models
│   │   │   ├── ai_provider.py
│   │   │   ├── wp_site.py
│   │   │   ├── project.py
│   │   │   ├── post.py
│   │   │   └── default_models.py
│   │   ├── routers/           # FastAPI routers
│   │   │   ├── ai_providers.py
│   │   │   ├── wp_sites.py
│   │   │   ├── projects.py
│   │   │   ├── posts.py
│   │   │   ├── jobs.py
│   │   │   └── default_models.py
│   │   ├── services/          # Business logic
│   │   │   ├── ai_service.py
│   │   │   ├── wp_service.py
│   │   │   ├── image_service.py
│   │   │   └── job_service.py
│   │   ├── workers/           # Background job processing
│   │   │   ├── redis_worker.py
│   │   │   └── tasks.py
│   │   └── utils/             # Utility functions
│   │       └── image_utils.py
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend container
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── main.jsx           # React entry point
│   │   ├── App.jsx            # Root component with routing
│   │   ├── api/
│   │   │   └── client.js      # Axios API client
│   │   └── components/        # React components
│   │       ├── Layout.jsx
│   │       ├── Dashboard.jsx
│   │       ├── AllPosts.jsx
│   │       ├── Posts/
│   │       │   └── PostView.jsx
│   │       ├── Projects/
│   │       │   ├── ProjectList.jsx
│   │       │   └── ProjectDetail.jsx
│   │       └── Settings/
│   │           ├── AIProviders.jsx
│   │           ├── WPSites.jsx
│   │           └── DefaultModels.jsx
│   ├── package.json           # Node.js dependencies
│   ├── vite.config.js        # Vite configuration
│   └── Dockerfile             # Frontend container
├── worker/                     # Worker container (same as backend)
├── docker-compose.yml         # Multi-container orchestration
├── .env                       # Environment variables
└── .planning/                 # GSD planning documents
```

## Key Locations

### Backend Entry Points
- `backend/app/main.py` - FastAPI application
- `backend/app/workers/redis_worker.py` - Redis worker

### Frontend Entry Points
- `frontend/src/main.jsx` - React application
- `frontend/src/App.jsx` - Root component with routing

### API Endpoints
- `backend/app/routers/` - All FastAPI routers
- `frontend/src/api/client.js` - Frontend API client

### Database
- `backend/app/database.py` - MongoDB collections
- Collections: `ai_providers`, `wp_sites`, `projects`, `posts`, `jobs`

### Job Processing
- `backend/app/workers/tasks.py` - Task handlers
- `backend/app/redis_client.py` - Redis pub/sub

## Naming Conventions

### Backend Python
- Files: `snake_case.py` (e.g., `ai_service.py`, `wp_sites.py`)
- Functions: `snake_case` (e.g., `get_ai_provider()`, `create_post()`)
- Classes: `PascalCase` (e.g., `AIProvider`, `PostCreate`)
- Private functions: `_snake_case` (e.g., `_call_openai()`)

### Frontend React
- Files: `PascalCase.jsx` (e.g., `Dashboard.jsx`, `ProjectDetail.jsx`)
- Components: `PascalCase` (e.g., `export default function Dashboard()`)
- Handlers: `camelCase` (e.g., `handleSubmit()`, `load()`)
- State: `camelCase` (e.g., `api_key`, `showModal`)

### Database Collections
- Names: `snake_case` with `_col` suffix (e.g., `ai_providers_col`, `posts_col`)

### API Routes
- Prefix: `/api/{resource}` (e.g., `/api/ai-providers`, `/api/posts`)
- Tags: `{Resource}` (e.g., `AI Providers`, `Posts`)

## File Organization Patterns

### Router Pattern
Each router follows identical structure:
1. Import dependencies
2. Create router with prefix and tags
3. Define CRUD endpoints
4. Use `format_*` helper for MongoDB → Pydantic conversion

### Component Pattern
Each component follows:
1. Import dependencies
2. Define state with `useState`
3. Define handlers
4. `useEffect` for data loading
5. Render JSX

### Service Pattern
Services are stateless async functions:
- No classes, only functions
- Helper functions prefixed with `_`
- Return tuples for multi-value returns
