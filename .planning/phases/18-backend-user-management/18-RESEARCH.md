# Phase 18: Backend User Management - Research

**Researched:** 2026-04-18
**Domain:** Backend User Management (FastAPI, MongoDB, CRUD operations)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Admin account created on first startup using FastAPI startup event
- **D-02:** Startup event checks if admin exists, creates if missing (safe idempotent approach)
- **D-03:** Admin account uses ADMIN_PASSWORD environment variable for password
- **D-04:** Admin account has role="admin" and username="admin"
- **D-05:** User creation endpoint path: POST /api/users
- **D-06:** User listing endpoint path: GET /api/users
- **D-07:** User deletion endpoint path: DELETE /api/users/{id}
- **D-08:** Password reset endpoint path: POST /api/users/{id}/reset-password
- **D-09:** Role update endpoint path: PUT /api/users/{id}/role
- **D-10:** User deletion reassigns all posts owned by deleted user to admin
- **D-11:** User deletion always succeeds even if user has no posts to reassign
- **D-12:** User deletion is permanent (no soft delete)
- **D-13:** Password reset is admin-only functionality
- **D-14:** Password reset is a separate endpoint: POST /api/users/{id}/reset-password
- **D-15:** Password reset requires admin authentication via get_current_user dependency
- **D-16:** Role update is admin-only functionality
- **D-17:** Role update is a separate endpoint: PUT /api/users/{id}/role
- **D-18:** Role update requires admin authentication via get_current_user dependency
- **D-19:** Currently no role-based access control — users just use the service (roles stored for future use)

### the agent's Discretion
- ADMIN_PASSWORD environment variable default value
- Admin account username (default: "admin")
- Admin account role (default: "admin")
- User update endpoint structure (PUT /api/users/{id} with optional fields)
- Response format for user listing (pagination, sorting, filtering)
- Error messages for user management operations
- Whether to include password_hash in user response (should be excluded for security)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| USER-01 | System creates admin account on first startup using ADMIN_PASSWORD environment variable | FastAPI startup event with @app.on_event("startup") or lifespan parameter |
| USER-02 | Admin can create new user accounts with username and password | POST /api/users endpoint with UserCreate model, hash_password() from auth_service |
| USER-03 | Admin can list all user accounts | GET /api/users endpoint with users_col.find() and UserResponse serialization |
| USER-04 | Admin can delete user accounts | DELETE /api/users/{id} endpoint with users_col.delete_one() |
| USER-05 | System stores user accounts in MongoDB users collection | users_col already exists in database.py with unique username index |
| USER-06 | System validates username uniqueness on user creation | MongoDB unique index on username field + Pydantic validation |
| USER-07 | System validates password strength on user creation | Pydantic field_validator in UserCreate model (already implemented) |
</phase_requirements>

## Summary

This phase implements backend user management functionality for the WordPress Writer Tool, enabling admin users to create, list, delete, and manage user accounts. The implementation builds on the authentication infrastructure established in Phase 17, leveraging existing JWT token validation, Argon2 password hashing, and MongoDB user storage patterns.

The phase introduces five new admin-only endpoints for user management operations, protected by the `get_current_user` dependency with role-based access control. Admin account creation is handled via FastAPI startup event, ensuring idempotent initialization on first application startup. All user management operations follow established codebase patterns for routers, models, and database operations, maintaining consistency with the existing architecture.

**Primary recommendation:** Use FastAPI's `@app.on_event("startup")` for admin account creation (as specified in CONTEXT.md), create a `get_current_admin` dependency for role-based access control, and follow existing router/service/model patterns from Phase 17 for user management endpoints.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Admin account creation (startup) | API / Backend | — | FastAPI startup event executes before request handling |
| User CRUD operations | API / Backend | — | Business logic for user management |
| Admin-only endpoint protection | API / Backend | — | FastAPI dependency injection for role checking |
| Password hashing | API / Backend | — | Argon2 hashing for secure password storage |
| User storage | Database / Storage | — | MongoDB users collection for persistence |
| Username uniqueness validation | Database / Storage | — | MongoDB unique index enforces constraint |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.115.0 | Web framework and dependency injection | Already in stack, provides startup events and Depends() |
| Pydantic | 2.9.0 | Request/response validation | Already in stack, UserCreate/UserUpdate/UserResponse models exist |
| Motor | 3.6.0 | Async MongoDB driver | Already in stack, users_col already defined |
| passlib | 1.7.4+ | Password hashing with Argon2 | Already in stack, hash_password() function exists |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| PyJWT | 2.8.0+ | JWT token validation | Already in stack, used by get_current_user dependency |
| pytest | 7.4.0+ | Testing framework | Already in stack, test_auth.py provides patterns |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| @app.on_event("startup") | lifespan parameter | lifespan is recommended but CONTEXT.md specifies @app.on_event |
| get_current_admin dependency | Custom middleware | Dependency injection is cleaner and more testable |
| MongoDB unique index | Application-level validation only | Database-level constraint prevents race conditions |

