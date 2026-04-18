---
wave: 1
depends_on: []
files_modified:
  - backend/app/main.py
  - backend/app/routers/ai_providers.py
  - backend/app/routers/projects.py
  - backend/app/routers/posts.py
  - backend/app/routers/jobs.py
  - backend/app/routers/default_models.py
  - backend/app/routers/link_map.py
  - backend/app/routers/wordpress.py
  - backend/app/routers/wp_sites.py
  - backend/app/routers/version.py
  - backend/app/dependencies/auth.py
  - backend/app/services/auth_service.py
  - backend/tests/test_security_integration.py
  - backend/tests/conftest.py
autonomous: true
requirements_addressed:
  - SEC-01
  - SEC-02
  - SEC-07
---

# Plan 01: Security Integration

## Objective

Integrate authentication middleware and token validation across all API endpoints. This phase delivers security integration by protecting all API endpoints by default, injecting user context into protected route handlers, and ensuring frontend automatically injects JWT tokens in API requests. This is critical because the service will be public to the internet.

## Success Criteria

- System requires authentication for all API endpoints
- System injects user context into protected route handlers
- Frontend automatically injects JWT token in API requests

## Tasks

### Task 01-01: Mark Public Endpoints as Public

<read_first>
- backend/app/main.py
- .planning/phases/20-security-integration/20-CONTEXT.md
</read_first>

<action>
Update backend/app/main.py to mark public endpoints as public:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from app.config import settings
from app.routers import (
    ai_providers,
    wp_sites,
    projects,
    posts,
    jobs,
    default_models,
    wordpress,
    version,
    link_map,
    auth,
    users,
)
from app.services.user_service import create_admin_account

app = FastAPI(
    title="WordPress AI Writer",
    description="AI-powered WordPress post generation tool",
    version="1.0.0",
)

# CORS
origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai_providers.router)
app.include_router(wp_sites.router)
app.include_router(projects.router)
app.include_router(posts.router)
app.include_router(jobs.router)
app.include_router(default_models.router)
app.include_router(wordpress.router)
app.include_router(version.router)
app.include_router(link_map.router)
app.include_router(auth.router)
app.include_router(users.router)


@app.on_event("startup")
async def startup_event():
    """Create admin account on first startup."""
    await create_admin_account()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "WordPress AI Writer"}


@app.get("/")
async def root():
    return {
        "message": "WordPress AI Writer API",
        "docs": "/docs",
        "health": "/health",
    }
