# Phase 17: Backend Authentication Foundation - Research

**Researched:** 2026-04-18
**Domain:** Backend Authentication (FastAPI, JWT, Argon2)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** JWT token claims include user_id, username, role, exp (expiration), iat (issued at)
- **D-02:** JWT signing algorithm is HS256 (HMAC-SHA256)
- **D-03:** JWT includes issuer (iss) claim with service name
- **D-04:** JWT includes audience (aud) claim for API endpoint validation
- **D-05:** Use Argon2id variant for balanced security and performance
- **D-06:** Argon2 time_cost parameter is 3 (balanced performance)
- **D-07:** Argon2 memory_cost parameter is 128 MB (balanced memory usage)
- **D-08:** Argon2 parallelism parameter is 2 (dual thread)
- **D-09:** ACCESS_TOKEN_EXPIRE_MINUTES is set to 120 minutes
- **D-10:** Support refresh tokens for better user experience
- **D-11:** Refresh token expiration is 30 days
- **D-12:** Refresh tokens are stored in MongoDB users collection
- **D-13:** Invalid login credentials return "Invalid username or password" (generic for security)
- **D-14:** Expired JWT token returns "Token expired, please login again"
- **D-15:** Invalid JWT token returns "Invalid token, please login again"
- **D-16:** Missing JWT token returns "Authentication required, please login"
- **D-17:** User model fields: username, password_hash, role, created_at, last_login_at
- **D-18:** Role field supports three values: admin, editor, user
- **D-19:** Username validation: 3-20 characters, alphanumeric and underscore only
- **D-20:** Password strength validation: minimum 8 characters, at least 1 uppercase, 1 lowercase, 1 number
- **D-21:** Authentication implemented as FastAPI dependency (get_current_user)
- **D-22:** All endpoints protected by default, public endpoints opt-in
- **D-23:** User context injected as full user object into protected endpoints
- **D-24:** Token validation errors raise HTTPException directly in dependency
- **D-25:** Cache both user objects and JWT tokens in Redis for performance
- **D-26:** Cache TTL is 15 minutes
- **D-27:** Cache invalidation uses TTL only (no manual invalidation)
- **D-28:** Cache key structure: auth:user:{user_id}, auth:token:{token_id}

### the agent's Discretion
- JWT issuer claim value (service name)
- JWT audience claim value (API identifier)
- Index creation strategy for users collection (username unique index recommended)
- Admin account creation mechanism (startup event vs migration script)
- Login endpoint path (/api/login vs /api/auth/login)
- Refresh endpoint path (/api/refresh vs /api/auth/refresh)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| AUTH-01 | User can login with username and password | FastAPI OAuth2PasswordRequestForm + authenticate_user function |
| AUTH-02 | System generates JWT token on successful login | PyJWT encode() with HS256 algorithm and expiration |
| AUTH-03 | System validates JWT token on protected API requests | FastAPI OAuth2PasswordBearer + get_current_user dependency |
| AUTH-04 | System rejects requests with invalid or expired tokens | PyJWT decode() with InvalidTokenError handling |
| AUTH-06 | System hashes passwords using Argon2 before storage | passlib.argon2 with time_cost=3, memory_cost=128MB, parallelism=2 |
| SEC-05 | System uses SECRET_KEY environment variable for JWT signing | PyJWT encode() with SECRET_KEY from config |
| SEC-06 | System sets ACCESS_TOKEN_EXPIRE_MINUTES for token lifetime | PyJWT encode() with exp claim from timedelta |
</phase_requirements>

## Summary

This phase establishes the backend authentication infrastructure for the WordPress Writer Tool. The implementation uses FastAPI's built-in security utilities with PyJWT for token management and passlib with Argon2 for secure password hashing. The architecture follows FastAPI's dependency injection pattern for authentication middleware, enabling clean separation of concerns and easy testing.