**Installation:**
```bash
# All dependencies already installed via requirements.txt
pip install fastapi==0.115.0 pydantic==2.9.0 motor==3.6.0 "passlib[argon2]>=1.7.4" "pyjwt>=2.8.0"
```

**Version verification:**
```bash
# Verified from requirements.txt
# fastapi==0.115.0
# pydantic==2.9.0
# motor==3.6.0
# passlib[argon2]>=1.7.4
# pyjwt>=2.8.0
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
│ │              Startup Event Handler                          │  │
│ │  ┌────────────────────────────────────────────────────┐  │  │
│ │  │  @app.on_event("startup")                          │  │  │
│ │  │  - Check if admin user exists                      │  │  │
│ │  │  - Create admin if missing (idempotent)            │  │  │
│ │  └────────────────────────────────────────────────────┘  │  │
│ └──────────────────────────────────────────────────────────┘  │
│                               │                                    │
│                               ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│ │              Authentication Middleware                     │  │
│ │  ┌────────────────────────────────────────────────────┐  │  │
│ │  │  get_current_user (validates JWT token)            │  │  │
│ │  │  get_current_admin (checks role == "admin")        │  │  │
│ │  └────────────────────────────────────────────────────┘  │  │
│ └──────────────────────────────────────────────────────────┘  │
│                               │                                    │
│                               ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│ │              User Management Router                        │  │
│ │  ┌────────────────────────────────────────────────────┐  │  │
│ │  │  POST   /api/users              (create user)       │  │  │
│ │  │  GET    /api/users              (list users)        │  │  │
│ │  │  DELETE /api/users/{id}         (delete user)       │  │  │
│ │  │  POST   /api/users/{id}/reset-password              │  │  │
│ │  │  PUT    /api/users/{id}/role                        │  │  │
│ │  └────────────────────────────────────────────────────┘  │  │
│ └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Authentication Service                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│ │  Password Hashing (passlib.argon2)                         │  │
│ │  - hash_password() (already exists)                       │  │
│ │  - verify_password() (already exists)                     │  │
│ └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│ │  User Management Service                                  │  │
│ │  - create_user() (new)                                    │  │
│ │  - list_users() (new)                                     │  │
│ │  - delete_user() (new)                                    │  │
│ │  - reset_user_password() (new)                           │  │
│ │  - update_user_role() (new)                              │  │
│ └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│ │  MongoDB (users collection)                               │  │
│ │  - User documents with username, password_hash, role      │  │
│ │  - Unique index on username (already exists)             │  │
│ └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure
```
backend/
├── app/
│   ├── routers/
│   │   ├── auth.py              # Authentication endpoints (existing)
│   │   └── users.py             # User management endpoints (new)
│   ├── models/
│   │   └── user.py              # User Pydantic models (existing)
│   ├── services/
│   │   ├── auth_service.py      # Authentication service (existing)
│   │   └── user_service.py      # User management service (new)
│   ├── dependencies/
│   │   └── auth.py              # Add get_current_admin dependency (update)
│   ├── database.py             # users_col already exists
│   ├── config.py                # Add ADMIN_PASSWORD (update)
│   └── main.py                  # Add startup event and users router (update)
└── tests/
    ├── test_auth.py             # Authentication tests (existing)
    ├── test_users.py            # User management tests (new)
    └── conftest.py              # Test fixtures (existing)
