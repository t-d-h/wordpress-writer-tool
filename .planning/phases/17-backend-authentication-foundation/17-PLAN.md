---
wave: 1
depends_on: []
files_modified:
  - backend/requirements.txt
  - backend/app/config.py
  - backend/app/models/user.py
  - backend/app/services/auth_service.py
  - backend/app/dependencies/auth.py
  - backend/app/routers/auth.py
  - backend/app/database.py
  - backend/app/main.py
  - backend/tests/test_auth.py
  - backend/tests/conftest.py
autonomous: true
requirements_addressed:
  - AUTH-01
  - AUTH-02
  - AUTH-03
  - AUTH-04
  - AUTH-06
  - SEC-05
  - SEC-06
---

# Plan 01: Backend Authentication Foundation

## Objective

Establish backend authentication infrastructure with user service, JWT tokens, and secure password handling. Implement login endpoint, JWT token generation/validation, Argon2 password hashing, authentication middleware, and Redis caching for performance.

## Success Criteria

- User can login with valid username and password and receive JWT token
- System validates JWT token on protected API requests and rejects invalid/expired tokens
- System hashes passwords using Argon2 before storage in MongoDB
- System uses SECRET_KEY environment variable for JWT signing
- System sets ACCESS_TOKEN_EXPIRE_MINUTES for token lifetime

## Tasks

### Task 01-01: Install Authentication Dependencies

<read_first>
- backend/requirements.txt
</read_first>

<action>
Add authentication dependencies to backend/requirements.txt:

```
pyjwt>=2.8.0
passlib[argon2]>=1.7.4
argon2-cffi>=23.1.0
```

Install the dependencies:
```bash
pip install "pyjwt>=2.8.0" "passlib[argon2]>=1.7.4" "argon2-cffi>=23.1.0"
```
</action>

<acceptance_criteria>
- backend/requirements.txt contains pyjwt>=2.8.0
- backend/requirements.txt contains passlib[argon2]>=1.7.4
- backend/requirements.txt contains argon2-cffi>=23.1.0
- pip show pyjwt exits 0
- pip show passlib exits 0
- pip show argon2-cffi exits 0
</acceptance_criteria>

---

### Task 01-02: Update Configuration with Auth Settings

<read_first>
- backend/app/config.py
- .planning/phases/17-backend-authentication-foundation/17-CONTEXT.md
</read_first>

<action>
Add SECRET_KEY and ACCESS_TOKEN_EXPIRE_MINUTES to backend/app/config.py:

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
```
</action>

<acceptance_criteria>
- backend/app/config.py contains SECRET_KEY: str
- backend/app/config.py contains ACCESS_TOKEN_EXPIRE_MINUTES: int
- backend/app/config.py contains os.getenv("SECRET_KEY"
- backend/app/config.py contains os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"
</acceptance_criteria>

---

### Task 01-03: Create User Pydantic Models

<read_first>
- backend/app/models/ai_provider.py
- .planning/phases/17-backend-authentication-foundation/17-CONTEXT.md
</read_first>

<action>
Create backend/app/models/user.py with UserCreate, UserUpdate, and UserResponse models:

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8)
    role: str = Field(default="user")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only alphanumeric characters and underscores')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['admin', 'editor', 'user']:
            raise ValueError('Role must be one of: admin, editor, user')
        return v

class UserUpdate(BaseModel):
    role: Optional[str] = None

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v is not None and v not in ['admin', 'editor', 'user']:
            raise ValueError('Role must be one of: admin, editor, user')
        return v

class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    created_at: str
    last_login_at: Optional[str] = None

    class Config:
        from_attributes = True
```
</action>

<acceptance_criteria>
- backend/app/models/user.py exists
- backend/app/models/user.py contains class UserCreate
- backend/app/models/user.py contains class UserUpdate
- backend/app/models/user.py contains class UserResponse
- backend/app/models/user.py contains validate_username validator
- backend/app/models/user.py contains validate_password validator
- backend/app/models/user.py contains validate_role validator
</acceptance_criteria>

---

### Task 01-04: Create Authentication Service

<read_first>
- backend/app/services/ai_service.py
- .planning/phases/17-backend-authentication-foundation/17-RESEARCH.md
- .planning/phases/17-backend-authentication-foundation/17-CONTEXT.md
</read_first>

<action>
Create backend/app/services/auth_service.py with authentication business logic:

```python
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.hash import argon2
from bson import ObjectId
from app.config import settings
from app.database import users_col
from app.redis_client import redis_client
import json

# Configure Argon2id with balanced parameters
password_hasher = argon2.using(
    type="id",
    time_cost=3,
    memory_cost=128000,
    parallelism=2,
    salt_size=16,
    hash_len=32
)

ALGORITHM = "HS256"
ISSUER = "wordpress-writer"
AUDIENCE = "wordpress-writer-api"

def hash_password(password: str) -> str:
    """Hash password using Argon2id."""
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash (constant-time)."""
    return password_hasher.verify(plain_password, hashed_password)

def create_access_token(user_id: str, username: str, role: str) -> str:
    """Create JWT access token with custom claims."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": username,
        "user_id": user_id,
        "username": username,
        "role": role,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "exp": expire,
        "iat": now,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str, username: str) -> str:
    """Create JWT refresh token with 30-day expiration."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=30)

    payload = {
        "sub": username,
        "user_id": user_id,
        "username": username,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "exp": expire,
        "iat": now,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired, please login again")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token, please login again")

async def get_user(username: str) -> Optional[dict]:
    """Get user from MongoDB or Redis cache."""
    cache_key = f"auth:user:{username}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    user = await users_col.find_one({"username": username})
    if user:
        user["id"] = str(user["_id"])
        await redis_client.set(cache_key, json.dumps(user), ex=900)
    return user

async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by ID from MongoDB or Redis cache."""
    cache_key = f"auth:user:{user_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if user:
        user["id"] = str(user["_id"])
        await redis_client.set(cache_key, json.dumps(user), ex=900)
    return user

async def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user with username and password."""
    user = await get_user(username)
    if not user:
        # Verify against dummy hash to prevent timing attacks
        DUMMY_HASH = password_hasher.hash("dummypassword")
        password_hasher.verify(password, DUMMY_HASH)
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return user
```
</action>