The authentication system implements JWT-based stateless authentication with refresh tokens for improved user experience. Passwords are hashed using Argon2id with balanced parameters (time_cost=3, memory_cost=128MB, parallelism=2) to provide strong security without excessive resource consumption. Redis caching is integrated for performance optimization, with a 15-minute TTL for both user objects and JWT tokens.

**Primary recommendation:** Use FastAPI's OAuth2PasswordBearer and OAuth2PasswordRequestForm utilities with PyJWT for token management, and passlib.argon2 for password hashing. Follow the existing codebase patterns for routers, models, and database collections to maintain consistency.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| User authentication (login) | API / Backend | — | Validates credentials, issues JWT tokens |
| JWT token generation/validation | API / Backend | — | Cryptographic operations, token lifecycle management |
| Password hashing | API / Backend | — | Argon2 hashing for secure password storage |
| Authentication middleware | API / Backend | — | FastAPI dependency injection for request interception |
| User context injection | API / Backend | — | Provides user object to protected endpoints |
| Redis caching | API / Backend | — | Performance optimization for auth lookups |
| Token storage (refresh tokens) | Database / Storage | — | MongoDB users collection for persistence |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PyJWT | 2.8.0+ | JWT token generation and validation | Industry standard for JWT in Python, maintained by PyJWT team |
| passlib | 1.7.4+ | Password hashing with Argon2 | Comprehensive password hashing library, supports Argon2id |
| argon2-cffi | 23.1.0+ | Argon2 backend for passlib | High-performance Argon2 implementation, recommended by passlib |
| FastAPI Security | 0.115.0+ | OAuth2 utilities and dependency injection | Built-in FastAPI security tools, standard for FastAPI apps |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pydantic | 2.9.0+ | Request/response validation | Already in stack, used for auth models |
| Motor | 3.6.0+ | Async MongoDB driver | Already in stack, used for user storage |
| Redis | 5.0.0+ | Async Redis client | Already in stack, used for auth caching |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| passlib + argon2-cffi | bcrypt | bcrypt is simpler but less memory-hard, Argon2 is more resistant to GPU attacks |
| PyJWT | python-jose | python-jose has more features but PyJWT is simpler and more widely used |
| FastAPI OAuth2 utilities | Custom middleware | FastAPI utilities provide automatic OpenAPI docs integration |

**Installation:**
```bash
pip install "pyjwt>=2.8.0" "passlib[argon2]>=1.7.4" "argon2-cffi>=23.1.0"
```

**Version verification:**
```bash
pip show pyjwt passlib argon2-cffi
```

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Request                            │
└──────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Authentication Middleware                     │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  OAuth2PasswordBearer (extracts Bearer token)       │  │  │
│  │  │  get_current_user dependency (validates token)      │  │  │
│  │  │  get_current_active_user (checks user status)       │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                               │                                    │
│                               ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Protected Route Handler                       │  │
│  │  (receives current_user from dependency)                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Authentication Service                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Token Management (PyJWT)                                 │  │
│  │  - create_access_token() (encode with HS256)             │  │
│  │  - decode_token() (validate signature and expiration)    │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Password Hashing (passlib.argon2)                         │  │
│  │  - hash_password() (Argon2id with configured params)      │  │
│  │  - verify_password() (constant-time comparison)           │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  User Authentication                                      │  │
│  │  - authenticate_user() (lookup user, verify password)     │  │
│  │  - get_user() (fetch from MongoDB or Redis cache)         │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  MongoDB (users collection)                               │  │
│  │  - User documents with password_hash, role, refresh_token│  │
│  │  - Unique index on username                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Redis (auth cache)                                       │  │
│  │  - auth:user:{user_id} (cached user object, 15min TTL)   │  │
│  │  - auth:token:{token_id} (cached token validation)       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure
```
backend/
├── app/
│   ├── routers/
│   │   └── auth.py              # Authentication endpoints (login, refresh)
│   ├── models/
│   │   └── user.py              # User Pydantic models (Create, Update, Response)
│   ├── services/
│   │   └── auth_service.py      # Authentication business logic
│   ├── dependencies/
│   │   └── auth.py              # FastAPI dependencies (get_current_user)
│   ├── database.py             # Add users_col and create_indexes()
│   ├── config.py                # Add SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
│   └── main.py                  # Include auth router
└── tests/
    ├── test_auth.py             # Authentication tests
    └── conftest.py              # Add users_col to cleanup
```