```

### Pattern 1: FastAPI Startup Event for Admin Account Creation
**What:** Use `@app.on_event("startup")` to create admin account on first startup.
**When to use:** For one-time initialization tasks that must run before request handling.
**Example:**
```python
# Source: https://fastapi.tiangolo.com/advanced/events/
from fastapi import FastAPI
from app.services.auth_service import hash_password
from app.database import users_col
from bson import ObjectId
from datetime import datetime, timezone

app = FastAPI()

@app.on_event("startup")
async def create_admin_user():
    """Create admin user on first startup if it doesn't exist."""
    # Check if admin already exists
    existing_admin = await users_col.find_one({"username": "admin"})
    if existing_admin:
        return  # Admin already exists, nothing to do

    # Create admin user
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_user = {
        "username": "admin",
        "password_hash": hash_password(admin_password),
        "role": "admin",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login_at": None,
    }

    try:
        await users_col.insert_one(admin_user)
        print("[STARTUP] Admin user created successfully")
    except Exception as e:
        print(f"[STARTUP] Failed to create admin user: {e}")
```

### Pattern 2: Admin-Only Endpoint Protection with Role Checking
**What:** Create a `get_current_admin` dependency that checks if the current user has admin role.
**When to use:** For protecting endpoints that require admin privileges.
**Example:**
```python
# Source: Based on FastAPI dependency injection patterns
from fastapi import Depends, HTTPException, status
from typing import Annotated
from app.dependencies.auth import get_current_user

async def get_current_admin(
    current_user: Annotated[dict, Depends(get_current_user)]
) -> dict:
    """Get current admin user (raises 403 if not admin)."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
```

### Pattern 3: User Creation with Validation
**What:** Create user endpoint with username uniqueness validation and password hashing.
**When to use:** For creating new user accounts via admin interface.
**Example:**
```python
# Source: Based on existing auth.py patterns
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from bson import ObjectId
from datetime import datetime, timezone

from app.models.user import UserCreate, UserResponse
from app.services.auth_service import hash_password
from app.database import users_col
from app.dependencies.auth import get_current_admin

router = APIRouter(prefix="/api/users", tags=["User Management"])

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> UserResponse:
    """Create a new user account (admin only)."""
    # Check if username already exists
    existing_user = await users_col.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Create user document
    new_user = {
        "username": user_data.username,
        "password_hash": hash_password(user_data.password),
        "role": user_data.role,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login_at": None,
    }

    try:
        result = await users_col.insert_one(new_user)
        new_user["_id"] = result.inserted_id
        return UserResponse(
            id=str(new_user["_id"]),
            username=new_user["username"],
            role=new_user["role"],
            created_at=new_user["created_at"],
            last_login_at=new_user["last_login_at"]
        )
    except Exception as e:
        # Handle duplicate key error from unique index
        if "duplicate key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
```

### Pattern 4: User Listing with Response Serialization
**What:** List all users with proper response model serialization (excluding password_hash).
**When to use:** For admin to view all user accounts.
**Example:**
```python
@router.get("", response_model=list[UserResponse])
async def list_users(
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> list[UserResponse]:
    """List all user accounts (admin only)."""
    users = await users_col.find().to_list(length=None)

    # Convert to UserResponse (excludes password_hash)
    return [
        UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            role=user["role"],
            created_at=user["created_at"],
            last_login_at=user.get("last_login_at")
        )
        for user in users
    ]
```

### Pattern 5: User Deletion with Post Reassignment (Future)
**What:** Delete user and reassign their posts to admin to prevent orphaned content.
**When to use:** When deleting user accounts.
**Example:**
```python
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_admin: Annotated[dict, Depends(get_current_admin)]
):
    """Delete a user account and reassign posts to admin (admin only)."""
    # Check if user exists
    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    user = await users_col.find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent deleting admin account
    if user["username"] == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin account"
        )

    # TODO: Reassign posts to admin when post ownership is implemented
    # await posts_col.update_many(
    #     {"owner_id": user_id},
    #     {"$set": {"owner_id": str(current_admin["_id"])}}
    # )

    # Delete user
    await users_col.delete_one({"_id": user_obj_id})

    return None  # 204 No Content
```

### Pattern 6: Password Reset Endpoint
**What:** Admin-only endpoint to reset a user's password.
**When to use:** When admin needs to reset a user's password.
**Example:**
```python
from pydantic import BaseModel

class PasswordResetRequest(BaseModel):
    new_password: str = Field(..., min_length=8)

@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: str,
    password_data: PasswordResetRequest,
    current_admin: Annotated[dict, Depends(get_current_admin)]
):
    """Reset a user's password (admin only)."""
    # Check if user exists
    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    user = await users_col.find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update password
    await users_col.update_one(
        {"_id": user_obj_id},
        {"$set": {"password_hash": hash_password(password_data.new_password)}}
    )

    return {"message": "Password reset successfully"}
