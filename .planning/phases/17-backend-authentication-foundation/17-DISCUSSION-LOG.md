# Phase 17: Backend Authentication Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-18
**Phase:** 17-Backend Authentication Foundation
**Areas discussed:** JWT token structure, Password hashing, Token expiration, Error handling, User model, Auth middleware, Redis caching

---

## JWT Token Structure

| Option | Description | Selected |
|--------|-------------|----------|
| user_id, username, exp, iat | Standard approach - includes user_id, username, expiration, issued_at. Simple and sufficient for MVP. | |
| user_id, username, role, exp, iat | More verbose - adds role (admin/user) for authorization checks. Useful if roles are needed soon. | ✓ |
| user_id, exp only | Minimal - only user_id and expiration. Reduces token size, requires database lookup for user details. | |

**User's choice:** user_id, username, role, exp, iat
**Notes:** User selected the option that includes role claim for authorization checks.

| Option | Description | Selected |
|--------|-------------|----------|
| HS256 (HMAC-SHA256) | Industry standard for JWT signing. Recommended by PyJWT documentation. | ✓ |
| RS256 (RSA-SHA256) | More secure but requires asymmetric key management. Overkill for MVP. | |

**User's choice:** HS256 (HMAC-SHA256)
**Notes:** User selected the industry standard signing algorithm.

| Option | Description | Selected |
|--------|-------------|----------|
| No issuer claim | No issuer claim. Simpler, but less secure. | |
| Include issuer claim | Add 'iss' claim with service name. Better security practice. | ✓ |

**User's choice:** Include issuer claim
**Notes:** User wants to include issuer claim for better security.

| Option | Description | Selected |
|--------|-------------|----------|
| No audience claim | No audience claim. Simpler. | |
| Include audience claim | Add 'aud' claim for API endpoint validation. More secure. | ✓ |

**User's choice:** Include audience claim
**Notes:** User wants to include audience claim for API endpoint validation.

---

## Password Hashing

| Option | Description | Selected |
|--------|-------------|----------|
| Argon2id | Balanced security and performance. Recommended for most applications. | ✓ |
| Argon2i | Maximum security against GPU attacks. Slower. | |
| Argon2d | Faster but less secure against side-channel attacks. | |

**User's choice:** Argon2id
**Notes:** User selected the recommended Argon2 variant.

| Option | Description | Selected |
|--------|-------------|----------|
| 2 (fast) | Fast hashing. Good for development, less secure for production. | |
| 3 (balanced) | Balanced performance and security. Recommended default. | ✓ |
| 4 (secure) | Slower hashing. More secure but may impact user experience. | |

**User's choice:** 3 (balanced)
**Notes:** User selected balanced time_cost parameter.

| Option | Description | Selected |
|--------|-------------|----------|
| 64 MB (low) | Low memory usage. Good for resource-constrained environments. | |
| 128 MB (balanced) | Balanced memory usage. Recommended default. | ✓ |
| 256 MB (secure) | High memory usage. More secure against GPU attacks. | |

**User's choice:** 128 MB (balanced)
**Notes:** User selected balanced memory_cost parameter.

| Option | Description | Selected |
|--------|-------------|----------|
| 1 (single thread) | Single thread. Simpler, slower. | |
| 2 (dual thread) | Dual thread. Balanced performance. | ✓ |
| 4 (quad thread) | Quad thread. Faster but uses more CPU. | |

**User's choice:** 2 (dual thread)
**Notes:** User selected dual thread parallelism.

---

## Token Expiration

| Option | Description | Selected |
|--------|-------------|----------|
| 30 minutes | Short-lived tokens. More secure, users re-login frequently. | |
| 60 minutes | Balanced security and user experience. Recommended default. | |
| 120 minutes | Long-lived tokens. Less secure, better user experience. | ✓ |

**User's choice:** 120 minutes
**Notes:** User selected longer-lived tokens for better user experience.

