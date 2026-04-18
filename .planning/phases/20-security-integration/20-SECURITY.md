---
phase: 20
slug: security-integration
status: verified
threats_open: 0
asvs_level: 1
created: 2026-04-18
---

# Phase 20 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Frontend ↔ Backend API | JWT-based authentication for all protected endpoints | JWT access tokens, user context |
| Backend ↔ MongoDB | User data storage and retrieval | User credentials (hashed), user profiles |
| Backend ↔ Redis | User session caching | User session data, cached user objects |
| Public Endpoints | Unauthenticated access to health and root endpoints | Service status information |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-20-01 | Spoofing | Authentication System | Mitigate | JWT tokens with Argon2 password hashing (Phase 17) | closed |
| T-20-02 | Tampering | API Endpoints | Mitigate | All endpoints protected by default with get_current_user dependency | closed |
| T-20-03 | Repudiation | User Actions | Mitigate | User context injected into all protected route handlers | closed |
| T-20-04 | Information Disclosure | Logs | Mitigate | Never log full tokens in tests | closed |
| T-20-05 | Denial of Service | Session Management | Mitigate | Short access token expiration (120 minutes) | closed |
| T-20-06 | Elevation of Privilege | Authorization | Mitigate | Role-based access control with get_current_admin dependency | closed |
| T-20-07 | Cross-Site Request Forgery | Frontend | N/A | Not applicable with JWT in Authorization header | closed |
| T-20-08 | Cross-Site Scripting | Token Storage | Accept | Token stored in localStorage (vulnerable to XSS) - acceptable for MVP, httpOnly cookies in future | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-20-01 | T-20-08 | XSS token theft risk accepted for MVP. Token stored in localStorage is vulnerable to XSS attacks. Mitigation (httpOnly cookies) deferred to future milestone. Risk is acceptable for MVP stage as application is not yet public-facing. | GSD Workflow | 2026-04-18 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-04-18 | 8 | 8 | 0 | GSD Secure Phase Workflow |

---

## ASVS Compliance

| ASVS Category | Control | Status |
|---------------|---------|--------|
| V2 Authentication | JWT tokens with Argon2 password hashing (Phase 17) | ✓ |
| V3 Session Management | JWT access tokens (120min) + refresh tokens (30 days) | ✓ |
| V4 Access Control | Protected routes with authentication check | ✓ |
| V5 Input Validation | Login form validation (Phase 19) | ✓ |
| V6 Cryptography | PyJWT with HS256, passlib.argon2 for password hashing (Phase 17) | ✓ |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-04-18

---

## Implementation Evidence

### Files Modified

**Backend Files:**
- `backend/app/main.py` - Verified public endpoints
- `backend/app/dependencies/auth.py` - Verified user context injection
- `backend/app/services/auth_service.py` - Verified user retrieval
- `backend/app/routers/wp_sites.py` - Added authentication to 11 endpoints
- `backend/app/routers/posts.py` - Added authentication to 13 endpoints
- `backend/app/routers/jobs.py` - Added authentication to 3 endpoints
- `backend/app/routers/default_models.py` - Added authentication to 2 endpoints
- `backend/app/routers/link_map.py` - Added authentication to 2 endpoints
- `backend/app/routers/wordpress.py` - Added authentication to 3 endpoints
- `backend/app/routers/version.py` - Added authentication to 1 endpoint
- `backend/app/routers/projects.py` - Added missing imports
- `backend/tests/test_security_integration.py` - Created security integration tests
- `backend/tests/conftest.py` - Verified users_col in cleanup

**Frontend Files:**
- `frontend/src/api/client.js` - Verified token injection and 401 handling

### Tests Created

- `test_protected_endpoint_requires_token` - Verifies protected endpoints require valid token
- `test_protected_endpoint_injects_user_context` - Verifies user context injection
- `test_invalid_token_returns_401` - Verifies invalid token handling
- `test_expired_token_returns_401` - Verifies expired token handling
- `test_public_endpoint_no_auth_required` - Verifies public endpoints work without auth
- `test_user_context_includes_required_fields` - Verifies user context structure
- `test_token_injection_in_all_api_calls` - Verifies token injection in all API calls
- `test_401_clears_tokens_and_redirects_to_login` - Frontend behavior test

### Security Controls Implemented

1. **Authentication:** JWT-based authentication with Argon2 password hashing
2. **Authorization:** Role-based access control (admin, editor, user)
3. **Session Management:** Short access token expiration (120 minutes) with refresh tokens (30 days)
4. **Input Validation:** Login form validation with password strength requirements
5. **Error Handling:** Consistent 401/403 error responses
6. **Token Management:** Automatic token injection via axios interceptor
7. **Session Cleanup:** Token clearing and redirect on 401 errors
