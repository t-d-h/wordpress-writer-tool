# Phase 19: Frontend Authentication - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Provide frontend authentication UI with login component, auth context, and protected routes. This phase delivers the frontend authentication layer including login form, token storage in localStorage, auth context for state management, protected route guards, and logout functionality.

</domain>

<decisions>
## Implementation Decisions

### Carrying Forward from Phase 17 (Backend Authentication Foundation)
- **D-01:** JWT token claims include user_id, username, role, exp, iat, iss, aud
- **D-02:** JWT signing algorithm is HS256 (HMAC-SHA256)
- **D-03:** JWT includes issuer (iss) claim with service name
- **D-04:** JWT includes audience (aud) claim for API endpoint validation
- **D-05:** ACCESS_TOKEN_EXPIRE_MINUTES is set to 120 minutes
- **D-06:** Support refresh tokens with 30-day expiration
- **D-07:** Login endpoint path: /api/auth/login
- **D-08:** Refresh endpoint path: /api/auth/refresh
- **D-09:** Error messages: "Invalid username or password", "Token expired, please login again", "Invalid token, please login again", "Authentication required, please login"

### Carrying Forward from Phase 18 (Backend User Management)
- **D-10:** Admin account created on first startup using ADMIN_PASSWORD environment variable
- **D-11:** User management endpoints: POST /api/users, GET /api/users, DELETE /api/users/{id}
- **D-12:** Password reset endpoint: POST /api/users/{id}/reset-password (admin-only)
- **D-13:** Role update endpoint: PUT /api/users/{id}/role (admin-only)

### the agent's Discretion
- Login component design (form layout, validation feedback, error display)
- Auth context structure (state management, token storage, user state)
- Protected routes implementation (route guards, redirect logic, loading states)
- Logout behavior (clear token, redirect, confirmation)
- Token storage strategy (localStorage vs sessionStorage, key naming)
- Authentication state persistence (page refresh handling, token refresh)
- Error handling (401/403 responses, token expiration, network errors)
- Loading states (login button, protected routes, token refresh)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Authentication Requirements
- `.planning/REQUIREMENTS.md` — AUTH-05, AUTH-07, SEC-03, SEC-04

### Phase Specifications
- `.planning/ROADMAP.md` — Phase 19: Frontend Authentication
- `.planning/phases/17-backend-authentication-foundation/17-CONTEXT.md` — Backend authentication decisions
- `.planning/phases/18-backend-user-management/18-CONTEXT.md` — User management decisions

### Codebase Patterns
- `.planning/codebase/CONVENTIONS.md` — Frontend naming conventions, component patterns
- `.planning/codebase/ARCHITECTURE.md` — Frontend layer structure, routing patterns
- `.planning/codebase/STRUCTURE.md` — Directory layout, component pattern

### Existing Code References
- `frontend/src/App.jsx` — Root component with routing
- `frontend/src/components/Layout.jsx` — Layout component with sidebar
- `frontend/src/components/Dashboard.jsx` — Dashboard component example
- `frontend/src/api/client.js` — Axios API client

### External Documentation
- React Router documentation — https://reactrouter.com/
- React Context documentation — https://react.dev/reference/react
- Axios interceptor documentation — https://axios-http.com/docs/interceptors

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **React Router**: Already configured in App.jsx for client-side routing
- **Axios client**: frontend/src/api/client.js — Existing API client for backend communication
- **Layout component**: frontend/src/components/Layout.jsx — Existing layout with sidebar
- **Dashboard component**: frontend/src/components/Dashboard.jsx — Example component structure

### Established Patterns
- **Component structure**: All components use PascalCase.jsx naming, export default function
- **State management**: Components use useState hooks for local state
- **API calls**: All API calls use axios from frontend/src/api/client.js
- **Error handling**: All API calls wrapped in try/catch with alert() for errors

### Integration Points
- **React Router**: frontend/src/App.jsx — New protected routes should be added here
- **API client**: frontend/src/api/client.js — Axios interceptor should be added here
- **Layout**: frontend/src/components/Layout.jsx — Login/logout buttons should be added here

</code_context>

<specifics>
## Specific Ideas

- JWT token stored in localStorage with key "auth_token"
- Refresh token stored in localStorage with key "refresh_token"
- Auth context provides user object, login/logout functions, loading state
- Protected routes redirect to /login if not authenticated
- Login form uses username/password fields with validation
- Logout clears tokens and redirects to /login
- Axios interceptor adds Authorization header with Bearer token

</specifics>

<deferred>
## Deferred Ideas

None — discussion skipped, using agent discretion for all gray areas

</deferred>

---

*Phase: 19-frontend-authentication*
*Context gathered: 2026-04-18*