### Pattern 1: FastAPI Authentication Dependency
**What:** Use FastAPI's `Depends()` with `OAuth2PasswordBearer` to extract and validate JWT tokens from the `Authorization` header.
**When to use:** For protecting API endpoints that require authentication.
**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(username)
    if user is None:
        raise credentials_exception
    return user
```

### Pattern 2: JWT Token Generation with Expiration
**What:** Use PyJWT to encode tokens with expiration time and custom claims.
**When to use:** When issuing access tokens and refresh tokens after successful authentication.
**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
from datetime import datetime, timedelta, timezone
import jwt

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### Pattern 3: Argon2 Password Hashing
**What:** Use passlib.argon2 with configured parameters for secure password hashing.
**When to use:** When creating new users or updating passwords.
**Example:**
```python
# Source: https://passlib.readthedocs.io/en/stable/lib/passlib.hash.argon2.html
from passlib.hash import argon2

# Configure Argon2id with balanced parameters
password_hash = argon2.using(
    rounds=3,           # time_cost
    memory_cost=128000, # 128 MB in bytes
    parallelism=2,      # dual thread
    salt_size=16,
    hash_len=32
)

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
```

### Pattern 4: Constant-Time Password Verification
**What:** Always verify passwords against a dummy hash when user doesn't exist to prevent timing attacks.
**When to use:** In authentication function to prevent username enumeration.
**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
DUMMY_HASH = password_hash.hash("dummypassword")

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        # Verify against dummy hash to prevent timing attacks
        password_hash.verify(password, DUMMY_HASH)
        return False
    if not password_hash.verify(password, user.password_hash):
        return False
    return user
```

### Pattern 5: Redis Caching for Auth Performance
**What:** Cache user objects and token validations in Redis with TTL to reduce database load.
**When to use:** For frequently accessed user data and token validations.
**Example:**
```python
# Source: Based on existing redis_client.py pattern
import json
from app.redis_client import redis_client

async def get_user_cached(user_id: str) -> dict | None:
    """Get user from Redis cache or MongoDB."""
    cache_key = f"auth:user:{user_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Fetch from MongoDB
    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if user:
        # Cache for 15 minutes
        await redis_client.set(cache_key, json.dumps(user), ex=900)
    return user
```

### Anti-Patterns to Avoid
- **Storing passwords in plaintext:** Always hash passwords with Argon2 before storage
- **Using weak hashing algorithms:** Avoid MD5, SHA1, SHA256 for passwords — use Argon2
- **Revealing which field is invalid:** Return generic "Invalid username or password" for both cases
- **Hardcoding SECRET_KEY:** Always use environment variable, generate with `openssl rand -hex 32`
- **Skipping token expiration:** Always set exp claim to prevent indefinite token validity
- **Timing attacks on authentication:** Always verify against dummy hash when user doesn't exist
- **Storing refresh tokens in JWT:** Store refresh tokens in MongoDB, not in JWT payload

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JWT token encoding/decoding | Custom JWT implementation | PyJWT library | Handles base64url encoding, signature verification, expiration validation |
| Password hashing | Custom bcrypt/SHA implementation | passlib.argon2 | Handles salt generation, memory-hard parameters, constant-time comparison |
| OAuth2 Bearer token extraction | Custom header parsing | FastAPI OAuth2PasswordBearer | Automatic OpenAPI docs integration, standardized error handling |
| Token validation middleware | Custom middleware | FastAPI Depends() | Clean dependency injection, easy testing, automatic error propagation |
| Password strength validation | Custom regex | Pydantic validators | Declarative validation, automatic error messages, type safety |
| Redis caching logic | Custom cache implementation | Existing redis_client.py pattern | Consistent with codebase, handles JSON serialization, TTL management |

