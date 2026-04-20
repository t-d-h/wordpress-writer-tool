# Technology Stack

**Project:** WordPress Writer Tool - User Management & Authentication
**Researched:** 2026-04-20 (Updated for Initial Admin Account Creation)
**Mode:** Ecosystem (authentication stack for FastAPI/React)

## Recommended Stack

### Core Authentication Framework
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| FastAPI Security | Built-in (0.115.0) | OAuth2 password flow, Bearer tokens, startup events | Official FastAPI utilities, integrates with OpenAPI docs, `@app.on_event("startup")` for initialization |
| PyJWT | >=2.8.0 | JWT token encoding/decoding | Industry standard, lightweight, supports HS256 algorithm, official FastAPI recommendation |
| passlib[argon2] | >=1.7.4 | Password hashing with Argon2id | Modern, secure, winner of Password Hashing Competition, provides constant-time verification |
| argon2-cffi | >=23.1.0 | Argon2 CFFI bindings | Required by passlib for Argon2 support, latest version (25.1.0) supports Python 3.8-3.14 |

### Database Integration
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| MongoDB | Existing (motor 3.6.0) | User account storage | Already in stack, async driver, fits existing patterns, no new infrastructure needed |
| MongoDB Indexes | Existing | Username uniqueness, email lookup | Leverage existing database.py patterns for index creation |

### Frontend Authentication
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| localStorage | Browser API | JWT token storage | Already used in codebase (theme, language preferences), persists across sessions, simple API |
| Axios | Existing (1.14.0) | API client with token injection | Already installed, supports interceptors for automatic token handling |
| React Router | Existing (7.14.0) | Protected routes, login redirect | Already installed, can wrap routes with auth checks |

### Security Configuration
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| SECRET_KEY | Environment variable | JWT signing key | Required for JWT security, generate with `openssl rand -hex 32` |
| INIT_USER | Environment variable | Initial admin username | Allows configurable admin account creation on first startup |
| INIT_PASSWORD | Environment variable | Initial admin password | Allows configurable admin account creation on first startup |
| ADMIN_PASSWORD | Environment variable | Fallback admin password | Used if INIT_USER/INIT_PASSWORD not provided (legacy support) |
| ACCESS_TOKEN_EXPIRE_MINUTES | Environment variable | Token lifetime | Configurable session duration, default 30 minutes |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Password Hashing | passlib (Argon2) | bcrypt | bcrypt is also secure but Argon2id is more resistant to GPU/ASIC attacks; passlib is mature and well-maintained |
| JWT Library | PyJWT | python-jose | PyJWT is simpler, official FastAPI recommendation, fewer dependencies |
| Token Storage | localStorage | sessionStorage | localStorage persists across browser sessions (better UX), sessionStorage clears on tab close |
| Auth Flow | OAuth2 Password Flow | Session-based cookies | JWT is stateless, scales better, works with existing API architecture |
| Frontend Auth | Custom hooks | Auth0/Firebase | Overkill for MVP, adds external dependencies, not needed for simple username/password |
| Admin Account Creation | Environment variables (INIT_USER, INIT_PASSWORD) | Interactive CLI prompt | Environment variables work better with Docker Compose and automated deployments; CLI prompt requires manual intervention |

## Installation

```bash
# Backend - Add to requirements.txt
pyjwt>=2.8.0
"passlib[argon2]>=1.7.4"
argon2-cffi>=23.1.0

# Backend - Install
pip install pyjwt "passlib[argon2]" argon2-cffi

# Frontend - No new dependencies needed
# Already have: axios, react-router-dom, localStorage (browser API)
```

## Integration Points