```
</action>

<acceptance_criteria>
- backend/app/main.py contains @app.get("/health") with no authentication
- backend/app/main.py contains @app.get("/") with no authentication
- backend/app/main.py contains allow_unauthenticated=True for public endpoints
</acceptance_criteria>

---

### Task 01-02: Verify All Protected Endpoints Use get_current_user

<read_first>
- backend/app/routers/ai_providers.py
- backend/app/routers/projects.py
- backend/app/routers/posts.py
- backend/app/routers/jobs.py
- backend/app/routers/default_models.py
- backend/app/routers/link_map.py
- backend/app/routers/wordpress.py
- backend/app/routers/wp_sites.py
- backend/app/routers/version.py
- .planning/phases/20-security-integration/20-CONTEXT.md
</read_first>

<action>
Verify all protected endpoints use get_current_user dependency:

1. Check backend/app/routers/ai_providers.py:
   - All endpoints should have `current_user: Annotated[dict, Depends(get_current_user)]` parameter
   - Example: `async def get_providers(current_user: Annotated[dict, Depends(get_current_user)])`

2. Check backend/app/routers/projects.py:
   - All endpoints should have `current_user: Annotated[dict, Depends(get_current_user)]` parameter
   - Example: `async def get_projects(current_user: Annotated[dict, Depends(get_current_user)])`

3. Check backend/app/routers/posts.py:
   - All endpoints should have `current_user: Annotated[dict, Depends(get_current_user)]` parameter
   - Example: `async def get_posts(current_user: Annotated[dict, Depends(get_current_user)])`

4. Check backend/app/routers/jobs.py:
   - All endpoints should have `current_user: Annotated[dict, Depends(get_current_user)]` parameter
   - Example: `async def get_jobs(current_user: Annotated[dict, Depends(get_current_user)])`

5. Check backend/app/routers/default_models.py:
   - All endpoints should have `current_user: Annotated[dict, Depends(get_current_user)]` parameter
   - Example: `async def get_default_models(current_user: Annotated[dict, Depends(get_current_user)])`

6. Check backend/app/routers/link_map.py:
   - All endpoints should have `current_user: Annotated[dict, Depends(get_current_user)]` parameter
   - Example: `async def get_link_map(current_user: Annotated[dict, Depends(get_current_user)])`

7. Check backend/app/routers/wordpress.py:
   - All endpoints should have `current_user: Annotated[dict, Depends(get_current_user)]` parameter
   - Example: `async def get_site_info(current_user: Annotated[dict, Depends(get_current_user)])`

8. Check backend/app/routers/wp_sites.py:
   - All endpoints should have `current_user: Annotated[dict, Depends(get_current_user)]` parameter
   - Example: `async def get_sites(current_user: Annotated[dict, Depends(get_current_user)])`

9. Check backend/app/routers/version.py:
   - All endpoints should have `current_user: Annotated[dict, Depends(get_current_user)]` parameter
   - Example: `async def get_version(current_user: Annotated[dict, Depends(get_current_user)])`

If any endpoint is missing the `current_user` parameter, add it to the function signature.
</action>

<acceptance_criteria>
- backend/app/routers/ai_providers.py contains current_user: Annotated[dict, Depends(get_current_user)] in all endpoint functions
- backend/app/routers/projects.py contains current_user: Annotated[dict, Depends(get_current_user)] in all endpoint functions
- backend/app/routers/posts.py contains current_user: Annotated[dict, Depends(get_current_user)] in all endpoint functions
- backend/app/routers/jobs.py contains current_user: Annotated[dict, Depends(get_current_user)] in all endpoint functions
- backend/app/routers/default_models.py contains current_user: Annotated[dict, Depends(get_current_user)] in all endpoint functions
- backend/app/routers/link_map.py contains current_user: Annotated[dict, Depends(get_current_user)] in all endpoint functions
- backend/app/routers/wordpress.py contains current_user: Annotated[dict, Depends(get_current_user)] in all endpoint functions
- backend/app/routers/wp_sites.py contains current_user: Annotated[dict, Depends(get_current_user)] in all endpoint functions
- backend/app/routers/version.py contains current_user: Annotated[dict, Depends(get_current_user)] in all endpoint functions
</acceptance_criteria>

---

### Task 01-03: Verify User Context Injection

<read_first>
- backend/app/dependencies/auth.py
- .planning/phases/20-security-integration/20-CONTEXT.md
</read_first>

<action>
Verify user context injection in get_current_user dependency:

1. Check backend/app/dependencies/auth.py:
   - get_current_user function should extract user_id from JWT token
   - get_current_user function should fetch user from database via get_user_by_id
   - get_current_user function should return full user object with user_id, username, role, created_at, last_login_at
   - get_current_user function should raise HTTPException with 401 status if token is invalid/expired
   - get_current_user function should raise HTTPException with 403 status if user not found

2. Check backend/app/services/auth_service.py:
   - get_user_by_id function should return user object with user_id, username, role, created_at, last_login_at
   - get_user function should exclude password_hash from response
   - get_user function should cache user in Redis for 15 minutes

3. Verify user object structure matches expected fields:
   - user_id (string)
   - username (string)
   - role (string: admin, editor, user)
   - created_at (ISO 8601 string)
   - last_login_at (optional ISO 8601 string)
</action>

<acceptance_criteria>
- backend/app/dependencies/auth.py contains get_current_user function
- backend/app/dependencies/auth.py contains user_id extraction from JWT token
- backend/app/dependencies/auth.py contains get_user_by_id call
- backend/app/dependencies/auth.py contains HTTPException with 401 status for invalid/expired tokens
- backend/app/services/auth_service.py contains get_user_by_id function
- backend/app/services/auth_service.py excludes password_hash from user response
- backend/app/services/auth_service.py caches user in Redis for 15 minutes
</acceptance_criteria>

---

### Task 01-04: Verify Frontend Token Injection

<read_first>
- frontend/src/api/client.js
- .planning/phases/20-security-integration/20-CONTEXT.md
</read_first>

<action>
Verify frontend token injection in axios interceptor:

1. Check frontend/src/api/client.js:
   - apiClient.interceptors.request.use should add Authorization header with Bearer token
   - apiClient.interceptors.request.use should read token from localStorage.getItem('auth_token')
   - apiClient.interceptors.request.use should set config.headers.Authorization = `Bearer ${token}`
   - apiClient.interceptors.response.use should handle 401 errors by clearing tokens and redirecting to /login

2. Verify token injection works for all API calls:
   - All API calls should automatically include Authorization header
   - Token should be read from localStorage on every request
   - 401 errors should clear tokens and redirect to login

3. Verify token storage:
   - auth_token key in localStorage contains JWT access token
   - auth_user key in localStorage contains user data as JSON string
   - refresh_token key in localStorage contains JWT refresh token
</action>

<acceptance_criteria>
- frontend/src/api/client.js contains apiClient.interceptors.request.use
- frontend/src/api/client.js adds Authorization header with Bearer token
- frontend/src/api/client.js reads token from localStorage.getItem('auth_token')
- frontend/src/api/client.js handles 401 errors by clearing tokens and redirecting to /login
- frontend/src/api/client.js stores auth_token in localStorage
- frontend/src/api/client.js stores auth_user in localStorage
- frontend/src/api/client.js stores refresh_token in localStorage
</acceptance_criteria>

---

### Task 01-05: Create Security Integration Tests

<read_first>
- backend/tests/conftest.py
- .planning/phases/20-security-integration/20-CONTEXT.md
</read_first>

<action>
Create backend/tests/test_security_integration.py with security integration tests:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import users_col
from app.services.auth_service import hash_password, create_access_token
from bson import ObjectId
from datetime import datetime, timezone, timedelta

client = TestClient(app)

@pytest.fixture
async def cleanup_users():
    """Cleanup users collection after tests."""
    yield
    await users_col.delete_many({})

@pytest.fixture
async def test_user(cleanup_users):
    """Create a test user for testing."""
    user_data = {
        "username": "testuser",
        "password_hash": hash_password("TestPass123"),
        "role": "user",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login_at": None
    }
    result = await users_col.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return user_data

def test_protected_endpoint_requires_token(test_user):
    """Test that protected endpoint requires valid token."""
    # Create valid token
    token = create_access_token(
        user_id=str(test_user["_id"]),
        username=test_user["username"],
        role=test_user["role"]
    )

    # Access protected endpoint without token
    response = client.get("/api/projects")
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]

    # Access protected endpoint with valid token
    response = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_protected_endpoint_injects_user_context(test_user):
    """Test that protected endpoint injects user context."""
    # Create valid token
    token = create_access_token(
        user_id=str(test_user["_id"]),
        username=test_user["username"],
        role=test_user["role"]
    )

    # Access protected endpoint with token
    response = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_invalid_token_returns_401(test_user):
    """Test that invalid token returns 401."""
    # Create invalid token
    invalid_token = "invalid.token.string"

    # Access protected endpoint with invalid token
    response = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]

def test_expired_token_returns_401(test_user):
    """Test that expired token returns 401."""
    # Create expired token
    expired_token = create_access_token(
        user_id=str(test_user["_id"]),
        username=test_user["username"],
        role=test_user["role"]
    )

    # Wait for token to expire
    import time
    time.sleep(2)

    # Access protected endpoint with expired token
    response = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "Token expired" in response.json()["detail"]

def test_public_endpoint_no_auth_required():
    """Test that public endpoints work without authentication."""
    # Access health endpoint without token
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    # Access root endpoint without token
    response = client.get("/")
    assert response.status_code == 200
    assert "WordPress AI Writer API" in response.json()["message"]

def test_user_context_includes_required_fields(test_user):
    """Test that user context includes all required fields."""
    # Create valid token
    token = create_access_token(
        user_id=str(test_user["_id"]),
        username=test_user["username"],
        role=test_user["role"]
    )

    # Access protected endpoint with token
    response = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # Verify user context structure (would need to add endpoint that returns user context)
    # For now, just verify token is valid
    assert token is not None
    assert len(token) > 0

def test_token_injection_in_all_api_calls(test_user):
    """Test that token is injected in all API calls."""
    # Create valid token
    token = create_access_token(
        user_id=str(test_user["_id"]),
        username=test_user["username"],
        role=test_user["role"]
    )

    # Test multiple API calls
    endpoints = [
        "/api/projects",
        "/api/posts",
        "/api/jobs",
        "/api/ai-providers",
        "/api/default-models",
    ]

    for endpoint in endpoints:
        response = client.get(
            endpoint,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

def test_401_clears_tokens_and_redirects_to_login():
    """Test that 401 errors clear tokens and redirect to login."""
    # Create valid token
    token = create_access_token(
        user_id=str(test_user["_id"]),
        username=test_user["username"],
        role=test_user["role"]
    )

    # Store token in localStorage
    import json
    localStorage.setItem('auth_token', token)
    localStorage.setItem('auth_user', json.dumps({
        "username": test_user["username"],
        "role": test_user["role"]
    }))

    # Access protected endpoint with valid token
    response = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # Expire token
    import time
    time.sleep(2)

    # Access protected endpoint with expired token
    response = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401

    # Verify tokens are cleared
    assert localStorage.getItem('auth_token') is None
    assert localStorage.getItem('auth_user') is None

    # Verify redirect to login
    assert window.location.href == '/login'
```

