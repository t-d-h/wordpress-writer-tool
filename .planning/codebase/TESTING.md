# Testing Patterns

**Analysis Date:** 2026-04-07

## Test Status: NOT DETECTED

**No test files, test frameworks, or test infrastructure were found in this codebase.**

### Search Results:
- No `*.test.*` files (searched `**/*.test.*`)
- No `*.spec.*` files (searched `**/*.spec.*`)
- No `tests/` or `test/` directories
- No `conftest.py`
- No `pytest.ini` or `pyproject.toml` with test config
- No `jest.config.*`, `vitest.config.*`, or equivalent frontend test config
- No testing packages in `backend/requirements.txt`
- No testing packages in `frontend/package.json` devDependencies

**This codebase has zero test coverage for both the Python backend and React frontend.**

## Recommendations for Adding Tests

### Python Backend

**Recommended Framework:** `pytest` with `pytest-asyncio`

Installable packages to add to `backend/requirements.txt`:
```
pytest==8.x
pytest-asyncio==0.25.x
httpx          # for async test client
mongomock_motor  # or motor mock
fakeredis       # for async Redis mock
```

**Suggested test directory structure:**
```
backend/
  tests/
    conftest.py           # shared fixtures
    test_routers/         # API endpoint tests
    test_services/        # Unit tests for service layer
    test_models/          # Pydantic model validation tests
    test_workers/         # Worker task tests
```

**Key areas to test:**

1. **Pydantic models** (`backend/app/models/`):
   - Input validation (e.g., `AIProviderCreate` with invalid `provider_type`)
   - Required field enforcement
   - `Field(pattern=...)` validation for `provider_type`

2. **Routers** (`backend/app/routers/`):
   - CRUD endpoints with mocked MongoDB
   - HTTP status codes for not-found cases
   - Cascade delete behavior (e.g., deleting a project also deletes posts)

3. **Services** (`backend/app/services/`):
   - `ai_service._call_ai()` routing logic by provider type
   - `wp_service._get_auth_header()` Basic Auth encoding
   - `image_service.generate_image()` with mocked Gemini client
   - `wp_service.upload_media()` with mocked httpx

4. **Workers** (`backend/app/workers/`):
   - Task routing in `TASK_MAP`
   - Job status update logic (`_update_job_status()`)
   - Redis pub/sub worker processing

**Recommended pattern (once pytest is added):**
```python
# Example pattern for router tests
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_post_400_when_project_missing():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/posts", json={
            "project_id": "000000000000000000000000",
            "topic": "test"
        })
    assert response.status_code == 400
    assert response.json()["detail"] == "Project not found"
```

**Recommended pattern for service tests:**
```python
# Example pattern for mocking
@pytest.mark.asyncio
async def test_research_topic_calls_ai(monkeypatch):
    async def mock_call_ai(prompt, system_prompt=""):
        return (json.dumps({"target_audience": "test", "keywords": []}), 50)
    monkeypatch.setattr(ai_service, "_call_ai", mock_call_ai)

    result, tokens = await ai_service.research_topic("test topic")
    assert result["target_audience"] == "test"
    assert tokens == 50
```

### React Frontend

**Recommended Framework:** `vitest` + `@testing-library/react`

Packages to add to `frontend/package.json` devDependencies:
```json
"vitest": "^2.x",
"@testing-library/react": "^16.x",
"@testing-library/jest-dom": "^6.x",
"@vitest/ui": "^2.x",
"jsdom": "^26.x"
```

**Update `frontend/vite.config.js`:**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
  },
  // ...rest
})
```

**Suggested test structure:**
```
frontend/
  src/
    test/
      setup.js
    components/
      __tests__/
        Dashboard.test.jsx
        ProjectDetail.test.jsx
        AIProviders.test.jsx
    api/
      __tests__/
        client.test.js
```

**Recommended pattern (once vitest is added):**
```jsx
// Example pattern for component tests
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Dashboard from '../Dashboard'

// Mock API client
vi.mock('../api/client', () => ({
  getDashboardStats: vi.fn(() => Promise.resolve({
    data: { pending: 2, running: 1, completed: 10, failed: 1 }
  })),
}))

describe('Dashboard', () => {
  it('renders stat cards', async () => {
    render(<Dashboard />)
    const completed = await screen.findByText('10')
    expect(completed).toBeInTheDocument()
  })
})
```

**Recommended pattern for API client tests:**
```javascript
// Example pattern for API tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { createPost, createProvider } from '../api/client'

vi.mock('axios', () => ({
  default: {
    create: () => ({
      post: vi.fn(),
      get: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    }),
  },
}))

describe('API Client', () => {
  it('createPost sends correct payload', async () => {
    // ...mock and verify axios.post is called with /posts
  })
})
```

## Test Data / Fixtures

**No fixtures or factories currently exist.** Once testing is added:

**Backend fixture suggestions:**
- `conftest.py` with fixtures for:
  - `mock_ai_provider_doc` — sample AI provider document
  - `mock_wp_site_doc` — sample WordPress site document
  - `mock_project_doc` — sample project document
  - `mock_post_doc` — sample post document with all fields populated

**Frontend fixture suggestions:**
- `src/test/fixtures/` with:
  - `projectFixture.js` — sample project object matching API response
  - `postFixture.js` — sample post with pipeline states
  - `jobFixture.js` — sample job object

## Coverage Requirements

**Currently:** None enforced.

**Recommended targets (if testing is introduced):**
- Models: 100% (Pydantic validation is easy to fully cover)
- Services: 80%+ (core business logic)
- Routers: 70%+ (happy paths + 404 cases)
- Frontend components: 60%+ (render + key interactions)

**View coverage (once configured):**
```bash
# Backend
pytest --cov=app --cov-report=html

# Frontend
npm run test -- --coverage
```

## Test Types

**Currently:** None.

**Recommended:**
- **Unit tests** — test individual functions (services, models, utilities)
- **Integration tests** — test API endpoints with mocked databases (routers)
- **Component tests** — test React components render and respond to user actions
- **E2E tests** — Not recommended initially; focus on unit + component tests first
  - If added later: Playwright (`@playwright/test`)

## Key Observations

**This is early-stage code with no testing infrastructure.** The codebase is an MVP with the following characteristics that will affect testing strategy:

1. **Heavy external dependencies** — AI APIs (OpenAI, Gemini, Anthropic), WordPress REST API — all need mocking
2. **Redis pub/sub worker** — requires mocking Redis pubsub
3. **MongoDB dependency** — requires mongomock or TestContainers
4. **No dependency injection** — database connections and Redis client are module-level singletons, making unit testing harder without monkeypatching
5. **`print()` logging** — no structured logging system; test output will need stdout capture if verification needed

---

*Testing analysis: 2026-04-07*