```

### Pattern 7: Role Update Endpoint
**What:** Admin-only endpoint to update a user's role.
**When to use:** When admin needs to change a user's role.
**Example:**
```python
from app.models.user import UserUpdate

@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    role_data: UserUpdate,
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> UserResponse:
    """Update a user's role (admin only)."""
    # Check if user exists
    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    user = await users_col.find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent changing admin role
    if user["username"] == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change admin role"
        )

    # Update role
    if role_data.role is not None:
        await users_col.update_one(
            {"_id": user_obj_id},
            {"$set": {"role": role_data.role}}
        )

    # Return updated user
    updated_user = await users_col.find_one({"_id": user_obj_id})
    return UserResponse(
        id=str(updated_user["_id"]),
        username=updated_user["username"],
        role=updated_user["role"],
        created_at=updated_user["created_at"],
        last_login_at=updated_user.get("last_login_at")
    )
```

### Anti-Patterns to Avoid
- **Returning password_hash in API responses:** Always exclude password_hash from UserResponse model for security
- **Deleting admin account:** Prevent deletion of admin account to avoid lockout
- **Skipping role validation:** Always check user role in admin-only endpoints
- **Relying only on application-level validation:** Use MongoDB unique index for username uniqueness to prevent race conditions
- **Hardcoding admin credentials:** Always use ADMIN_PASSWORD environment variable
- **Not handling duplicate key errors:** Catch MongoDB duplicate key errors and return user-friendly messages
- **Including password in logs:** Never log passwords or password hashes

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password hashing | Custom bcrypt/SHA implementation | passlib.argon2 (already exists) | Handles salt generation, memory-hard parameters, constant-time comparison |
| JWT token validation | Custom token parsing | get_current_user dependency (already exists) | Handles signature verification, expiration validation, error handling |
| Username uniqueness validation | Application-level check only | MongoDB unique index (already exists) | Prevents race conditions, enforces constraint at database level |
| Request/response validation | Custom validation logic | Pydantic models (already exist) | Declarative validation, automatic error messages, type safety |
| Admin role checking | Custom middleware | FastAPI Depends() with get_current_admin | Clean dependency injection, easy testing, automatic error propagation |

**Key insight:** User management is security-critical code. Hand-rolling implementations introduces vulnerabilities that have been fixed in battle-tested libraries. Use standard libraries and follow established patterns from Phase 17.

## Common Pitfalls

### Pitfall 1: Startup Event Race Conditions
**What goes wrong:** Admin account creation fails if multiple workers start simultaneously, causing duplicate key errors.
**Why it happens:** Multiple workers check for admin existence at the same time, both see it doesn't exist, and both try to create it.
**How to avoid:** Use idempotent approach with try/except to handle duplicate key errors gracefully. The startup event should check if admin exists first, and only create if missing.
**Warning signs:** Startup logs show duplicate key errors or admin creation failures.

### Pitfall 2: Exposing password_hash in API Responses
**What goes wrong:** UserResponse model includes password_hash field, exposing hashed passwords in API responses.
**Why it happens:** Forgetting to exclude password_hash from response model or using MongoDB document directly.
**How to avoid:** Always use UserResponse model which explicitly excludes password_hash. Never return raw MongoDB documents.
**Warning signs:** API responses contain password_hash field.

### Pitfall 3: Deleting Admin Account
**What goes wrong:** Admin deletes their own account, causing lockout with no way to recover.
**Why it happens:** Not checking if the user being deleted is the admin account.
**How to avoid:** Always check if username == "admin" before deletion and raise HTTPException if true.
**Warning signs:** No validation before user deletion.

### Pitfall 4: Missing Role Validation in Admin Endpoints
**What goes wrong:** Non-admin users can access admin-only endpoints by having a valid JWT token.
**Why it happens:** Forgetting to check user role in admin-only endpoints.
**How to avoid:** Always use get_current_admin dependency for admin-only endpoints, which checks role == "admin".
**Warning signs:** Admin endpoints only use get_current_user without role checking.

### Pitfall 5: Not Handling MongoDB Duplicate Key Errors
**What goes wrong:** Username uniqueness validation fails due to race conditions, causing 500 errors instead of 400 errors.
**Why it happens:** Relying only on application-level validation without handling database-level duplicate key errors.
**How to avoid:** Catch duplicate key errors from MongoDB and return user-friendly 400 error messages.
**Warning signs:** 500 errors when creating users with duplicate usernames.

### Pitfall 6: Password Reset Without Validation
**What goes wrong:** Admin can reset password to weak passwords, bypassing password strength validation.
**Why it happens:** Not reusing UserCreate password validation logic in password reset endpoint.
**How to avoid:** Use the same password validation logic (Pydantic field_validator) for password reset as for user creation.
**Warning signs:** Password reset accepts weak passwords.

### Pitfall 7: Not Invalidating Redis Cache on Password Change
**What goes wrong:** User can still authenticate with old password after password reset until cache expires.
**Why it happens:** Redis cache stores user data with 15-minute TTL, not invalidated on password change.
**How to avoid:** Manually invalidate Redis cache key after password change by deleting auth:user:{user_id} key.
**Warning signs:** User can login with old password after reset.

## Code Examples

Verified patterns from official sources:

### FastAPI Startup Event
```python
# Source: https://fastapi.tiangolo.com/advanced/events/
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Code to run before application starts
    print("Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    # Code to run after application finishes
    print("Application shutting down...")
```

### Admin Role Checking Dependency
```python
# Source: Based on FastAPI dependency injection patterns
from fastapi import Depends, HTTPException, status
from typing import Annotated

async def get_current_admin(
    current_user: Annotated[dict, Depends(get_current_user)]
) -> dict:
    """Get current admin user (raises 403 if not admin)."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
```

### MongoDB Unique Index for Username
```python
# Source: https://www.mongodb.com/docs/manual/core/index-unique/
# Already implemented in database.py
await users_col.create_index([("username", 1)], unique=True)
```

### User Creation with Password Hashing
```python
# Source: Based on existing auth_service.py patterns
from app.services.auth_service import hash_password
from datetime import datetime, timezone

new_user = {
    "username": user_data.username,
    "password_hash": hash_password(user_data.password),
    "role": user_data.role,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "last_login_at": None,
}

result = await users_col.insert_one(new_user)
```

### User Listing with Response Serialization
```python
# Source: Based on existing auth.py patterns
from app.models.user import UserResponse

users = await users_col.find().to_list(length=None)

return [
    UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        role=user["role"],
        created_at=user["created_at"],
        last_login_at=user.get("last_login_at")
    )
    for user in users
]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| @app.on_event("startup") | lifespan parameter with @asynccontextmanager | FastAPI 0.95.0+ | lifespan is recommended but @app.on_event still works |
| Application-level validation only | Database-level unique index | MongoDB 2.6+ | Prevents race conditions, enforces constraint at database level |
| bcrypt for password hashing | Argon2id | 2015 (Password Hashing Competition) | Argon2 is memory-hard, more resistant to GPU/ASIC attacks |
| Manual role checking | FastAPI dependency injection | FastAPI 0.95.0+ | Cleaner code, easier testing, automatic error propagation |

**Deprecated/outdated:**
- **@app.on_event("startup"):** Still works but lifespan parameter is recommended (CONTEXT.md specifies @app.on_event)
- **bcrypt for passwords:** Argon2id is more secure against GPU attacks
- **Application-level validation only:** Database-level constraints prevent race conditions

## Assumptions Log

> List all claims tagged `[ASSUMED]` in this research. The planner and discuss-phase use this
> section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | ADMIN_PASSWORD default value should be "admin123" | the agent's Discretion | May not meet security requirements if default is too weak |
| A2 | Admin account username should be "admin" | the agent's Discretion | Frontend may need updates if different username is chosen |
| A3 | Admin account role should be "admin" | the agent's Discretion | May conflict with future role-based access control if different value is used |
| A4 | User listing should return all users without pagination | the agent's Discretion | Performance issues if user count grows large |
| A5 | Password reset should allow admin to set new password directly | the agent's Discretion | May not align with security best practices if password reset should be user-initiated |
| A6 | User deletion should succeed even if user has no posts to reassign | Locked Decision (D-11) | No risk - this is a locked decision |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed.

## Open Questions

1. **ADMIN_PASSWORD default value**
   - What we know: Admin account must be created on first startup using ADMIN_PASSWORD environment variable
   - What's unclear: What default value to use if ADMIN_PASSWORD is not set
   - Recommendation: Use "admin123" as default but require user to change on first login, or require ADMIN_PASSWORD to be set

2. **User listing pagination**
   - What we know: Admin needs to list all user accounts
   - What's unclear: Whether to implement pagination, sorting, or filtering for user listing
   - Recommendation: For MVP, return all users without pagination. Add pagination in future if user count grows large.

3. **Password reset mechanism**
   - What we know: Admin can reset user passwords via POST /api/users/{id}/reset-password
   - What's unclear: Whether admin should set new password directly or generate random password
   - Recommendation: Allow admin to set new password directly for MVP. Add random password generation in future.

4. **Post ownership reassignment**
   - What we know: User deletion should reassign posts to admin (D-10)
   - What's unclear: Current post model doesn't have owner_id field
   - Recommendation: Implement user deletion without post reassignment for now. Add post ownership and reassignment in future phase.

## Environment Availability

> Skip this section if the phase has no external dependencies (code/config-only changes).

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11+ | Backend runtime | ✓ | 3.12.3 | — |
| MongoDB | User storage | ✓ | — | — |
| FastAPI 0.115.0 | Web framework | ✓ | 0.115.0 | — |
| Pydantic 2.9.0 | Request/response validation | ✓ | 2.9.0 | — |
| Motor 3.6.0 | Async MongoDB driver | ✓ | 3.6.0 | — |
| passlib 1.7.4+ | Password hashing | ✓ | 1.7.4+ | — |
| PyJWT 2.8.0+ | JWT token validation | ✓ | 2.8.0+ | — |
| pytest 7.4.0+ | Testing framework | ✓ | 7.4.0+ | — |

**Missing dependencies with no fallback:**
- None — all dependencies are already installed

**Missing dependencies with fallback:**
- None — all dependencies are already installed

**Installation required:**
```bash
# All dependencies already installed via requirements.txt
# No additional installation needed
```

## Validation Architecture

> Skip this section entirely if workflow.nyquist_validation is explicitly set to false in .planning/config.json. If the key is absent, treat as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 7.4+ with pytest-asyncio 0.23+ |
| Config file | None — default pytest discovery |
| Quick run command | `pytest backend/tests/test_users.py -x -v` |
| Full suite command | `pytest backend/tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| USER-01 | System creates admin account on first startup | integration | `pytest backend/tests/test_users.py::test_admin_created_on_startup -x` | ❌ Wave 0 |
| USER-02 | Admin can create new user accounts with username and password | integration | `pytest backend/tests/test_users.py::test_create_user_success -x` | ❌ Wave 0 |
| USER-03 | Admin can list all user accounts | integration | `pytest backend/tests/test_users.py::test_list_users -x` | ❌ Wave 0 |
| USER-04 | Admin can delete user accounts | integration | `pytest backend/tests/test_users.py::test_delete_user_success -x` | ❌ Wave 0 |
| USER-05 | System stores user accounts in MongoDB users collection | unit | `pytest backend/tests/test_users.py::test_user_stored_in_mongodb -x` | ❌ Wave 0 |
| USER-06 | System validates username uniqueness on user creation | integration | `pytest backend/tests/test_users.py::test_create_user_duplicate_username -x` | ❌ Wave 0 |
| USER-07 | System validates password strength on user creation | unit | `pytest backend/tests/test_users.py::test_create_user_weak_password -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest backend/tests/test_users.py -x -v`
- **Per wave merge:** `pytest backend/tests/ -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `backend/tests/test_users.py` — Covers USER-01 through USER-07
- [ ] `backend/tests/conftest.py` — Add admin_user fixture for user management tests
- [ ] Framework install: Already present (pytest>=7.4.0, pytest-asyncio>=0.23.0)

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled). Omit only if explicitly `false` in config.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | JWT tokens with Argon2 password hashing (from Phase 17) |
| V3 Session Management | yes | JWT access tokens (120min) + refresh tokens (30 days) (from Phase 17) |
| V4 Access Control | yes | Role-based access control (admin-only endpoints) |
| V5 Input Validation | yes | Pydantic models for username/password validation |
| V6 Cryptography | yes | PyJWT with HS256, passlib.argon2 for password hashing (from Phase 17) |

### Known Threat Patterns for FastAPI + MongoDB + User Management

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Admin account deletion (lockout) | Denial of Service | Prevent deletion of admin account, check username == "admin" |
| Privilege escalation (role change) | Tampering | Role update endpoint requires admin authentication, validate role values |
| Username enumeration (user lookup) | Information Disclosure | Return generic "User not found" for non-existent users |
| Password reset abuse | Tampering | Password reset endpoint requires admin authentication |
| Weak admin password | Tampering | Require ADMIN_PASSWORD environment variable, use strong default |
| Exposing password_hash in responses | Information Disclosure | UserResponse model excludes password_hash field |
| Race condition in user creation | Tampering | MongoDB unique index on username prevents duplicates |
| Cache invalidation after password change | Information Disclosure | Manually invalidate Redis cache after password change |

### Security Best Practices

1. **Admin Account Management**
   - Prevent deletion of admin account to avoid lockout
   - Require ADMIN_PASSWORD environment variable for admin account creation
   - Use strong default password or require password to be set
   - Log admin account creation for audit trail

2. **Role-Based Access Control**
   - Always check user role in admin-only endpoints
   - Use get_current_admin dependency for role validation
   - Return 403 Forbidden for non-admin users
   - Prevent changing admin role to avoid lockout

3. **Password Management**
   - Use Argon2id for password hashing (already implemented)
   - Validate password strength on creation and reset
   - Never expose password_hash in API responses
   - Invalidate Redis cache after password changes

4. **Username Uniqueness**
   - Use MongoDB unique index on username field
   - Handle duplicate key errors gracefully
   - Return user-friendly error messages for duplicate usernames
   - Check for existing users before creation (defense in depth)

5. **User Deletion**
   - Prevent deletion of admin account
   - Reassign posts to admin when post ownership is implemented
   - Always succeed even if no posts to reassign
   - Log user deletions for audit trail

6. **Error Handling**
   - Return generic error messages for user not found
   - Use appropriate HTTP status codes (400, 403, 404, 500)
   - Never expose sensitive information in error messages
   - Log security-relevant events (admin actions, failures)

## Sources

### Primary (HIGH confidence)
- FastAPI Lifespan Events - https://fastapi.tiangolo.com/advanced/events/ - Startup event patterns and examples
- FastAPI Dependencies - https://fastapi.tiangolo.com/tutorial/dependencies/ - Dependency injection patterns for role checking
- MongoDB Unique Indexes - https://www.mongodb.com/docs/manual/core/index-unique/ - Unique index creation and behavior
- Existing codebase patterns - `backend/app/routers/auth.py`, `backend/app/models/user.py`, `backend/app/services/auth_service.py`, `backend/app/dependencies/auth.py`, `backend/app/database.py`, `backend/app/config.py` - Established patterns for routers, models, services, dependencies, database, and configuration
- Phase 17 Research - `.planning/phases/17-backend-authentication-foundation/17-RESEARCH.md` - Authentication infrastructure and patterns

### Secondary (MEDIUM confidence)
- FastAPI Security Tutorial - https://fastapi.tiangolo.com/tutorial/security/ - Security patterns and best practices
- MongoDB CRUD Operations - https://www.mongodb.com/docs/manual/crud/ - MongoDB create, read, update, delete operations

### Tertiary (LOW confidence)
- None — all findings verified from official documentation or existing codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified from existing codebase and requirements.txt
- Architecture: HIGH - Based on official FastAPI patterns and existing codebase structure
- Pitfalls: HIGH - Based on security best practices and common vulnerabilities documented in OWASP

**Research date:** 2026-04-18
**Valid until:** 2026-05-18 (30 days - stable FastAPI and MongoDB libraries with infrequent breaking changes)