**Key insight:** Authentication is security-critical code. Hand-rolling implementations introduces vulnerabilities that have been fixed in battle-tested libraries. Use standard libraries and follow established patterns.

## Common Pitfalls

### Pitfall 1: Timing Attack Vulnerability
**What goes wrong:** Authentication endpoint responds faster when username doesn't exist, allowing attackers to enumerate valid usernames.
**Why it happens:** Password verification is skipped when user is not found, making the endpoint faster.
**How to avoid:** Always verify password against a dummy hash when user doesn't exist, ensuring constant response time.
**Warning signs:** Authentication function has early return when user is None without password verification.

### Pitfall 2: Weak SECRET_KEY
**What goes wrong:** JWT tokens can be forged if SECRET_KEY is predictable or too short.
**Why it happens:** Using hardcoded keys, short keys, or keys generated from weak randomness.
**How to avoid:** Generate SECRET_KEY with `openssl rand -hex 32` (32 bytes = 256 bits), store in environment variable.
**Warning signs:** SECRET_KEY is hardcoded in code, shorter than 32 characters, or generated from simple strings.

### Pitfall 3: Missing Token Expiration
**What goes wrong:** JWT tokens never expire, allowing indefinite access if compromised.
**Why it happens:** Forgetting to set exp claim or using very long expiration times.
**How to avoid:** Always set exp claim with reasonable expiration (120 minutes for access tokens, 30 days for refresh tokens).
**Warning signs:** Token generation doesn't include exp claim, or expiration is set to years.

### Pitfall 4: Insecure Error Messages
**What goes wrong:** Error messages reveal whether username or password is incorrect, aiding attackers.
**Why it happens:** Using specific error messages like "User not found" or "Invalid password".
**How to avoid:** Return generic "Invalid username or password" for both cases.
**Warning signs:** Multiple error messages for authentication failures with different text.

### Pitfall 5: Argon2 Parameter Misconfiguration
**What goes wrong:** Argon2 parameters are too weak (fast hashing) or too strong (excessive resource usage).
**Why it happens:** Using default parameters or copying values without understanding their impact.
**How to avoid:** Use balanced parameters: time_cost=3, memory_cost=128MB, parallelism=2 for MVP. Adjust based on security requirements.
**Warning signs:** Using default Argon2 parameters, or memory_cost < 64MB, or time_cost < 2.

### Pitfall 6: Missing Username Unique Index
**What goes wrong:** Multiple users can be created with the same username, causing authentication conflicts.
**Why it happens:** Forgetting to create unique index on username field in MongoDB.
**How to avoid:** Create unique index on username in create_indexes() function.
**Warning signs:** User creation doesn't check for duplicate usernames, or relies on application-level validation only.

### Pitfall 7: Cache Invalidation Issues
**What goes wrong:** Stale user data in Redis cache after user updates or password changes.
**Why it happens:** Relying only on TTL without manual invalidation for critical updates.
**How to avoid:** For password changes, manually invalidate cache by deleting auth:user:{user_id} key.
**Warning signs:** User can still authenticate after password change until cache expires.

### Pitfall 8: Token Leakage in Logs
**What goes wrong:** JWT tokens are logged in plaintext, exposing them to anyone with log access.
**Why it happens:** Logging request headers or full token objects without masking.
**How to avoid:** Never log full tokens. Log only first 8 characters with "..." suffix for debugging.
**Warning signs:** Logs contain full Authorization headers or token strings.

## Code Examples

Verified patterns from official sources:

### JWT Token Generation with Custom Claims
```python
# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
from datetime import datetime, timedelta, timezone
import jwt

def create_access_token(user_id: str, username: str, role: str) -> str:
    """Create JWT access token with custom claims."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": username,              # Subject (username)
        "user_id": user_id,           # Custom claim
        "username": username,         # Custom claim
        "role": role,                 # Custom claim
        "iss": "wordpress-writer",    # Issuer (service name)
        "aud": "wordpress-writer-api",# Audience (API identifier)
        "exp": expire,                # Expiration time
        "iat": now,                   # Issued at time
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

### JWT Token Validation
```python
# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

def decode_token(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer="wordpress-writer",
            audience="wordpress-writer-api"
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired, please login again"
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token, please login again"
        )
```

### Argon2 Password Hashing with Configured Parameters
```python
# Source: https://passlib.readthedocs.io/en/stable/lib/passlib.hash.argon2.html
from passlib.hash import argon2

# Configure Argon2id with balanced parameters
password_hasher = argon2.using(
    type="id",           # Argon2id variant
    time_cost=3,        # Number of iterations
    memory_cost=128000, # Memory in bytes (128 MB)
    parallelism=2,      # Number of threads
    salt_size=16,       # Salt size in bytes
    hash_len=32         # Hash length in bytes
)

def hash_password(password: str) -> str:
    """Hash password using Argon2id."""
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash (constant-time)."""
    return password_hasher.verify(plain_password, hashed_password)
```

### FastAPI Authentication Dependency
```python
# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> dict:
    """Extract and validate JWT token, return user object."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception

    user = await get_user(username)
    if user is None:
        raise credentials_exception

    return user
```

### Login Endpoint with OAuth2PasswordRequestForm
```python
# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

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

    # Update last_login_at
    await users_col.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login_at": datetime.now(timezone.utc).isoformat()}}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )
```

### Refresh Token Endpoint
```python
# Source: Based on JWT best practices
@router.post("/refresh")
async def refresh_token(refresh_token: str) -> TokenResponse:
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
            refresh_token=refresh_token  # Return same refresh token
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| bcrypt | Argon2id | 2015 (Password Hashing Competition) | Argon2 is memory-hard, more resistant to GPU/ASIC attacks |
| PBKDF2 | Argon2id | 2015 | PBKDF2 is not memory-hard, vulnerable to parallel attacks |
| SHA256 for passwords | Argon2id | 2015 | SHA256 is too fast, vulnerable to brute force |
| Session-based auth | JWT tokens | 2018+ | Stateless, scalable, easier for microservices |
| Long-lived tokens | Short access + refresh tokens | 2019+ | Better security, token revocation capability |

**Deprecated/outdated:**
- **MD5 for passwords:** Broken, vulnerable to collision attacks
- **SHA1 for passwords:** Too fast, vulnerable to brute force
- **Plaintext password storage:** Never acceptable, immediate security risk
- **Hardcoded SECRET_KEY:** Allows token forgery if code is exposed
- **JWT without expiration:** Allows indefinite access if token is compromised

## Assumptions Log

> List all claims tagged `[ASSUMED]` in this research. The planner and discuss-phase use this
> section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | JWT issuer claim value should be "wordpress-writer" | Standard Stack | Token validation may fail if issuer doesn't match expectation |
| A2 | JWT audience claim value should be "wordpress-writer-api" | Standard Stack | Token validation may fail if audience doesn't match expectation |
| A3 | Admin account creation should use startup event in main.py | the agent's Discretion | May not align with deployment strategy if migration script preferred |
| A4 | Login endpoint path should be /api/auth/login | the agent's Discretion | Frontend may need updates if different path is chosen |
| A5 | Refresh endpoint path should be /api/auth/refresh | the agent's Discretion | Frontend may need updates if different path is chosen |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed.

## Open Questions