| Option | Description | Selected |
|--------|-------------|----------|
| No refresh tokens | Simpler implementation. Users re-login after token expires. | |
| Yes, refresh tokens | Better UX. Users stay logged in longer with refresh token rotation. | ✓ |

**User's choice:** Yes, refresh tokens
**Notes:** User wants refresh tokens for better user experience.

| Option | Description | Selected |
|--------|-------------|----------|
| 7 days | Short-lived refresh tokens. More secure. | |
| 14 days | Balanced security and user experience. Recommended default. | |
| 30 days | Long-lived refresh tokens. Less secure, better UX. | ✓ |

**User's choice:** 30 days
**Notes:** User selected long-lived refresh tokens for better UX.

| Option | Description | Selected |
|--------|-------------|----------|
| MongoDB | Store in MongoDB users collection. Simple, persistent. | ✓ |
| Redis | Store in Redis. Faster, can revoke easily. | |

**User's choice:** MongoDB
**Notes:** User selected MongoDB for refresh token storage.

---

## Error Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Invalid username or password | Generic message. More secure, less user-friendly. | ✓ |
| Username not found / Incorrect password | Specific message. More user-friendly, less secure. | |

**User's choice:** Invalid username or password
**Notes:** User selected generic message for security.

| Option | Description | Selected |
|--------|-------------|----------|
| Token expired | Generic message. Simpler. | |
| Token expired, please login again | Specific message with guidance. Better UX. | ✓ |

**User's choice:** Token expired, please login again
**Notes:** User selected specific message with guidance.

| Option | Description | Selected |
|--------|-------------|----------|
| Invalid token | Generic message. Simpler. | |
| Invalid token, please login again | Specific message with guidance. Better UX. | ✓ |

**User's choice:** Invalid token, please login again
**Notes:** User selected specific message with guidance.

| Option | Description | Selected |
|--------|-------------|----------|
| Authentication required | Generic message. Simpler. | |
| Authentication required, please login | Specific message with guidance. Better UX. | ✓ |

**User's choice:** Authentication required, please login
**Notes:** User selected specific message with guidance.

---

## User Model

| Option | Description | Selected |
|--------|-------------|----------|
| username, password_hash, created_at | Minimal fields. Simple, sufficient for MVP. | |
| username, password_hash, role, created_at | Standard fields. Includes role for authorization. | |
| username, password_hash, role, created_at, last_login_at | Comprehensive fields. Includes role and last login tracking. | ✓ |

**User's choice:** username, password_hash, role, created_at, last_login_at
**Notes:** User selected comprehensive fields including last_login_at.

| Option | Description | Selected |
|--------|-------------|----------|
| admin, user | Simple roles. Sufficient for MVP. | |
| admin, editor, user | More granular roles. Future-proof. | ✓ |

**User's choice:** admin, editor, user
**Notes:** User selected three role values for future flexibility.

| Option | Description | Selected |
|--------|-------------|----------|
| 3-20 chars, alphanumeric + underscore | Simple validation. 3-20 chars, alphanumeric and underscores only. | ✓ |
| 3-30 chars, alphanumeric + underscore + hyphen | Standard validation. 3-30 chars, alphanumeric, underscores, and hyphens. | |
| 3-50 chars, flexible | Flexible validation. 3-50 chars, most characters allowed. | |

**User's choice:** 3-20 chars, alphanumeric + underscore
**Notes:** User selected simple username validation.

| Option | Description | Selected |
|--------|-------------|----------|
| 8 chars minimum | Simple validation. 8 chars minimum. | |
| 8 chars, 1 uppercase, 1 lowercase, 1 number | Standard validation. 8 chars, 1 uppercase, 1 lowercase, 1 number. | ✓ |
| 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special | Strong validation. 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char. | |

**User's choice:** 8 chars, 1 uppercase, 1 lowercase, 1 number
**Notes:** User selected standard password validation.

---

## Auth Middleware