### Backend Integration
- **Existing Service**: `backend/app/services/auth_service.py` - Authentication logic, password hashing, JWT token generation
- **Existing Service**: `backend/app/services/user_service.py` - User management, `create_admin_account()` function for initial admin creation
- **Existing Router**: `backend/app/routers/auth.py` - Login endpoint, user management endpoints
- **Existing Router**: `backend/app/routers/users.py` - User CRUD operations
- **Existing Models**: `backend/app/models/user.py` - User Pydantic models (UserCreate, UserResponse, UserUpdate)
- **Existing Collection**: `users` collection in MongoDB - Store user accounts with hashed passwords
- **Existing Config**: Add `INIT_USER`, `INIT_PASSWORD` to `backend/app/config.py` (in addition to existing `SECRET_KEY`, `ADMIN_PASSWORD`, `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Existing Database**: Add user collection indexes in `backend/app/database.py` (username unique index already exists)
- **Existing Startup Event**: `backend/app/main.py` - `@app.on_event("startup")` already calls `create_admin_account()`

### Initial Admin Account Creation Flow
1. **FastAPI Startup**: Application starts, `@app.on_event("startup")` triggers
2. **Environment Variables**: Read `INIT_USER` and `INIT_PASSWORD` from environment
3. **Validation**: Validate credentials meet UserCreate requirements (username 3-20 chars, password 8+ chars with complexity)
4. **Check Existing**: Query MongoDB for existing admin account by username
5. **Create if Missing**: If no admin exists, create new admin account with hashed password
6. **Skip if Exists**: If admin already exists, skip creation (no modifications)
7. **Log Result**: Log success or skip message to console

### Frontend Integration
- **Existing Component**: `frontend/src/components/Login.jsx` - Login form
- **Existing Hook**: `frontend/src/hooks/useAuth.js` - Authentication state, token management
- **Existing API**: `login()`, `getCurrentUser()` in `frontend/src/api/client.js`
- **Existing Router**: Protected route wrapper in `frontend/src/App.jsx`
- **Existing Storage**: `localStorage` for token storage (pattern already established)

### Security Best Practices
- **Password Hashing**: Use Argon2id with recommended parameters (time_cost=3, memory_cost=128000, parallelism=2, salt_size=16, hash_len=32)
- **JWT Tokens**: Use HS256 algorithm, set expiration, include `sub` claim for username, `user_id` for database reference
- **Token Storage**: Store in localStorage, send in `Authorization: Bearer <token>` header
- **Timing Attacks**: Always verify password against dummy hash when user not found (prevents username enumeration)
- **Secret Key**: Generate with `openssl rand -hex 32`, store in environment variable, never commit to git
- **Token Expiration**: Default 30 minutes, configurable via environment variable
- **Error Messages**: Generic "Incorrect username or password" to prevent user enumeration
- **Initial Admin Account**: Create only on first startup, never overwrite existing admin account
- **Environment Variables**: Use `INIT_USER` and `INIT_PASSWORD` for configurable admin credentials, fallback to `ADMIN_PASSWORD` for legacy support
- **Admin Account Protection**: Prevent deletion and role modification of admin account (already implemented in user_service.py)

## What NOT to Add

### Avoid These Libraries
- **python-jose** - More complex than needed, PyJWT is sufficient
- **Auth0/Firebase** - Overkill for MVP, adds external dependencies
- **Session management libraries** - JWT is stateless, no server-side sessions needed
- **OAuth provider SDKs** - Not needed for simple username/password authentication
- **Frontend auth libraries** (react-auth-kit, etc.) - Custom hooks are sufficient
- **Additional password hashing libraries** - passlib with Argon2 is already implemented and secure

### Avoid These Patterns
- **Session-based authentication** - JWT is better for API architecture
- **Cookie-based token storage** - localStorage is simpler for SPA
- **Complex role-based access** - MVP only needs admin/user distinction
- **Multi-factor authentication** - Not needed for MVP
- **Social login** - Not in scope for MVP
- **Password reset flows** - Can be added later, not MVP requirement
- **Hardcoded admin credentials** - Security risk, use environment variables instead
- **Overwriting existing admin account** - Only create if doesn't exist, preserve manual changes
- **Interactive CLI prompts for admin setup** - Doesn't work well with Docker Compose and automated deployments
- **Database migrations for user collection** - MongoDB is schemaless, no migrations needed

## Sources

- **HIGH Confidence**: FastAPI official documentation (https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) - Official recommendation for PyJWT and passlib
- **HIGH Confidence**: FastAPI Startup Events (https://fastapi.tiangolo.com/advanced/events/) - Official documentation for `@app.on_event("startup")`
- **HIGH Confidence**: PyJWT documentation (https://pyjwt.readthedocs.io/en/stable/) - Industry standard JWT library, latest version 2.12.1
- **HIGH Confidence**: passlib documentation (https://passlib.readthedocs.io/en/stable/) - Password hashing framework, version 1.7.4
- **HIGH Confidence**: argon2-cffi documentation (https://argon2-cffi.readthedocs.io/) - Argon2 CFFI bindings, latest version 25.1.0
- **HIGH Confidence**: MDN Web Storage API (https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage) - Browser API for token storage
- **HIGH Confidence**: Existing codebase analysis - MongoDB, Redis, FastAPI, React patterns already established
- **HIGH Confidence**: Existing authentication infrastructure - backend/app/services/auth_service.py, backend/app/services/user_service.py, backend/app/models/user.py
- **HIGH Confidence**: PyPI package verification - Verified current versions of PyJWT (2.12.1), passlib (1.7.4), argon2-cffi (25.1.0)

## Initial Admin Account Creation - Specific Stack

### Feature Overview
Create an initial admin user account automatically on first application startup using environment variables for credentials. This feature leverages existing authentication infrastructure without requiring additional dependencies.

### Required Changes (No New Libraries)

#### 1. Configuration Updates
**File**: `backend/app/config.py`
```python
class Settings:
    # ... existing settings ...
    INIT_USER: str = os.getenv("INIT_USER", "admin")
    INIT_PASSWORD: str = os.getenv("INIT_PASSWORD", "")
```

#### 2. Service Updates
**File**: `backend/app/services/user_service.py`
```python
async def create_admin_account():
    """Create admin account on first startup if it doesn't exist."""
    # Use INIT_USER and INIT_PASSWORD from settings
    username = settings.INIT_USER
    password = settings.INIT_PASSWORD or settings.ADMIN_PASSWORD

    existing_admin = await users_col.find_one({"username": username})
    if existing_admin:
        return

    admin_data = {
        "username": username,
        "password_hash": hash_password(password),
        "role": "admin",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login_at": None,
    }
    await users_col.insert_one(admin_data)
```

#### 3. Environment Variables
**File**: `.env`
```bash
INIT_USER=tam
INIT_PASSWORD=tam123
```

### Integration with Existing Infrastructure

**Already Implemented**:
- ✅ User model with validation (`backend/app/models/user.py`)
- ✅ Password hashing with Argon2id (`backend/app/services/auth_service.py`)
- ✅ JWT token creation and validation (`backend/app/services/auth_service.py`)
- ✅ MongoDB users collection with unique index (`backend/app/database.py`)
- ✅ Startup event handler (`backend/app/main.py`)
- ✅ User service with `create_admin_account()` function (`backend/app/services/user_service.py`)
- ✅ Admin account protection (prevent deletion/role change) (`backend/app/services/user_service.py`)

**Required Changes**:
- 🔄 Update `config.py` to add `INIT_USER` and `INIT_PASSWORD` settings
- 🔄 Update `user_service.py` to use `INIT_USER` and `INIT_PASSWORD` instead of hardcoded "admin"
- 🔄 Add validation for `INIT_USER` and `INIT_PASSWORD` to meet UserCreate requirements
- 🔄 Update `.env` to include `INIT_USER` and `INIT_PASSWORD` (already present in current .env)

### No New Dependencies Required

All necessary libraries are already installed and configured:
- ✅ FastAPI 0.115.0 - Startup events
- ✅ PyJWT >=2.8.0 - JWT authentication
- ✅ passlib[argon2] >=1.7.4 - Password hashing
- ✅ argon2-cffi >=23.1.0 - Argon2 bindings
- ✅ Motor 3.6.0 - Async MongoDB driver
- ✅ Pydantic 2.9.0 - Request/response validation

### Version Compatibility

| Package | Current Version | Latest Version | Status |
|---------|----------------|-----------------|--------|
| PyJWT | >=2.8.0 | 2.12.1 | ✅ Compatible |
| passlib | >=1.7.4 | 1.7.4 | ✅ Latest |
| argon2-cffi | >=23.1.0 | 25.1.0 | ✅ Compatible |
| FastAPI | 0.115.0 | 0.115.0 | ✅ Latest |
| Motor | 3.6.0 | 3.6.0 | ✅ Latest |
| Pydantic | 2.9.0 | 2.9.0 | ✅ Latest |

### Stack Patterns by Variant

**If INIT_USER and INIT_PASSWORD are provided:**
- Create admin account with those credentials on first startup
- Only create if admin account doesn't already exist
- Use existing `create_admin_account()` function in user_service.py

**If INIT_USER and INIT_PASSWORD are NOT provided:**
- Use default admin credentials (username: "admin", password: from ADMIN_PASSWORD env var)
- Log warning to console about using default credentials
- Recommend setting INIT_USER and INIT_PASSWORD in production

**If admin account already exists:**
- Skip creation on subsequent startups
- No changes to existing admin account
- Allows manual admin account management via API

### What NOT to Add for This Feature

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| New authentication libraries | Existing infrastructure is sufficient | Current PyJWT + passlib setup |
| Database migrations | MongoDB is schemaless | FastAPI startup event for initialization |
| Interactive CLI prompts | Doesn't work with Docker Compose | Environment variables |
| Hardcoded credentials | Security risk | INIT_USER and INIT_PASSWORD environment variables |
| Additional dependencies | Unnecessary complexity | Leverage existing services |