1. **JWT issuer and audience claim values**
   - What we know: Claims must be included in JWT tokens for validation
   - What's unclear: Exact string values for iss and aud claims
   - Recommendation: Use "wordpress-writer" for issuer and "wordpress-writer-api" for audience, but confirm with user

2. **Admin account creation mechanism**
   - What we know: Admin account must be created on first startup using ADMIN_PASSWORD env var
   - What's unclear: Whether to use FastAPI startup event or migration script
   - Recommendation: Use FastAPI startup event in main.py for simplicity, but confirm with user

3. **API endpoint paths**
   - What we know: Need login and refresh endpoints
   - What's unclear: Whether to use /api/login or /api/auth/login
   - Recommendation: Use /api/auth/login and /api/auth/refresh for consistency, but confirm with user

## Environment Availability

> Skip this section if the phase has no external dependencies (code/config-only changes).

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11+ | Backend runtime | ✓ | 3.12.3 | — |
| MongoDB | User storage | ✓ | — | — |
| Redis | Auth caching | ✓ | — | — |
| PyJWT | JWT token management | ✗ | — | Must install |
| passlib | Password hashing | ✗ | — | Must install |
| argon2-cffi | Argon2 backend | ✗ | — | Must install |

**Missing dependencies with no fallback:**
- PyJWT: Required for JWT token generation and validation
- passlib: Required for password hashing with Argon2
- argon2-cffi: Required as Argon2 backend for passlib

**Missing dependencies with fallback:**
- None — all missing dependencies are required for authentication functionality

**Installation required:**
```bash
pip install "pyjwt>=2.8.0" "passlib[argon2]>=1.7.4" "argon2-cffi>=23.1.0"
```

## Validation Architecture

> Skip this section entirely if workflow.nyquist_validation is explicitly set to false in .planning/config.json. If the key is absent, treat as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 7.4+ with pytest-asyncio 0.23+ |
| Config file | None — default pytest discovery |
| Quick run command | `pytest backend/tests/test_auth.py -x -v` |
| Full suite command | `pytest backend/tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AUTH-01 | User can login with username and password | integration | `pytest backend/tests/test_auth.py::test_login_success -x` | ❌ Wave 0 |
| AUTH-02 | System generates JWT token on successful login | unit | `pytest backend/tests/test_auth.py::test_login_returns_token -x` | ❌ Wave 0 |
| AUTH-03 | System validates JWT token on protected API requests | integration | `pytest backend/tests/test_auth.py::test_protected_endpoint_with_valid_token -x` | ❌ Wave 0 |
| AUTH-04 | System rejects requests with invalid or expired tokens | integration | `pytest backend/tests/test_auth.py::test_protected_endpoint_rejects_invalid_token -x` | ❌ Wave 0 |
| AUTH-06 | System hashes passwords using Argon2 before storage | unit | `pytest backend/tests/test_auth.py::test_password_hashing -x` | ❌ Wave 0 |
| SEC-05 | System uses SECRET_KEY environment variable for JWT signing | unit | `pytest backend/tests/test_auth.py::test_token_uses_secret_key -x` | ❌ Wave 0 |
| SEC-06 | System sets ACCESS_TOKEN_EXPIRE_MINUTES for token lifetime | unit | `pytest backend/tests/test_auth.py::test_token_expiration -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest backend/tests/test_auth.py -x -v`
- **Per wave merge:** `pytest backend/tests/ -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `backend/tests/test_auth.py` — Covers AUTH-01 through AUTH-06, SEC-05 through SEC-06
- [ ] `backend/tests/conftest.py` — Add users_col to cleanup fixture
- [ ] Framework install: Already present (pytest>=7.4.0, pytest-asyncio>=0.23.0)

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled). Omit only if explicitly `false` in config.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | JWT tokens with Argon2 password hashing |
| V3 Session Management | yes | JWT access tokens (120min) + refresh tokens (30 days) |
| V4 Access Control | yes | Role-based access control (admin, editor, user) |
| V5 Input Validation | yes | Pydantic models for username/password validation |
| V6 Cryptography | yes | PyJWT with HS256, passlib.argon2 for password hashing |

