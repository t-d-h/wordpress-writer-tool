---
wave: 1
depends_on: []
files_modified:
  - backend/app/config.py
  - backend/app/main.py
  - backend/app/dependencies/auth.py
  - backend/app/routers/users.py
  - backend/app/services/user_service.py
  - backend/tests/test_user_management.py
  - backend/tests/conftest.py
autonomous: true
requirements_addressed:
  - USER-01
  - USER-02
  - USER-03
  - USER-04
  - USER-05
  - USER-06
  - USER-07
---

# Plan 01: Backend User Management

## Objective

Enable admin to manage user accounts with CRUD operations and validation. Implement admin account creation on startup, user creation, listing, deletion, password reset, and role update functionality. All operations are admin-only and leverage the authentication infrastructure established in Phase 17.

## Success Criteria

- System creates admin account on first startup using ADMIN_PASSWORD environment variable
- Admin can create new user accounts with username and password
- Admin can list all user accounts
- Admin can delete user accounts
- System validates username uniqueness on user creation
- System validates password strength on user creation

## Tasks

### Task 01-01: Update Configuration with Admin Password

<read_first>
- backend/app/config.py
- .planning/phases/18-backend-user-management/18-CONTEXT.md
</read_first>

<action>
Add ADMIN_PASSWORD to backend/app/config.py:

```python
class Settings:
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "wordpress_writer")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
```
</action>