<acceptance_criteria>
- backend/app/services/auth_service.py exists
- backend/app/services/auth_service.py contains hash_password function
- backend/app/services/auth_service.py contains verify_password function
- backend/app/services/auth_service.py contains create_access_token function
- backend/app/services/auth_service.py contains create_refresh_token function
- backend/app/services/auth_service.py contains decode_token function
- backend/app/services/auth_service.py contains get_user function
- backend/app/services/auth_service.py contains get_user_by_id function
- backend/app/services/auth_service.py contains authenticate_user function
- backend/app/services/auth_service.py contains password_hasher = argon2.using(
- backend/app/services/auth_service.py contains time_cost=3
- backend/app/services/auth_service.py contains memory_cost=128000
- backend/app/services/auth_service.py contains parallelism=2
</acceptance_criteria>

---

### Task 01-05: Create Authentication Dependencies

<read_first>
- .planning/phases/17-backend-authentication-foundation/17-RESEARCH.md
- .planning/phases/17-backend-authentication-foundation/17-CONTEXT.md
</read_first>

<action>
Create backend/app/dependencies/auth.py with FastAPI authentication dependencies:

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
```
</action>

<acceptance_criteria>
- backend/app/dependencies/auth.py exists
- backend/app/dependencies/auth.py contains oauth2_scheme
- backend/app/dependencies/auth.py contains get_current_user function
- backend/app/dependencies/auth.py contains get_current_active_user function
- backend/app/dependencies/auth.py contains OAuth2PasswordBearer(tokenUrl="/api/auth/login")
</acceptance_criteria>

---

### Task 01-06: Create Authentication Router

<read_first>
- backend/app/routers/ai_providers.py
- .planning/phases/17-backend-authentication-foundation/17-RESEARCH.md
- .planning/phases/17-backend-authentication-foundation/17-CONTEXT.md
</read_first>

<action>
Create backend/app/routers/auth.py with login and refresh endpoints:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated
from datetime import datetime, timezone
from bson import ObjectId
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password
)
from app.database import users_col
from app.dependencies.auth import get_current_user
from app.models.user import UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> TokenResponse:
    """Authenticate user and return JWT tokens."""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token = create_access_token(
        user_id=str(user["_id"]),
        username=user["username"],
        role=user["role"]
    )

    # Generate refresh token
    refresh_token = create_refresh_token(
        user_id=str(user["_id"]),
        username=user["username"]
    )

    # Update last_login_at and store refresh token
    await users_col.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "last_login_at": datetime.now(timezone.utc).isoformat(),
                "refresh_token": refresh_token
            }
        }
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh")
async def refresh(refresh_token: str) -> TokenResponse:
    """Refresh access token using refresh token."""
    try:
        payload = decode_token(refresh_token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Verify refresh token exists in database
        user = await users_col.find_one({"_id": ObjectId(user_id)})
        if not user or user.get("refresh_token") != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Generate new access token
        access_token = create_access_token(
            user_id=user_id,
            username=user["username"],
            role=user["role"]
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.get("/me")
async def get_me(
    current_user: Annotated[dict, Depends(get_current_user)]
) -> UserResponse:
    """Get current user information."""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        role=current_user["role"],
        created_at=current_user["created_at"],
        last_login_at=current_user.get("last_login_at")
    )
```
</action>

<acceptance_criteria>
- backend/app/routers/auth.py exists
- backend/app/routers/auth.py contains @router.post("/login")
- backend/app/routers/auth.py contains @router.post("/refresh")
- backend/app/routers/auth.py contains @router.get("/me")
- backend/app/routers/auth.py contains class TokenResponse
- backend/app/routers/auth.py contains router = APIRouter(prefix="/api/auth"
</acceptance_criteria>

---

### Task 01-07: Update Database with Users Collection

<read_first>
- backend/app/database.py
- .planning/phases/17-backend-authentication-foundation/17-CONTEXT.md
</read_first>

<action>
Add users collection and indexes to backend/app/database.py:

```python
# Collections
ai_providers_col = db["ai_providers"]
wp_sites_col = db["wp_sites"]
projects_col = db["projects"]
posts_col = db["posts"]
jobs_col = db["jobs"]
default_models_col = db["default_models"]
wp_posts_cache_col = db["wp_posts_cache"]
link_maps_col = db["link_maps"]
users_col = db["users"]


async def create_indexes():
    """Create database indexes for optimized queries."""
    # Index on posts collection for token usage aggregation
    await posts_col.create_index([("project_id", 1)])
    await posts_col.create_index([("token_usage.research", 1)])
    await posts_col.create_index([("token_usage.outline", 1)])
    await posts_col.create_index([("token_usage.content", 1)])
    await posts_col.create_index([("token_usage.thumbnail", 1)])

    # New indexes for Phase 2: WordPress Integration
    await posts_col.create_index([("wp_post_id", 1)])
    await posts_col.create_index([("origin", 1)])
    await posts_col.create_index(
        [("project_id", 1), ("wp_post_id", 1)],
        unique=True,
        partialFilterExpression={"wp_post_id": {"$ne": None}},
    )

    # Index for Phase 4: WordPress post cache with TTL
    await wp_posts_cache_col.create_index([("cached_at", 1)], expireAfterSeconds=10800)

    # Index for link maps
    await link_maps_col.create_index([("project_id", 1)])

    # Index for Phase 17: Users collection
    await users_col.create_index([("username", 1)], unique=True)
```
</action>

<acceptance_criteria>
- backend/app/database.py contains users_col = db["users"]
- backend/app/database.py contains await users_col.create_index([("username", 1)], unique=True)
</acceptance_criteria>

---

### Task 01-08: Update Main App to Include Auth Router

<read_first>
- backend/app/main.py
- backend/app/routers/auth.py
</read_first>

<action>
Update backend/app/main.py to include auth router:

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
)

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
- backend/app/main.py contains from app.routers import auth
- backend/app/main.py contains app.include_router(auth.router)
</acceptance_criteria>

---

### Task 01-09: Create Authentication Tests

<read_first>
- backend/tests/conftest.py
- .planning/phases/17-backend-authentication-foundation/17-VALIDATION.md
</read_first>

<action>
Create backend/tests/test_auth.py with comprehensive authentication tests:

```python
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.database import users_col
from app.services.auth_service import hash_password, create_access_token, decode_token
from bson import ObjectId

client = TestClient(app)

@pytest.fixture
async def cleanup_users():
    """Cleanup users collection after tests."""
    yield
    await users_col.delete_many({})

@pytest.fixture
async def test_user(cleanup_users):
    """Create a test user."""
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

def test_password_hashing():
    """Test password hashing with Argon2."""
    password = "TestPass123"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 50

def test_jwt_token_creation():
    """Test JWT token creation with required claims."""
    token = create_access_token(
        user_id=str(ObjectId()),
        username="testuser",
        role="user"
    )
    assert isinstance(token, str)
    assert len(token) > 50

def test_jwt_token_decode():
    """Test JWT token decoding and validation."""
    user_id = str(ObjectId())
    token = create_access_token(
        user_id=user_id,
        username="testuser",
        role="user"
    )
    payload = decode_token(token)
    assert payload["user_id"] == user_id
    assert payload["username"] == "testuser"
    assert payload["role"] == "user"
    assert "exp" in payload
    assert "iat" in payload

def test_jwt_token_expiration():
    """Test JWT token expiration validation."""
    from app.services.auth_service import settings
    from app.config import Settings
    import jwt

    # Create token with short expiration
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=1)
    payload = {
        "sub": "testuser",
        "user_id": str(ObjectId()),
        "username": "testuser",
        "role": "user",
        "iss": "wordpress-writer",
        "aud": "wordpress-writer-api",
        "exp": expire,
        "iat": now,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    # Wait for token to expire
    import time
    time.sleep(2)

    # Should raise exception for expired token
    with pytest.raises(Exception, match="Token expired"):
        decode_token(token)

def test_login_success(test_user):
    """Test successful login."""
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "TestPass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "WrongPass123"}
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]

def test_login_missing_user():
    """Test login with non-existent user."""
    response = client.post(
        "/api/auth/login",
        data={"username": "nonexistent", "password": "TestPass123"}
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]

def test_protected_endpoint_with_valid_token(test_user):
    """Test protected endpoint with valid token."""
    # Login to get token
    login_response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "user"

def test_protected_endpoint_without_token():
    """Test protected endpoint without token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]

def test_protected_endpoint_with_invalid_token():
    """Test protected endpoint with invalid token."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]

def test_refresh_token_success(test_user):
    """Test refresh token endpoint."""
    # Login to get refresh token
    login_response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "TestPass123"}
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh access token
    response = client.post(
        "/api/auth/refresh",
        params={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_refresh_token_invalid():
    """Test refresh token with invalid token."""
    response = client.post(
        "/api/auth/refresh",
        params={"refresh_token": "invalid_token"}
    )
    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["detail"]
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
- backend/tests/test_auth.py exists
- backend/tests/test_auth.py contains test_password_hashing
- backend/tests/test_auth.py contains test_jwt_token_creation
- backend/tests/test_auth.py contains test_jwt_token_decode
- backend/tests/test_auth.py contains test_jwt_token_expiration
- backend/tests/test_auth.py contains test_login_success
- backend/tests/test_auth.py contains test_login_invalid_credentials
- backend/tests/test_auth.py contains test_login_missing_user
- backend/tests/test_auth.py contains test_protected_endpoint_with_valid_token
- backend/tests/test_auth.py contains test_protected_endpoint_without_token
- backend/tests/test_auth.py contains test_protected_endpoint_with_invalid_token
- backend/tests/test_auth.py contains test_refresh_token_success
- backend/tests/test_auth.py contains test_refresh_token_invalid
- backend/tests/conftest.py contains await users_col.delete_many({})
</acceptance_criteria>

---

## Verification

### Automated Tests

Run authentication tests:
```bash
pytest backend/tests/test_auth.py -v
```

Expected: All tests pass (13 tests)

### Manual Verification

1. **Login endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -d "username=testuser&password=TestPass123"
   ```
   Expected: Returns access_token and refresh_token

2. **Protected endpoint with valid token**:
   ```bash
   curl -X GET http://localhost:8000/api/auth/me \
     -H "Authorization: Bearer <access_token>"
   ```
   Expected: Returns user information

3. **Protected endpoint without token**:
   ```bash
   curl -X GET http://localhost:8000/api/auth/me
   ```
   Expected: Returns 401 with "Authentication required, please login"

### Integration Checks

- [ ] Login endpoint returns JWT tokens with correct claims
- [ ] Token validation rejects invalid tokens
- [ ] Token validation rejects expired tokens
- [ ] Passwords are hashed with Argon2id
- [ ] SECRET_KEY is used for JWT signing
- [ ] ACCESS_TOKEN_EXPIRE_MINUTES is used for token expiration
- [ ] Redis caching is working (check Redis for auth:user:* keys)
- [ ] Users collection has unique index on username

---

## Threat Model

### Security Considerations

| Threat | Mitigation | Status |
|--------|------------|--------|
| Timing attack (username enumeration) | Constant-time password verification with dummy hash | ✓ Implemented in authenticate_user |
| JWT token forgery (weak SECRET_KEY) | Use strong SECRET_KEY from environment variable | ✓ Implemented in config |
| Brute force password cracking | Argon2id with memory_cost=128MB, time_cost=3, parallelism=2 | ✓ Implemented in auth_service |
| Token replay attack | Short access token expiration (120 minutes) | ✓ Implemented in create_access_token |
| Token leakage in logs | Never log full tokens in tests | ✓ Implemented in tests |
| SQL injection | Not applicable — using MongoDB | N/A |
| Stored XSS | Not applicable — API returns JSON | N/A |
| CSRF attack | Not applicable — JWT in Authorization header | N/A |

### ASVS Compliance

| ASVS Category | Control | Status |
|---------------|---------|--------|
| V2 Authentication | JWT tokens with Argon2 password hashing | ✓ |
| V3 Session Management | JWT access tokens (120min) + refresh tokens (30 days) | ✓ |
| V4 Access Control | Role-based access control (admin, editor, user) | ✓ |
| V5 Input Validation | Pydantic models for username/password validation | ✓ |
| V6 Cryptography | PyJWT with HS256, passlib.argon2 for password hashing | ✓ |

---

## Notes

- JWT issuer claim value: "wordpress-writer" (the agent's discretion)
- JWT audience claim value: "wordpress-writer-api" (the agent's discretion)
- Login endpoint path: /api/auth/login (the agent's discretion)
- Refresh endpoint path: /api/auth/refresh (the agent's discretion)
- Admin account creation will be handled in Phase 18 (Backend User Management)
- All endpoints protected by default, public endpoints opt-in (implemented in Phase 20)