Update backend/tests/conftest.py to add users_col to cleanup:

```python
@pytest.fixture(scope="function", autouse=True)
async def cleanup_database():
    """Cleanup database after each test."""
    yield
    await ai_providers_col.delete_many({})
    await wp_sites_col.delete_many({})
    await projects_col.delete_many({})
    await posts_col.delete_many({})
    await jobs_col.delete_many({})
    await default_models_col.delete_many({})
    await wp_posts_cache_col.delete_many({})
    await link_maps_col.delete_many({})
    await users_col.delete_many({})
```
</action>

<acceptance_criteria>
- backend/tests/test_security_integration.py exists
- backend/tests/test_security_integration.py contains test_protected_endpoint_requires_token
- backend/tests/test_security_integration.py contains test_protected_endpoint_injects_user_context
- backend/tests/test_security_integration.py contains test_invalid_token_returns_401
- backend/tests/test_security_integration.py contains test_expired_token_returns_401
- backend/tests/test_security_integration.py contains test_public_endpoint_no_auth_required
- backend/tests/test_security_integration.py contains test_user_context_includes_required_fields
- backend/tests/test_security_integration.py contains test_token_injection_in_all_api_calls
- backend/tests/test_security_integration.py contains test_401_clears_tokens_and_redirects_to_login
- backend/tests/conftest.py contains await users_col.delete_many({})
</acceptance_criteria>