| Option | Description | Selected |
|--------|-------------|----------|
| FastAPI dependency (get_current_user) | FastAPI dependency injection. Standard pattern, reusable across endpoints. | ✓ |
| Custom middleware | Custom middleware. Runs on all requests, simpler for global protection. | |
| Decorator pattern | Decorator pattern. Explicit opt-in, more control. | |

**User's choice:** FastAPI dependency (get_current_user)
**Notes:** User selected FastAPI dependency injection pattern.

| Option | Description | Selected |
|--------|-------------|----------|
| Protect by default, opt-in public | All endpoints protected by default, opt-in for public endpoints. | ✓ |
| Public by default, opt-in protected | All endpoints public by default, opt-in for protected endpoints. | |

**User's choice:** Protect by default, opt-in public
**Notes:** User selected more secure approach with protection by default.

| Option | Description | Selected |
|--------|-------------|----------|
| Inject user_id only | Inject user_id only. Simple, endpoints fetch user details if needed. | |
| Inject full user object | Inject full user object. More convenient, but may be stale. | ✓ |
| Inject user_id and role | Inject user_id and role. Balanced approach for authorization. | |

**User's choice:** Inject full user object
**Notes:** User selected to inject full user object for convenience.

| Option | Description | Selected |
|--------|-------------|----------|
| HTTPException in dependency | Raise HTTPException directly. Simple, consistent with existing codebase. | ✓ |
| Custom exception handler | Custom exception handler. More flexible, centralized error handling. | |

**User's choice:** HTTPException in dependency
**Notes:** User selected approach consistent with existing codebase.

---

## Redis Caching

| Option | Description | Selected |
|--------|-------------|----------|
| Cache user objects | Cache user objects by user_id. Reduces database lookups for token validation. | |
| Cache JWT tokens | Cache JWT tokens. Faster validation, but requires cache invalidation on logout. | |
| Cache both | Cache both user objects and tokens. Maximum performance, more complex. | ✓ |
| No caching | No caching. Simpler, sufficient for MVP. | |

**User's choice:** Cache both
**Notes:** User wants to cache both user objects and JWT tokens for maximum performance.

| Option | Description | Selected |
|--------|-------------|----------|
| 5 minutes | Short cache. More frequent refreshes, less stale data. | |
| 15 minutes | Balanced cache. Recommended default. | ✓ |
| 30 minutes | Long cache. Less frequent refreshes, more stale data. | |

**User's choice:** 15 minutes
**Notes:** User selected balanced cache TTL.

| Option | Description | Selected |
|--------|-------------|----------|
| TTL only | Simple TTL-based. Cache expires automatically. | ✓ |
| TTL + manual invalidation | TTL + manual invalidation on logout/password change. More complex but more accurate. | |
| TTL + manual invalidation + refresh | TTL + manual invalidation + cache refresh on user update. Most accurate. | |

**User's choice:** TTL only
**Notes:** User selected simpler TTL-based cache invalidation.

| Option | Description | Selected |
|--------|-------------|----------|
| user:{user_id}, token:{token_id} | Simple keys. user:{user_id}, token:{token_id}. | |
| auth:user:{user_id}, auth:token:{token_id} | Namespaced keys. auth:user:{user_id}, auth:token:{token_id}. | ✓ |
| wordpress_writer:auth:user:{user_id}, wordpress_writer:auth:token:{token_id} | Hierarchical keys. wordpress_writer:auth:user:{user_id}, wordpress_writer:auth:token:{token_id}. | |

**User's choice:** auth:user:{user_id}, auth:token:{token_id}
**Notes:** User selected namespaced keys to avoid conflicts.

---

## the agent's Discretion

Areas where user deferred to the agent:
- JWT issuer claim value (service name)
- JWT audience claim value (API identifier)
- Index creation strategy for users collection
- Admin account creation mechanism
- Login endpoint path
- Refresh endpoint path

## Deferred Ideas

None — discussion stayed within phase scope
