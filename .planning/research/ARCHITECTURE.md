# Architecture Research

**Domain:** Initial Admin Account Creation for WordPress Writer Tool
**Researched:** 2026-04-20
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Startup Layer                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │              FastAPI Startup Event Handler          │    │
│  │  (main.py: @app.on_event("startup"))                 │    │
│  └────────────────────┬────────────────────────────────┘    │
│                       │                                        │
├───────────────────────┴──────────────────────────────────────┤
│                    Configuration Layer                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  .env File   │  │  Environment │  │  Settings    │      │
│  │  (INIT_USER) │  │  Variables   │  │  Class       │      │
│  │  (INIT_PASS) │  │  (os.getenv) │  │  (config.py) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│                    Service Layer                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │         User Service (user_service.py)               │    │
│  │  - create_admin_account()                            │    │
│  │  - Check if admin exists                             │    │
│  │  - Create admin with env credentials                 │    │
│  └────────────────────┬────────────────────────────────┘    │
│                       │                                        │
│  ┌────────────────────┴────────────────────────────────┐     │
│  │         Auth Service (auth_service.py)              │     │
│  │  - hash_password() (Argon2id)                       │     │
│  │  - verify_password()                                │     │
│  └─────────────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │              MongoDB (users collection)              │    │
│  │  - Unique index on username                          │    │
│  │  - Stores: username, password_hash, role, timestamps │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **FastAPI Startup Event** | Execute initialization logic before app accepts requests | `@app.on_event("startup")` in main.py |
| **Settings Class** | Load and validate environment variables | Pydantic Settings with `os.getenv()` |
| **User Service** | Manage user account creation and lifecycle | Async functions with MongoDB operations |
| **Auth Service** | Handle password hashing and verification | Argon2id with constant-time comparison |
| **MongoDB** | Persist user accounts with unique constraints | Motor async driver with unique indexes |

## Recommended Project Structure

```
backend/app/
├── config.py              # Environment variable configuration (MODIFY)
│   └── Add INIT_USER, INIT_PASSWORD fields
├── main.py                # FastAPI application entry point (MODIFY)
│   └── Update startup event to call create_admin_account()
├── services/
│   ├── user_service.py    # User account management (MODIFY)
│   │   └── Update create_admin_account() to use env variables
│   └── auth_service.py    # Authentication utilities (NO CHANGE)
│       └── Password hashing and verification already implemented
├── models/
│   └── user.py            # User Pydantic models (NO CHANGE)
│       └── UserCreate, UserUpdate, UserResponse already defined
├── database.py            # MongoDB connection and collections (NO CHANGE)
│   └── users_col already defined with unique index
└── routers/
    ├── auth.py            # Authentication endpoints (NO CHANGE)
    └── users.py           # User management endpoints (NO CHANGE)
```

### Structure Rationale

- **config.py:** Centralized configuration management ensures environment variables are loaded once and validated at startup
- **user_service.py:** Business logic for user operations keeps database operations isolated from API layer
- **auth_service.py:** Separation of authentication concerns allows reuse across different user operations
- **main.py:** Startup event is the appropriate place for one-time initialization tasks

## Architectural Patterns

### Pattern 1: Startup Event Initialization

**What:** Execute one-time initialization tasks when the application starts, before accepting requests

**When to use:** Database seeding, cache warming, resource allocation, default account creation

**Trade-offs:**
- ✅ Ensures initialization happens exactly once before any requests
- ✅ Clean separation from request handling logic
- ⚠️ Startup failures prevent application from starting
- ⚠️ Deprecated in favor of `lifespan` context manager (but still functional)

**Example:**
```python
# backend/app/main.py
from fastapi import FastAPI
from app.services.user_service import create_admin_account

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Create admin account on first startup."""
    await create_admin_account()
```

### Pattern 2: Environment-Driven Configuration

**What:** Use environment variables for configuration that varies across environments

**When to use:** Secrets, database URLs, feature flags, deployment-specific settings

**Trade-offs:**
- ✅ No sensitive data in code
- ✅ Easy to change between environments
- ✅ Standard practice for containerized deployments
- ⚠️ Requires documentation of required variables
- ⚠️ Missing variables cause runtime errors

**Example:**
```python
# backend/app/config.py
import os

class Settings:
    INIT_USER: str = os.getenv("INIT_USER", "admin")
    INIT_PASSWORD: str = os.getenv("INIT_PASSWORD", "admin123")

settings = Settings()
```

