# Phase 18: Backend User Management - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Enable admin to manage user accounts with CRUD operations and validation. This phase delivers user management endpoints including admin account creation on startup, user creation, listing, deletion, password reset, and role update functionality. All operations are admin-only and leverage the authentication infrastructure established in Phase 17.

</domain>

<decisions>
## Implementation Decisions

### Admin Account Creation
- **D-01:** Admin account created on first startup using FastAPI startup event
- **D-02:** Startup event checks if admin exists, creates if missing (safe idempotent approach)
- **D-03:** Admin account uses ADMIN_PASSWORD environment variable for password
- **D-04:** Admin account has role="admin" and username="admin"

### User Management Endpoints
- **D-05:** User creation endpoint path: POST /api/users
- **D-06:** User listing endpoint path: GET /api/users
- **D-07:** User deletion endpoint path: DELETE /api/users/{id}
- **D-08:** Password reset endpoint path: POST /api/users/{id}/reset-password
- **D-09:** Role update endpoint path: PUT /api/users/{id}/role

### User Deletion Behavior
- **D-10:** User deletion reassigns all posts owned by deleted user to admin
- **D-11:** User deletion always succeeds even if user has no posts to reassign
- **D-12:** User deletion is permanent (no soft delete)

### Password Reset Functionality
- **D-13:** Password reset is admin-only functionality
- **D-14:** Password reset is a separate endpoint: POST /api/users/{id}/reset-password
- **D-15:** Password reset requires admin authentication via get_current_user dependency

### Role Update Functionality
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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Authentication Requirements
- `.planning/REQUIREMENTS.md` — USER-01 through USER-07
- `.planning/phases/17-backend-authentication-foundation/17-CONTEXT.md` — Authentication infrastructure decisions
- `.planning/phases/17-backend-authentication-foundation/17-RESEARCH.md` — Authentication research and patterns

### Phase Specification
- `.planning/ROADMAP.md` — Phase 18: Backend User Management

### Codebase Patterns
- `.planning/codebase/CONVENTIONS.md` — Backend naming conventions, router patterns, model patterns
- `.planning/codebase/ARCHITECTURE.md` — Backend layer structure, service layer patterns
- `.planning/codebase/STRUCTURE.md` — Directory layout, router pattern, service pattern

### Existing Code References
- `backend/app/routers/auth.py` — Example router structure with authentication dependencies
- `backend/app/models/user.py` — User Pydantic models (UserCreate, UserUpdate, UserResponse)
- `backend/app/services/auth_service.py` — Authentication service (hash_password, verify_password, get_user, get_user_by_id)
- `backend/app/dependencies/auth.py` — get_current_user dependency for admin-only endpoints
- `backend/app/database.py` — MongoDB collections and index creation pattern
- `backend/app/main.py` — FastAPI application entry point with startup event pattern

### External Documentation
- FastAPI Startup Events — https://fastapi.tiangolo.com/advanced/events/
- FastAPI Dependency Injection — https://fastapi.tiangolo.com/tutorial/dependencies/
- MongoDB Unique Indexes — https://www.mongodb.com/docs/indexes/

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Authentication infrastructure**: Phase 17 established JWT tokens, Argon2 password hashing, and authentication middleware
- **User models**: UserCreate, UserUpdate, UserResponse models already exist with validation
- **Authentication service**: hash_password, verify_password, get_user, get_user_by_id functions available
- **Authentication dependencies**: get_current_user dependency for protecting admin-only endpoints
- **Database pattern**: users_col already created with unique username index
- **Router pattern**: backend/app/routers/auth.py shows how to structure user management router

### Established Patterns
- **Router structure**: All routers use APIRouter with prefix and tags, define format_* helpers for MongoDB → Pydantic conversion
- **Error handling**: Routers raise HTTPException with status_code and detail for errors
- **Collection naming**: All collections use snake_case with _col suffix (e.g., users_col)
- **Service layer**: Business logic in services/ directory, stateless async functions with helper functions prefixed with _
- **Authentication**: All protected endpoints use get_current_user dependency for admin-only access

### Integration Points
- **FastAPI app**: `backend/app/main.py` — New startup event should be added here
- **Database**: `backend/app/database.py` — users_col already exists, no new collections needed
- **Config**: `backend/app/config.py` — ADMIN_PASSWORD should be added here
- **Auth router**: `backend/app/routers/auth.py` — User management router should be included in main.py

</code_context>

<specifics>
## Specific Ideas

- Admin account creation uses FastAPI startup event with @app.on_event("startup")
- Startup event checks if admin exists before creating to avoid duplicates
- All user management endpoints require admin authentication via get_current_user dependency
- User deletion reassigns posts to admin to prevent orphaned content
- Password reset and role update are separate endpoints for clarity and security
- Role field is stored in user documents but not yet used for access control (future feature)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 18-backend-user-management*
*Context gathered: 2026-04-18*
