# Technology Stack

**Project:** WordPress Writer Tool - User Management & Authentication
**Researched:** 2026-04-18
**Mode:** Ecosystem (authentication stack for FastAPI/React)

## Recommended Stack

### Core Authentication Framework
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| FastAPI Security | Built-in (0.115.0) | OAuth2 password flow, Bearer tokens | Official FastAPI utilities, integrates with OpenAPI docs, no additional dependencies needed |
| PyJWT | >=2.8.0 | JWT token encoding/decoding | Industry standard, lightweight, supports HS256 algorithm, official FastAPI recommendation |
| pwdlib | >=1.7.0 | Password hashing with Argon2 | Modern, secure, recommended by FastAPI docs, supports Argon2 (winner of Password Hashing Competition) |

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
| ADMIN_PASSWORD | Environment variable | Initial admin account | Project requirement for first account setup |
| ACCESS_TOKEN_EXPIRE_MINUTES | Environment variable | Token lifetime | Configurable session duration, default 30 minutes |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Password Hashing | pwdlib (Argon2) | passlib (bcrypt) | Passlib is older, pwdlib is modern and recommended by FastAPI docs |
| JWT Library | PyJWT | python-jose | PyJWT is simpler, official FastAPI recommendation, fewer dependencies |
| Token Storage | localStorage | sessionStorage | localStorage persists across browser sessions (better UX), sessionStorage clears on tab close |
| Auth Flow | OAuth2 Password Flow | Session-based cookies | JWT is stateless, scales better, works with existing API architecture |
| Frontend Auth | Custom hooks | Auth0/Firebase | Overkill for MVP, adds external dependencies, not needed for simple username/password |

## Installation

```bash
# Backend - Add to requirements.txt
pyjwt>=2.8.0
"pwdlib[argon2]>=1.7.0"

# Backend - Install
pip install pyjwt "pwdlib[argon2]"

# Frontend - No new dependencies needed
# Already have: axios, react-router-dom, localStorage (browser API)
```

## Integration Points

### Backend Integration
- **New Service**: `backend/app/services/auth_service.py` - Authentication logic, password hashing, JWT token generation
- **New Router**: `backend/app/routers/auth.py` - Login endpoint, user management endpoints
- **New Models**: `backend/app/models/user.py` - User Pydantic models (UserCreate, UserResponse, UserInDB)
- **New Collection**: `users` collection in MongoDB - Store user accounts with hashed passwords
- **Existing Config**: Add `SECRET_KEY`, `ADMIN_PASSWORD`, `ACCESS_TOKEN_EXPIRE_MINUTES` to `backend/app/config.py`
- **Existing Database**: Add user collection indexes in `backend/app/database.py`

### Frontend Integration
- **New Component**: `frontend/src/components/Login.jsx` - Login form
- **New Hook**: `frontend/src/hooks/useAuth.js` - Authentication state, token management
- **Existing API**: Add `login()`, `getCurrentUser()` to `frontend/src/api/client.js`
- **Existing Router**: Add protected route wrapper in `frontend/src/App.jsx`
- **Existing Storage**: Use `localStorage` for token storage (pattern already established)

### Security Best Practices
- **Password Hashing**: Use Argon2id with recommended parameters (m=65536, t=3, p=4)
- **JWT Tokens**: Use HS256 algorithm, set expiration, include `sub` claim for username
- **Token Storage**: Store in localStorage, send in `Authorization: Bearer <token>` header
- **Timing Attacks**: Always verify password against dummy hash when user not found (prevents username enumeration)
- **Secret Key**: Generate with `openssl rand -hex 32`, store in environment variable, never commit to git
- **Token Expiration**: Default 30 minutes, configurable via environment variable
- **Error Messages**: Generic "Incorrect username or password" to prevent user enumeration

## What NOT to Add

### Avoid These Libraries
- **passlib** - Older library, pwdlib is modern and recommended
- **python-jose** - More complex than needed, PyJWT is sufficient
- **Auth0/Firebase** - Overkill for MVP, adds external dependencies
- **Session management libraries** - JWT is stateless, no server-side sessions needed
- **OAuth provider SDKs** - Not needed for simple username/password authentication
- **Frontend auth libraries** (react-auth-kit, etc.) - Custom hooks are sufficient

### Avoid These Patterns
- **Session-based authentication** - JWT is better for API architecture
- **Cookie-based token storage** - localStorage is simpler for SPA
- **Complex role-based access** - MVP only needs admin/user distinction
- **Multi-factor authentication** - Not needed for MVP
- **Social login** - Not in scope for MVP
- **Password reset flows** - Can be added later, not MVP requirement

## Sources

- **HIGH Confidence**: FastAPI official documentation (https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) - Official recommendation for PyJWT and pwdlib
- **HIGH Confidence**: PyJWT documentation (https://pyjwt.readthedocs.io/en/stable/) - Industry standard JWT library
- **HIGH Confidence**: pwdlib documentation (https://passlib.readthedocs.io/en/stable/) - Modern password hashing library
- **HIGH Confidence**: MDN Web Storage API (https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage) - Browser API for token storage
- **HIGH Confidence**: Existing codebase analysis - MongoDB, Redis, FastAPI, React patterns already established
