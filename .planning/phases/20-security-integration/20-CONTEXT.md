# Phase 20: Security Integration - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Integrate authentication middleware and token validation across all API endpoints. This phase delivers security integration by protecting all API endpoints by default, injecting user context into protected route handlers, and ensuring frontend automatically injects JWT tokens in API requests. This is critical because the service will be public to the internet.

</domain>

<decisions>
## Implementation Decisions

### Endpoint Protection Strategy
- **D-01:** All API endpoints are protected by default (user's decision)
- **D-02:** Public endpoints (like /health, /docs) must be explicitly marked as public (opt-in approach)
- **D-03:** Authentication middleware applies to all routes unless explicitly marked as public

### Public Endpoint Handling
- **D-04:** Public endpoints use FastAPI's `allow_methods=["*"]` with no authentication requirement
- **D-05:** Public endpoints use `allow_unauthenticated=True` in FastAPI Security
- **D-06:** Public endpoints are explicitly marked with `allow_unauthenticated=True` in route definition

### User Context Injection
- **D-07:** User context injected as full user object into protected route handlers via get_current_user dependency
- **D-08:** get_current_user dependency is already implemented in Phase 17 and reused across all protected endpoints
- **D-09:** User object includes user_id, username, role, created_at, last_login_at fields

### Error Handling
- **D-10:** Authentication errors raise HTTPException directly in get_current_user dependency
- **D-11:** 401 errors from invalid/expired tokens return "Token expired, please login again"
- **D-12:** 403 errors from missing/invalid tokens return "Authentication required, please login"
- **D-13:** All protected endpoints use the same error handling pattern for consistency

### Admin-Only Endpoints
- **D-14:** User management endpoints from Phase 18 are admin-only (already implemented with get_current_admin dependency)
- **D-15:** No additional admin-only endpoints needed in this phase

### the agent's Discretion
- Which specific endpoints should be marked as public (e.g., /health, /docs, /api/auth/login)
- Whether to create a custom error handler for authentication errors
- Whether to add rate limiting for authentication attempts
- Whether to log authentication failures for security monitoring

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Security Requirements
- `.planning/REQUIREMENTS.md` — SEC-01, SEC-02, SEC-07

### Phase Specifications
- `.planning/ROADMAP.md` — Phase 20: Security Integration
- `.planning/phases/17-backend-authentication-foundation/17-CONTEXT.md` — Backend authentication decisions
- `.planning/phases/19-frontend-authentication/19-CONTEXT.md` — Frontend authentication decisions

### Codebase Patterns
- `.planning/codebase/CONVENTIONS.md` — Backend naming conventions, router patterns, error handling patterns
- `.planning/codebase/ARCHITECTURE.md` — Backend layer structure, service layer patterns
- `.planning/codebase/STRUCTURE.md` — Directory layout, router pattern, service pattern

### Existing Code References
- `backend/app/dependencies/auth.py` — get_current_user dependency implementation
- `backend/app/routers/auth.py` — Example router with authentication dependency
- `backend/app/routers/ai_providers.py` — Example protected endpoint with get_current_user
- `backend/app/routers/projects.py` — Example protected endpoint with get_current_user
- `backend/app/routers/posts.py` — Example protected endpoint with get_current_user
- `frontend/src/api/client.js` — Axios interceptor for token injection (Phase 19)

### External Documentation
- FastAPI Security documentation — https://fastapi.tiangolo.com/tutorial/security/
- FastAPI OAuth2 documentation — https://fastapi.tiangolo.com/tutorial/security/oauth2/
- FastAPI Public endpoints documentation — https://fastapi.tiangolo.com/tutorial/security/enable-allow_unauthenticated/

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **get_current_user dependency**: `backend/app/dependencies/auth.py` — Already implemented in Phase 17
- **Axios interceptor**: `frontend/src/api/client.js` — Already implemented in Phase 19
- **Protected routes**: `frontend/src/components/ProtectedRoute.jsx` — Already implemented in Phase 19
- **Auth context**: `frontend/src/contexts/AuthContext.jsx` — Already implemented in Phase 19

### Established Patterns
- **Router structure**: All routers use APIRouter with prefix and tags
- **Error handling**: Routers raise HTTPException with status_code and detail for errors
- **Authentication dependency**: Protected endpoints use `current_user: Annotated[dict, Depends(get_current_user)]` pattern
- **Token validation**: get_current_user validates JWT token and raises HTTPException on failure

### Integration Points
- **FastAPI app**: `backend/app/main.py` — All routers already included
- **Database**: `backend/app/database.py` — users_col already exists
- **Config**: `backend/app/config.py` — SECRET_KEY and ACCESS_TOKEN_EXPIRE_MINUTES already configured
- **Redis**: `backend/app/redis_client.py` — Existing Redis client for caching

### Protected Endpoints Already Using get_current_user
- `backend/app/routers/auth.py` — /api/auth/me endpoint
- `backend/app/routers/ai_providers.py` — All AI provider endpoints
- `backend/app/routers/projects.py` — All project endpoints
- `backend/app/routers/posts.py` — All post endpoints
- `backend/app/routers/jobs.py` — All job endpoints
- `backend/app/routers/default_models.py` — All default model endpoints
- `backend/app/routers/link_map.py` — All link map endpoints
- `backend/app/routers/wordpress.py` — All WordPress endpoints
- `backend/app/routers/wp_sites.py` — All WordPress site endpoints

### Public Endpoints (Already Implemented)
- `backend/app/main.py` — /health endpoint (no authentication required)
- `backend/app/routers/version.py` — /version endpoint (no authentication required)

</code_context>

<specifics>
## Specific Ideas

- All API endpoints are protected by default because service will be public to internet
- Public endpoints like /health and /docs must be explicitly marked with `allow_unauthenticated=True`
- User context injected as full user object via get_current_user dependency
- Authentication errors raise HTTPException with status_code 401 or 403
- Frontend axios interceptor already injects Bearer token in Authorization header
- 401 errors from token expiration redirect to login page (already implemented in Phase 19)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 20-security-integration*
*Context gathered: 2026-04-18*
