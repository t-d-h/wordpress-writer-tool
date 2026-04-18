# Phase 17: Backend Authentication Foundation - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish backend authentication infrastructure with user service, JWT tokens, and secure password handling. This phase delivers the core authentication system including user login, JWT token generation/validation, password hashing with Argon2, and authentication middleware for protecting API endpoints.

</domain>

<decisions>
## Implementation Decisions

### JWT Token Structure
- **D-01:** JWT token claims include user_id, username, role, exp (expiration), iat (issued at)
- **D-02:** JWT signing algorithm is HS256 (HMAC-SHA256)
- **D-03:** JWT includes issuer (iss) claim with service name
- **D-04:** JWT includes audience (aud) claim for API endpoint validation

### Password Hashing
- **D-05:** Use Argon2id variant for balanced security and performance
- **D-06:** Argon2 time_cost parameter is 3 (balanced performance)
- **D-07:** Argon2 memory_cost parameter is 128 MB (balanced memory usage)
- **D-08:** Argon2 parallelism parameter is 2 (dual thread)

### Token Expiration
- **D-09:** ACCESS_TOKEN_EXPIRE_MINUTES is set to 120 minutes
- **D-10:** Support refresh tokens for better user experience
- **D-11:** Refresh token expiration is 30 days
- **D-12:** Refresh tokens are stored in MongoDB users collection

### Error Handling
- **D-13:** Invalid login credentials return "Invalid username or password" (generic for security)
- **D-14:** Expired JWT token returns "Token expired, please login again"
- **D-15:** Invalid JWT token returns "Invalid token, please login again"
- **D-16:** Missing JWT token returns "Authentication required, please login"

### User Model
- **D-17:** User model fields: username, password_hash, role, created_at, last_login_at
- **D-18:** Role field supports three values: admin, editor, user
- **D-19:** Username validation: 3-20 characters, alphanumeric and underscore only
- **D-20:** Password strength validation: minimum 8 characters, at least 1 uppercase, 1 lowercase, 1 number

### Auth Middleware
- **D-21:** Authentication implemented as FastAPI dependency (get_current_user)
- **D-22:** All endpoints protected by default, public endpoints opt-in
- **D-23:** User context injected as full user object into protected endpoints
- **D-24:** Token validation errors raise HTTPException directly in dependency

### Redis Caching
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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Authentication Requirements
- `.planning/REQUIREMENTS.md` — AUTH-01 through AUTH-07, SEC-05 through SEC-06

### Phase Specification
- `.planning/ROADMAP.md` — Phase 17: Backend Authentication Foundation

### Codebase Patterns
- `.planning/codebase/CONVENTIONS.md` — Backend naming conventions, router patterns, model patterns
- `.planning/codebase/ARCHITECTURE.md` — Backend layer structure, service layer patterns
- `.planning/codebase/STRUCTURE.md` — Directory layout, router pattern, service pattern

### Existing Code References
- `backend/app/routers/ai_providers.py` — Example router structure with format_* helpers
- `backend/app/models/ai_provider.py` — Example Pydantic model pattern (Create/Update/Response)
- `backend/app/database.py` — MongoDB collection definitions and index creation
- `backend/app/config.py` — Environment variable configuration pattern

### External Documentation
- FastAPI Security documentation — https://fastapi.tiangolo.com/tutorial/security/
- PyJWT documentation — https://pyjwt.readthedocs.io/
- passlib documentation — https://passlib.readthedocs.io/
- Argon2 specification — https://github.com/P-H-C/phc-winner-argon2

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Router pattern**: `backend/app/routers/ai_providers.py` — Shows standard FastAPI router structure with prefix, tags, and format_* helper functions
- **Model pattern**: `backend/app/models/ai_provider.py` — Shows Pydantic Create/Update/Response model pattern
- **Database pattern**: `backend/app/database.py` — Shows MongoDB collection definitions with _col suffix and create_indexes() function
- **Config pattern**: `backend/app/config.py` — Shows Settings class for environment variable configuration

### Established Patterns
- **Router structure**: All routers use APIRouter with prefix and tags, define format_* helpers for MongoDB → Pydantic conversion
- **Error handling**: Routers raise HTTPException with status_code and detail for errors
- **Collection naming**: All collections use snake_case with _col suffix (e.g., ai_providers_col)
- **Service layer**: Business logic in services/ directory, stateless async functions with helper functions prefixed with _

### Integration Points
- **FastAPI app**: `backend/app/main.py` — New auth router should be included here
- **Database**: `backend/app/database.py` — New users collection should be added here
- **Config**: `backend/app/config.py` — New SECRET_KEY and ACCESS_TOKEN_EXPIRE_MINUTES should be added here
- **Redis**: `backend/app/redis_client.py` — Existing Redis client can be reused for caching

</code_context>

<specifics>
## Specific Ideas

- JWT tokens should include role claim for authorization checks in future phases
- Refresh tokens stored in MongoDB users collection for persistence
- Redis caching uses namespaced keys (auth:user:{user_id}, auth:token:{token_id}) to avoid conflicts
- Generic error message for invalid login credentials ("Invalid username or password") for security
- All endpoints protected by default, public endpoints like /health opt-in
- User model includes last_login_at for tracking user activity

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 17-backend-authentication-foundation*
*Context gathered: 2026-04-18*