### Pattern 3: Idempotent Initialization

**What:** Initialization logic that can be run multiple times without side effects

**When to use:** Database seeding, cache warming, resource setup

**Trade-offs:**
- ✅ Safe to run on every startup
- ✅ Handles container restarts gracefully
- ✅ No need for "already initialized" tracking
- ⚠️ Slightly more complex logic (check before create)

**Example:**
```python
# backend/app/services/user_service.py
async def create_admin_account():
    """Create admin account on first startup if it doesn't exist."""
    existing_admin = await users_col.find_one({"username": settings.INIT_USER})
    if existing_admin:
        return  # Already exists, do nothing

    admin_data = {
        "username": settings.INIT_USER,
        "password_hash": hash_password(settings.INIT_PASSWORD),
        "role": "admin",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login_at": None,
    }
    await users_col.insert_one(admin_data)
```

## Data Flow

### Startup Flow

```
[Docker Compose starts containers]
    ↓
[Backend container starts]
    ↓
[FastAPI application initializes]
    ↓
[Startup event triggers]
    ↓
[create_admin_account() called]
    ↓
[Check if admin exists in MongoDB]
    ↓
[If exists → Return early]
    ↓
[If not exists → Read INIT_USER, INIT_PASSWORD from settings]
    ↓
[Hash password using Argon2id]
    ↓
[Insert admin document into users collection]
    ↓
[Application ready to accept requests]
```

### Authentication Flow (Existing)

```
[User submits credentials]
    ↓
[POST /auth/login endpoint]
    ↓
[authenticate_user() in auth_service.py]
    ↓
[get_user() from MongoDB or Redis cache]
    ↓
[verify_password() with Argon2id]
    ↓
[create_access_token() with JWT]
    ↓
[Return token to client]
```

### Key Data Flows

1. **Initial Admin Creation:** Environment variables → Settings → User Service → MongoDB
2. **User Authentication:** Request → Auth Service → MongoDB/Redis Cache → JWT Token
3. **Password Verification:** Plain password → Argon2id hash → Constant-time comparison

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k users | Current architecture is sufficient — single admin account, no scaling needed |
| 1k-100k users | Current architecture is sufficient — admin account is static, no scaling impact |
| 100k+ users | Current architecture is sufficient — admin account is not a scaling bottleneck |

### Scaling Priorities

1. **First bottleneck:** Not applicable — admin account creation is a one-time operation at startup
2. **Second bottleneck:** Not applicable — admin account is static after creation

**Note:** The initial admin account creation feature has minimal scaling impact because:
- It runs only once at application startup
- The admin account is a single static entity
- No dynamic scaling or load balancing considerations
- Authentication system (JWT tokens) already scales horizontally

## Anti-Patterns

### Anti-Pattern 1: Hardcoded Credentials

**What people do:** Hardcode admin username and password in the code

**Why it's wrong:**
- Credentials exposed in version control
- Cannot change between environments without code changes
- Security vulnerability if code is leaked

**Do this instead:**
```python
# ❌ BAD
async def create_admin_account():
    admin_data = {
        "username": "admin",  # Hardcoded
        "password_hash": hash_password("admin123"),  # Hardcoded
    }

# ✅ GOOD
async def create_admin_account():
    admin_data = {
        "username": settings.INIT_USER,  # From environment
        "password_hash": hash_password(settings.INIT_PASSWORD),  # From environment
    }
```

### Anti-Pattern 2: Non-Idempotent Initialization

**What people do:** Create admin account without checking if it already exists

**Why it's wrong:**
- Causes duplicate key errors on container restart
- Application fails to start if admin already exists
- Requires manual intervention to fix

**Do this instead:**
```python
# ❌ BAD
async def create_admin_account():
    admin_data = {"username": "admin", ...}
    await users_col.insert_one(admin_data)  # Fails if admin exists

# ✅ GOOD
async def create_admin_account():
    existing_admin = await users_col.find_one({"username": settings.INIT_USER})
    if existing_admin:
        return  # Already exists, safe to skip
    admin_data = {"username": settings.INIT_USER, ...}
    await users_col.insert_one(admin_data)
```

### Anti-Pattern 3: Plain Text Password Storage