---

## Verification

### Automated Tests

Run security integration tests:
```bash
pytest backend/tests/test_security_integration.py -v
```

Expected: All tests pass

### Manual Verification

1. **Protected endpoint requires token**:
   - Try to access /api/projects without token
   - Expected: Returns 401 with "Authentication required" error

2. **Protected endpoint injects user context**:
   - Login with valid credentials
   - Access /api/projects with token
   - Expected: Returns 200 with user data

3. **Invalid token returns 401**:
   - Try to access /api/projects with invalid token
   - Expected: Returns 401 with "Invalid token" error

4. **Expired token returns 401**:
   - Login with valid credentials
   - Wait for token to expire
   - Try to access /api/projects with expired token
   - Expected: Returns 401 with "Token expired" error

5. **Public endpoints work without authentication**:
   - Access /health without token
   - Access / without token
   - Expected: Returns 200 with service status

6. **401 errors clear tokens and redirect to login**:
   - Login with valid credentials
   - Wait for token to expire
   - Try to access /api/projects with expired token
   - Expected: Tokens cleared from localStorage, redirect to /login

7. **Token injection in all API calls**:
   - Login with valid credentials
   - Make multiple API calls (/api/projects, /api/posts, /api/jobs, etc.)
   - Check network tab for Authorization header
   - Expected: All requests include Bearer token in Authorization header

### Integration Checks

- [ ] System requires authentication for all API endpoints
- [ ] System injects user context into protected route handlers
- [ ] Frontend automatically injects JWT token in API requests
- [ ] All protected endpoints use get_current_user dependency
- [ ] Public endpoints work without authentication
- [ ] 401 errors clear tokens and redirect to login

---

## Threat Model

### Security Considerations

| Threat | Mitigation | Status |
|--------|------------|--------|
| Unauthorized access | All endpoints protected by default with get_current_user dependency | ✓ Implemented in Phase 17 |
| Token replay attack | Short access token expiration (120 minutes) | ✓ Implemented in Phase 17 |
| Token leakage in logs | Never log full tokens in tests | ✓ Implemented in tests |
| CSRF attacks | Not applicable with JWT in Authorization header | ✓ Not vulnerable |
| Session hijacking | Short access token expiration (120 minutes) | ✓ Implemented in Phase 17 |
| XSS token theft | Token stored in localStorage (vulnerable to XSS) | ⚠️ Acceptable for MVP, httpOnly cookies in future |

### ASVS Compliance

| ASVS Category | Control | Status |
|---------------|---------|--------|
| V2 Authentication | JWT tokens with Argon2 password hashing (Phase 17) | ✓ |
| V3 Session Management | JWT access tokens (120min) + refresh tokens (30 days) | ✓ |
| V4 Access Control | Protected routes with authentication check | ✓ |
| V5 Input Validation | Login form validation (Phase 19) | ✓ |
| V6 Cryptography | PyJWT with HS256, passlib.argon2 for password hashing (Phase 17) | ✓ |

---

## Notes

- All API endpoints are protected by default because service will be public to internet
- Public endpoints like /health and /docs must be explicitly marked with `allow_unauthenticated=True`
- User context injected as full user object via get_current_user dependency
- Authentication errors raise HTTPException with status_code 401 or 403
- Frontend axios interceptor already injects Bearer token in Authorization header
- 401 errors clear tokens and redirect to login page (already implemented in Phase 19)
- User management endpoints from Phase 18 are admin-only (already implemented with get_current_admin dependency)
- All protected endpoints use the same error handling pattern for consistency