### Known Threat Patterns for FastAPI + JWT + Argon2

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Timing attack (username enumeration) | Information Disclosure | Constant-time password verification with dummy hash |
| JWT token forgery (weak SECRET_KEY) | Tampering | Use strong SECRET_KEY (32 bytes from openssl rand -hex 32) |
| Brute force password cracking | Tampering | Argon2id with memory_cost=128MB, time_cost=3, parallelism=2 |
| Token replay attack | Spoofing | Short access token expiration (120 minutes) |
| Token leakage in logs | Information Disclosure | Never log full tokens, mask first 8 chars only |
| SQL injection (if using SQL) | Tampering | Not applicable — using MongoDB with parameterized queries |
| Stored XSS (if user data reflected) | Tampering | Not applicable — API returns JSON, not HTML |
| CSRF attack | Spoofing | Not applicable — JWT in Authorization header, not cookies |

### Security Best Practices

1. **SECRET_KEY Management**
   - Generate with `openssl rand -hex 32` (32 bytes = 256 bits)
   - Store in environment variable, never in code
   - Rotate periodically in production
   - Use different keys for development/staging/production

2. **Password Hashing**
   - Use Argon2id with balanced parameters (time_cost=3, memory_cost=128MB, parallelism=2)
   - Never store plaintext passwords
   - Use constant-time verification to prevent timing attacks
   - Hash passwords on client side before transmission (optional, adds defense in depth)

3. **JWT Token Security**
   - Set reasonable expiration (120 minutes for access, 30 days for refresh)
   - Include iss and aud claims for additional validation
   - Use HS256 algorithm with strong SECRET_KEY
   - Validate all claims (exp, iat, iss, aud) on every request
   - Implement token revocation for refresh tokens (store in MongoDB)

4. **Error Handling**
   - Return generic error messages for authentication failures
   - Use HTTP 401 for authentication errors
   - Include WWW-Authenticate: Bearer header for OAuth2 compliance
   - Log authentication failures (without sensitive data) for monitoring

5. **Rate Limiting**
   - Implement rate limiting on login endpoint (e.g., 5 attempts per minute)
   - Use Redis to track attempt counts by IP or username
   - Lock accounts after excessive failed attempts (optional for MVP)

6. **HTTPS Enforcement**
   - Always use HTTPS in production
   - Set HSTS header to enforce HTTPS
   - Never transmit tokens over HTTP

## Sources

### Primary (HIGH confidence)
- FastAPI Security Tutorial - https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ - Complete JWT authentication example with PyJWT and passlib
- Passlib Argon2 Documentation - https://passlib.readthedocs.io/en/stable/lib/passlib.hash.argon2.html - Argon2 API reference and configuration
- PyJWT Documentation - https://pyjwt.readthedocs.io/ - JWT encoding/decoding API
- Existing codebase patterns - `backend/app/routers/ai_providers.py`, `backend/app/models/ai_provider.py`, `backend/app/database.py`, `backend/app/config.py` - Established patterns for routers, models, database, and configuration

### Secondary (MEDIUM confidence)
- Password Hashing Competition - https://password-hashing.net/ - Argon2 selection rationale
- OWASP Password Storage Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html - Password hashing best practices
- JWT.io - https://jwt.io/ - JWT token structure and validation

### Tertiary (LOW confidence)
- None — all findings verified from official documentation or existing codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified from official documentation (FastAPI, passlib, PyJWT)
- Architecture: HIGH - Based on official FastAPI patterns and existing codebase structure
- Pitfalls: HIGH - Based on security best practices and common vulnerabilities documented in OWASP

**Research date:** 2026-04-18
**Valid until:** 2026-05-18 (30 days - stable authentication libraries with infrequent breaking changes)