**What people do:** Store passwords in plain text in the database

**Why it's wrong:**
- Security vulnerability if database is compromised
- Violates security best practices
- Existing codebase already uses Argon2id hashing

**Do this instead:**
```python
# ❌ BAD
admin_data = {
    "username": "admin",
    "password": "admin123",  # Plain text!
}

# ✅ GOOD
from app.services.auth_service import hash_password
admin_data = {
    "username": "admin",
    "password_hash": hash_password("admin123"),  # Hashed with Argon2id
}
```

### Anti-Pattern 4: Missing Environment Variable Validation

**What people do:** Use environment variables without validation or defaults

**Why it's wrong:**
- Application crashes with cryptic errors if variables are missing
- Difficult to debug in production
- Poor developer experience

**Do this instead:**
```python
# ❌ BAD
class Settings:
    INIT_USER: str = os.getenv("INIT_USER")  # None if not set
    INIT_PASSWORD: str = os.getenv("INIT_PASSWORD")  # None if not set

# ✅ GOOD
class Settings:
    INIT_USER: str = os.getenv("INIT_USER", "admin")  # Default value
    INIT_PASSWORD: str = os.getenv("INIT_PASSWORD", "admin123")  # Default value
```

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| MongoDB | Motor async driver | Users collection already exists with unique index on username |
| Redis | Async client | Used for user caching (15-minute TTL) — existing infrastructure |
| Environment Variables | os.getenv() | Loaded from .env file via docker-compose |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| main.py ↔ user_service.py | Direct function call | Startup event calls create_admin_account() |
| user_service.py ↔ auth_service.py | Direct function call | Uses hash_password() for password hashing |
| user_service.py ↔ database.py | Direct MongoDB operations | Uses users_col for CRUD operations |
| config.py ↔ All modules | Global settings object | Settings imported wherever needed |

### New vs Modified Components

| Component | Status | Changes Required |
|-----------|--------|------------------|
| **config.py** | MODIFY | Add INIT_USER and INIT_PASSWORD fields |
| **user_service.py** | MODIFY | Update create_admin_account() to use env variables |
| **main.py** | NO CHANGE | Already calls create_admin_account() in startup event |
| **auth_service.py** | NO CHANGE | Password hashing already implemented |
| **database.py** | NO CHANGE | Users collection already exists |
| **models/user.py** | NO CHANGE | User models already defined |
| **routers/auth.py** | NO CHANGE | Authentication endpoints already exist |
| **routers/users.py** | NO CHANGE | User management endpoints already exist |

## Build Order

### Phase 1: Configuration Layer
1. **Update config.py** to add INIT_USER and INIT_PASSWORD environment variables
   - Add fields to Settings class
   - Provide sensible defaults
   - Ensure .env file is updated with new variables

### Phase 2: Service Layer
2. **Update user_service.py** to use environment variables
   - Modify create_admin_account() to use settings.INIT_USER and settings.INIT_PASSWORD
   - Ensure idempotent behavior (check if admin exists before creating)
   - Add logging for debugging

### Phase 3: Testing
3. **Test the integration**
   - Verify admin account is created on first startup
   - Verify admin account is not recreated on subsequent startups
   - Verify admin can authenticate with the configured credentials
   - Test with missing environment variables (should use defaults)

### Phase 4: Documentation
4. **Update documentation**
   - Document required environment variables
   - Update deployment instructions
   - Add troubleshooting guide

## Sources

- **FastAPI Lifespan Events Documentation:** https://fastapi.tiangolo.com/advanced/events/ (HIGH confidence — official docs)
- **FastAPI Settings and Environment Variables:** https://fastapi.tiangolo.com/advanced/settings/ (HIGH confidence — official docs)
- **FastAPI Security Documentation:** https://fastapi.tiangolo.com/tutorial/security/ (HIGH confidence — official docs)
- **Existing Codebase Analysis:** backend/app/main.py, backend/app/config.py, backend/app/services/user_service.py, backend/app/services/auth_service.py (HIGH confidence — direct inspection)
- **Argon2 Password Hashing:** passlib library documentation (MEDIUM confidence — standard library)
- **MongoDB Unique Indexes:** Motor driver documentation (MEDIUM confidence — standard driver)

---
*Architecture research for: Initial Admin Account Creation for WordPress Writer Tool*
*Researched: 2026-04-20*