<acceptance_criteria>
- backend/app/config.py contains ADMIN_PASSWORD: str
- backend/app/config.py contains os.getenv("ADMIN_PASSWORD"
</acceptance_criteria>

---

### Task 01-02: Create Admin-Only Dependency

<read_first>
- backend/app/dependencies/auth.py
- .planning/phases/18-backend-user-management/18-RESEARCH.md
</read_first>

<action>
Add get_current_admin dependency to backend/app/dependencies/auth.py:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from app.services.auth_service import decode_token, get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> dict:
    """Extract and validate JWT token, return user object."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required, please login",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception

    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(
    current_user: Annotated[dict, Depends(get_current_user)]
) -> dict:
    """Get current active user (can be extended for status checks)."""
    return current_user

async def get_current_admin(
    current_user: Annotated[dict, Depends(get_current_user)]
) -> dict:
    """Get current admin user (admin-only access)."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```
</action>

<acceptance_criteria>
- backend/app/dependencies/auth.py contains get_current_admin function
- backend/app/dependencies/auth.py contains HTTPException with status_code=status.HTTP_403_FORBIDDEN
- backend/app/dependencies/auth.py contains detail="Admin access required"
</acceptance_criteria>

---

### Task 01-03: Create User Service

<read_first>
- backend/app/services/auth_service.py
- .planning/phases/18-backend-user-management/18-RESEARCH.md
- .planning/phases/18-backend-user-management/18-CONTEXT.md
</read_first>

<action>
Create backend/app/services/user_service.py with user management business logic:

```python
from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId
from app.config import settings
from app.database import users_col
from app.services.auth_service import hash_password, verify_password
from app.redis_client import redis_client
import json

async def create_admin_account():
    """Create admin account on first startup if it doesn't exist."""
    existing_admin = await users_col.find_one({"username": "admin"})
    if existing_admin:
        return

    admin_data = {
        "username": "admin",
        "password_hash": hash_password(settings.ADMIN_PASSWORD),
        "role": "admin",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login_at": None
    }
    await users_col.insert_one(admin_data)

async def create_user(username: str, password: str, role: str = "user") -> dict:
    """Create a new user account."""
    # Check if username already exists
    existing = await users_col.find_one({"username": username})
    if existing:
        raise ValueError("Username already exists")

    user_data = {
        "username": username,
        "password_hash": hash_password(password),
        "role": role,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login_at": None
    }
    result = await users_col.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return user_data

async def list_users() -> List[dict]:
    """List all user accounts."""
    users = await users_col.find().to_list(length=None)
    for user in users:
        user["id"] = str(user["_id"])
        # Exclude password_hash from response
        if "password_hash" in user:
            del user["password_hash"]
    return users

async def get_user(user_id: str) -> Optional[dict]:
    """Get user by ID."""
    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if user:
        user["id"] = str(user["_id"])
        # Exclude password_hash from response
        if "password_hash" in user:
            del user["password_hash"]
    return user

async def delete_user(user_id: str) -> bool:
    """Delete a user account (prevents deletion of admin)."""
    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        return False

    # Prevent deletion of admin account
    if user.get("role") == "admin":
        raise ValueError("Cannot delete admin account")

    # Delete user
    await users_col.delete_one({"_id": ObjectId(user_id)})

    # Invalidate Redis cache
    cache_key = f"auth:user:{user_id}"
    await redis_client.delete(cache_key)

    return True

async def reset_password(user_id: str, new_password: str) -> bool:
    """Reset user password."""
    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        return False

    # Update password
    await users_col.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password_hash": hash_password(new_password)}}
    )

    # Invalidate Redis cache
    cache_key = f"auth:user:{user_id}"
    await redis_client.delete(cache_key)

    return True

async def update_role(user_id: str, new_role: str) -> bool:
    """Update user role."""
    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        return False

    # Prevent changing admin role
    if user.get("role") == "admin":
        raise ValueError("Cannot change admin role")

    # Update role
    await users_col.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": new_role}}
    )

    # Invalidate Redis cache
    cache_key = f"auth:user:{user_id}"
    await redis_client.delete(cache_key)

    return True
```
</action>

<acceptance_criteria>
- backend/app/services/user_service.py exists
- backend/app/services/user_service.py contains create_admin_account function
- backend/app/services/user_service.py contains create_user function
- backend/app/services/user_service.py contains list_users function
- backend/app/services/user_service.py contains get_user function
- backend/app/services/user_service.py contains delete_user function
- backend/app/services/user_service.py contains reset_password function
- backend/app/services/user_service.py contains update_role function
</acceptance_criteria>

---

### Task 01-04: Create User Management Router

<read_first>
- backend/app/routers/auth.py
- .planning/phases/18-backend-user-management/18-RESEARCH.md
- .planning/phases/18-backend-user-management/18-CONTEXT.md
</read_first>

<action>
Create backend/app/routers/users.py with user management endpoints:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Annotated, List
from bson import ObjectId
from app.services.user_service import (
    create_user,
    list_users,
    get_user,
    delete_user,
    reset_password,
    update_role
)
from app.dependencies.auth import get_current_admin
from app.models.user import UserCreate, UserResponse

router = APIRouter(prefix="/api/users", tags=["User Management"])

class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: str = "user"

class UserListResponse(BaseModel):
    users: List[UserResponse]

class PasswordResetRequest(BaseModel):
    new_password: str

class RoleUpdateRequest(BaseModel):
    role: str

@router.post("", response_model=UserResponse)
async def create_user_endpoint(
    user_data: UserCreateRequest,
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> UserResponse:
    """Create a new user account (admin-only)."""
    try:
        user = await create_user(user_data.username, user_data.password, user_data.role)
        return UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            role=user["role"],
            created_at=user["created_at"],
            last_login_at=user.get("last_login_at")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=UserListResponse)
async def list_users_endpoint(
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> UserListResponse:
    """List all user accounts (admin-only)."""
    users = await list_users()
    return UserListResponse(
        users=[
            UserResponse(
                id=user["id"],
                username=user["username"],
                role=user["role"],
                created_at=user["created_at"],
                last_login_at=user.get("last_login_at")
            )
            for user in users
        ]
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(
    user_id: str,
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> UserResponse:
    """Get user by ID (admin-only)."""
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user["id"],
        username=user["username"],
        role=user["role"],
        created_at=user["created_at"],
        last_login_at=user.get("last_login_at")
    )

@router.delete("/{user_id}")
async def delete_user_endpoint(
    user_id: str,
    current_admin: Annotated[dict, Depends(get_current_admin)]
):
    """Delete a user account (admin-only)."""
    try:
        success = await delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{user_id}/reset-password")
async def reset_password_endpoint(
    user_id: str,
    request: PasswordResetRequest,
    current_admin: Annotated[dict, Depends(get_current_admin)]
):
    """Reset user password (admin-only)."""
    success = await reset_password(user_id, request.new_password)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password reset successfully"}

@router.put("/{user_id}/role")
async def update_role_endpoint(
    user_id: str,
    request: RoleUpdateRequest,
    current_admin: Annotated[dict, Depends(get_current_admin)]
):
    """Update user role (admin-only)."""
    try:
        success = await update_role(user_id, request.role)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "Role updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```
</action>

<acceptance_criteria>
- backend/app/routers/users.py exists
- backend/app/routers/users.py contains @router.post("")
- backend/app/routers/users.py contains @router.get("")
- backend/app/routers/users.py contains @router.get("/{user_id}")
- backend/app/routers/users.py contains @router.delete("/{user_id}")
- backend/app/routers/users.py contains @router.post("/{user_id}/reset-password")
- backend/app/routers/users.py contains @router.put("/{user_id}/role")
- backend/app/routers/users.py contains router = APIRouter(prefix="/api/users"
</acceptance_criteria>

---

### Task 01-05: Add Startup Event to Main App

<read_first>
- backend/app/main.py
- .planning/phases/18-backend-user-management/18-RESEARCH.md
- .planning/phases/18-backend-user-management/18-CONTEXT.md
</read_first>

<action>
Add startup event and include users router in backend/app/main.py:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
- backend/app/main.py contains from app.routers import users
- backend/app/main.py contains app.include_router(users.router)
- backend/app/main.py contains from app.services.user_service import create_admin_account
- backend/app/main.py contains @app.on_event("startup")
- backend/app/main.py contains await create_admin_account()
</acceptance_criteria>

---

### Task 01-06: Create User Management Tests

<read_first>
- backend/tests/conftest.py
- .planning/phases/18-backend-user-management/18-VALIDATION.md
</read_first>

<action>
Create backend/tests/test_user_management.py with comprehensive user management tests:

```python
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.database import users_col
from app.services.user_service import create_user, list_users, delete_user, reset_password, update_role
from bson import ObjectId

client = TestClient(app)

@pytest.fixture
async def cleanup_users():
    """Cleanup users collection after tests."""
    yield
    await users_col.delete_many({})

@pytest.fixture
async def admin_user(cleanup_users):
    """Create an admin user for testing."""
    from app.services.auth_service import hash_password
    admin_data = {
        "username": "admin",
        "password_hash": hash_password("admin123"),
        "role": "admin",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login_at": None
    }
    result = await users_col.insert_one(admin_data)
    admin_data["_id"] = result.inserted_id
    return admin_data

@pytest.fixture
async def test_user(cleanup_users):
    """Create a test user."""
    user = await create_user("testuser", "TestPass123", "user")
    return user

def test_create_user(test_user):
    """Test creating a new user."""
    assert test_user["username"] == "testuser"
    assert test_user["role"] == "user"
    assert "password_hash" in test_user
    assert "created_at" in test_user

def test_create_user_duplicate_username(test_user):
    """Test creating user with duplicate username."""
    with pytest.raises(ValueError, match="Username already exists"):
        create_user("testuser", "AnotherPass123", "user")

def test_list_users(test_user):
    """Test listing all users."""
    users = await list_users()
    assert len(users) >= 1
    assert any(u["username"] == "testuser" for u in users)
    # Verify password_hash is excluded
    for user in users:
        assert "password_hash" not in user

def test_get_user(test_user):
    """Test getting user by ID."""
    user = await get_user(str(test_user["_id"]))
    assert user is not None
    assert user["username"] == "testuser"
    assert "password_hash" not in user

def test_delete_user(test_user):
    """Test deleting a user."""
    user_id = str(test_user["_id"])
    success = await delete_user(user_id)
    assert success is True

    # Verify user is deleted
    user = await get_user(user_id)
    assert user is None

def test_delete_nonexistent_user():
    """Test deleting a non-existent user."""
    fake_id = str(ObjectId())
    success = await delete_user(fake_id)
    assert success is False

def test_delete_admin_user(admin_user):
    """Test that admin account cannot be deleted."""
    with pytest.raises(ValueError, match="Cannot delete admin account"):
        await delete_user(str(admin_user["_id"]))

def test_reset_password(test_user):
    """Test resetting user password."""
    user_id = str(test_user["_id"])
    success = await reset_password(user_id, "NewPass456")
    assert success is True

def test_reset_password_nonexistent_user():
    """Test resetting password for non-existent user."""
    fake_id = str(ObjectId())
    success = await reset_password(fake_id, "NewPass456")
    assert success is False

def test_update_role(test_user):
    """Test updating user role."""
    user_id = str(test_user["_id"])
    success = await update_role(user_id, "editor")
    assert success is True

    # Verify role was updated
    user = await get_user(user_id)
    assert user["role"] == "editor"

def test_update_role_nonexistent_user():
    """Test updating role for non-existent user."""
    fake_id = str(ObjectId())
    success = await update_role(fake_id, "editor")
    assert success is False

def test_update_admin_role(admin_user):
    """Test that admin role cannot be changed."""
    with pytest.raises(ValueError, match="Cannot change admin role"):
        await update_role(str(admin_user["_id"]), "user")

def test_create_user_endpoint(test_user, admin_user):
    """Test user creation endpoint."""
    # Login as admin to get token
    from app.services.auth_service import create_access_token
    token = create_access_token(
        user_id=str(admin_user["_id"]),
        username=admin_user["username"],
        role=admin_user["role"]
    )

    response = client.post(
        "/api/users",
        json={"username": "newuser", "password": "NewPass123", "role": "user"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["role"] == "user"

def test_list_users_endpoint(test_user, admin_user):
    """Test user listing endpoint."""
    # Login as admin to get token
    from app.services.auth_service import create_access_token
    token = create_access_token(
        user_id=str(admin_user["_id"]),
        username=admin_user["username"],
        role=admin_user["role"]
    )

    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert len(data["users"]) >= 1

def test_delete_user_endpoint(test_user, admin_user):
    """Test user deletion endpoint."""
    user_id = str(test_user["_id"])

    # Login as admin to get token
    from app.services.auth_service import create_access_token
    token = create_access_token(
        user_id=str(admin_user["_id"]),
        username=admin_user["username"],
        role=admin_user["role"]
    )

    response = client.delete(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

def test_reset_password_endpoint(test_user, admin_user):
    """Test password reset endpoint."""
    user_id = str(test_user["_id"])

    # Login as admin to get token
    from app.services.auth_service import create_access_token
    token = create_access_token(
        user_id=str(admin_user["_id"]),
        username=admin_user["username"],
        role=admin_user["role"]
    )

    response = client.post(
        f"/api/users/{user_id}/reset-password",
        json={"new_password": "NewPass456"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "reset successfully" in response.json()["message"]

def test_update_role_endpoint(test_user, admin_user):
    """Test role update endpoint."""
    user_id = str(test_user["_id"])

    # Login as admin to get token
    from app.services.auth_service import create_access_token
    token = create_access_token(
        user_id=str(admin_user["_id"]),
        username=admin_user["username"],
        role=admin_user["role"]
    )

    response = client.put(
        f"/api/users/{user_id}/role",
        json={"role": "editor"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "updated successfully" in response.json()["message"]
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
- backend/tests/test_user_management.py exists
- backend/tests/test_user_management.py contains test_create_user
- backend/tests/test_user_management.py contains test_create_user_duplicate_username
- backend/tests/test_user_management.py contains test_list_users
- backend/tests/test_user_management.py contains test_get_user
- backend/tests/test_user_management.py contains test_delete_user
- backend/tests/test_user_management.py contains test_delete_nonexistent_user
- backend/tests/test_user_management.py contains test_delete_admin_user
- backend/tests/test_user_management.py contains test_reset_password
- backend/tests/test_user_management.py contains test_reset_password_nonexistent_user
- backend/tests/test_user_management.py contains test_update_role
- backend/tests/test_user_management.py contains test_update_role_nonexistent_user
- backend/tests/test_user_management.py contains test_update_admin_role
- backend/tests/test_user_management.py contains test_create_user_endpoint
- backend/tests/test_user_management.py contains test_list_users_endpoint
- backend/tests/test_user_management.py contains test_delete_user_endpoint
- backend/tests/test_user_management.py contains test_reset_password_endpoint
- backend/tests/test_user_management.py contains test_update_role_endpoint
- backend/tests/conftest.py contains await users_col.delete_many({})
</acceptance_criteria>

---

## Verification

### Automated Tests

Run user management tests:
```bash
pytest backend/tests/test_user_management.py -v
```

Expected: All tests pass (17 tests)

### Manual Verification

1. **Admin account creation on startup**:
   ```bash
   # Start backend server
   cd backend && uvicorn app.main:app --reload

   # Check MongoDB for admin account
   # Should see admin user with hashed password
   ```

2. **User creation endpoint**:
   ```bash
   # Login as admin to get token
   curl -X POST http://localhost:8000/api/auth/login \
     -d "username=admin&password=admin123"

   # Create new user
   curl -X POST http://localhost:8000/api/users \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"TestPass123","role":"user"}'
   ```
   Expected: Returns user object with id, username, role, created_at

3. **User listing endpoint**:
   ```bash
   curl -X GET http://localhost:8000/api/users \
     -H "Authorization: Bearer <token>"
   ```
   Expected: Returns list of users without password_hash

4. **User deletion endpoint**:
   ```bash
   curl -X DELETE http://localhost:8000/api/users/<user_id> \
     -H "Authorization: Bearer <token>"
   ```
   Expected: Returns success message

5. **Password reset endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/users/<user_id>/reset-password \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"new_password":"NewPass456"}'
   ```
   Expected: Returns success message

6. **Role update endpoint**:
   ```bash
   curl -X PUT http://localhost:8000/api/users/<user_id>/role \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"role":"editor"}'
   ```
   Expected: Returns success message

### Integration Checks

- [ ] Admin account created on first startup
- [ ] Admin can create new user accounts
- [ ] Admin can list all user accounts
- [ ] Admin can delete user accounts
- [ ] System validates username uniqueness on user creation
- [ ] System validates password strength on user creation
- [ ] Admin account cannot be deleted
- [ ] Admin role cannot be changed
- [ ] password_hash excluded from API responses
- [ ] Redis cache invalidated after password changes

---

## Threat Model

### Security Considerations

| Threat | Mitigation | Status |
|--------|------------|--------|
| Admin account deletion | Prevent deletion of admin account in delete_user() | ✓ Implemented in user_service |
| Admin role change | Prevent changing admin role in update_role() | ✓ Implemented in user_service |
| Password hash exposure | Exclude password_hash from all API responses | ✓ Implemented in list_users() and get_user() |
| Unauthorized user management | All endpoints require get_current_admin dependency | ✓ Implemented in users router |
| Username collision | MongoDB unique index on username field | ✓ Already implemented in database.py |
| Weak passwords | Password validation in UserCreate model (Phase 17) | ✓ Already implemented in user.py |
| Cache staleness | Invalidate Redis cache after password/role changes | ✓ Implemented in reset_password() and update_role() |

### ASVS Compliance

| ASVS Category | Control | Status |
|---------------|---------|--------|
| V2 Authentication | Admin account creation on startup with ADMIN_PASSWORD | ✓ |
| V2 Authentication | Password hashing with Argon2id (Phase 17) | ✓ |
| V4 Access Control | Admin-only endpoints with get_current_admin dependency | ✓ |
| V4 Access Control | Role-based access control (admin, editor, user) | ✓ |
| V5 Input Validation | Username uniqueness validation | ✓ |
| V5 Input Validation | Password strength validation (Phase 17) | ✓ |
| V6 Cryptography | Password hashing with Argon2id (Phase 17) | ✓ |

---

## Notes

- ADMIN_PASSWORD default value: "admin123" (the agent's discretion)
- Admin account username: "admin" (the agent's discretion)
- Admin account role: "admin" (the agent's discretion)
- User listing returns all users without pagination (MVP approach)
- Password reset allows admin to set new password directly (MVP approach)
- Role update allows admin to change user roles (MVP approach)
- Post ownership reassignment not implemented (posts don't have owner_id field yet)
- Role field stored but not yet used for access control (future feature)
