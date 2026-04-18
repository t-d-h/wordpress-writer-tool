# Architecture Patterns

**Domain:** User Management and Authentication
**Researched:** 2026-04-18

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Login Page  │───▶│ AuthContext  │───▶│ Protected    │      │
│  │              │    │  (Provider)  │    │   Routes     │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                    │               │
│         │                   │                    │               │
│         ▼                   ▼                    ▼               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              API Client (axios interceptor)              │   │
│  │  - Adds Authorization: Bearer <token> to all requests    │   │
│  │  - Handles 401 responses (redirect to login)             │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS + JWT
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  /token      │    │  /api/users  │    │  All /api/*  │      │
│  │  (login)     │    │  (CRUD)      │    │  (protected) │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                    │               │
│         │                   │                    │               │
│         ▼                   ▼                    ▼               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Auth Middleware (Depends)                     │   │
│  │  - get_current_user() dependency                         │   │
│  │  - Validates JWT token                                    │   │
│  │  - Returns User object to route handlers                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│         │                   │                    │               │
│         ▼                   ▼                    ▼               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              User Service                                 │   │
│  │  - authenticate_user()                                    │   │
│  │  - create_user()                                          │   │
│  │  - get_user()                                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Database (MongoDB)                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  users      │    │  projects    │    │  posts       │      │
│  │  collection │    │  collection  │    │  collection  │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                    │               │
│         └───────────────────┴────────────────────┘               │
│                           │                                        │
│                           ▼                                        │
│              All data scoped by user_id                          │
└─────────────────────────────────────────────────────────────────┘
```

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| **AuthContext** (Frontend) | Manages authentication state, token storage, login/logout | All React components, API client |
| **ProtectedRoute** (Frontend) | Route wrapper that checks auth before rendering | React Router, AuthContext |
| **Login** (Frontend) | Login form, calls /token endpoint | AuthContext, API client |
| **API Client** (Frontend) | Axios instance with token interceptor | Backend API, localStorage |
| **Auth Router** (Backend) | /token endpoint, /api/users CRUD | User service, MongoDB |
| **Auth Middleware** (Backend) | JWT validation, user context injection | All routers, User service |
| **User Service** (Backend) | User CRUD, password hashing, authentication | MongoDB, pwdlib |
| **Users Collection** (Database) | Stores user credentials and metadata | User service |

### Data Flow

#### Login Flow
```
1. User enters credentials in Login component
2. Login component calls POST /token with form data
3. Backend authenticates user (User service)
4. Backend generates JWT token (signed with SECRET_KEY)
5. Backend returns { access_token, token_type: "bearer" }
6. Frontend stores token in localStorage
7. AuthContext updates state: isAuthenticated = true
8. User redirected to protected route
```

#### Authenticated Request Flow
```
1. Component makes API call (e.g., getProjects())
2. Axios interceptor adds Authorization: Bearer <token> header
3. Request sent to backend
4. FastAPI Depends(get_current_user) extracts token
5. Token validated (JWT decode, signature check)
6. User fetched from MongoDB by username
7. User object injected into route handler
8. Route handler uses user.user_id to filter data
9. Response returned to frontend
```

#### Logout Flow
```
1. User clicks logout button
2. AuthContext clears token from localStorage
3. AuthContext updates state: isAuthenticated = false
4. User redirected to /login
5. Subsequent API calls fail with 401
6. Axios interceptor redirects to login
```

## Patterns to Follow

### Pattern 1: FastAPI Dependency Injection for Auth

**What:** Use FastAPI's `Depends()` to inject authentication into route handlers

**When:** All protected routes need user context

**Example:**
```python
# backend/app/auth/dependencies.py
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from app.auth.service import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """Validate JWT token and return current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = await get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

# Usage in routers
@router.get("/projects")
async def get_projects(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get all projects for current user."""
    projects = await projects_col.find({"user_id": current_user.id}).to_list(None)
    return projects
```

### Pattern 2: React Context for Auth State

**What:** Use React Context to manage authentication state globally

**When:** Multiple components need access to auth state

**Example:**
```javascript
// frontend/src/contexts/AuthContext.jsx
import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))

  const login = async (username, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const response = await fetch('/token', {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      const data = await response.json()
      localStorage.setItem('token', data.access_token)
      setToken(data.access_token)
      setUser({ username })
      return true
    }
    return false
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
```

### Pattern 3: Axios Interceptor for Token Injection

**What:** Use axios interceptor to automatically add auth headers

**When:** All API calls need authentication

**Example:**
```javascript
// frontend/src/api/client.js
import axios from 'axios'

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: add token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

### Pattern 4: Protected Routes with React Router

**What:** Create a wrapper component to protect routes

**When:** Routes should only be accessible to authenticated users

**Example:**
```javascript
// frontend/src/components/ProtectedRoute.jsx
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

// Usage in App.jsx
<Route
  path="/projects"
  element={
    <ProtectedRoute>
      <ProjectList />
    </ProtectedRoute>
  }
/>
```

### Pattern 5: User-Scoped Data Queries

**What:** Filter all database queries by user_id

**When:** Any data retrieval or modification

**Example:**
```python
# Backend: All queries include user_id filter
@router.get("/projects")
async def get_projects(current_user: User = Depends(get_current_user)):
    projects = await projects_col.find({"user_id": current_user.id}).to_list(None)
    return projects

@router.post("/projects")
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user)
):
    project_dict = project.model_dump()
    project_dict["user_id"] = current_user.id
    result = await projects_col.insert_one(project_dict)
    return {**project_dict, "id": str(result.inserted_id)}

@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    project = await projects_col.find_one({
        "_id": ObjectId(project_id),
        "user_id": current_user.id
    })
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Storing Passwords in Plain Text

**What:** Storing user passwords without hashing

**Why bad:** If database is compromised, all user passwords are exposed

**Instead:** Use password hashing with Argon2 (via pwdlib)

```python
# BAD
user_dict["password"] = password  # Never do this!

# GOOD
from pwdlib import PasswordHash
password_hash = PasswordHash.recommended()
user_dict["hashed_password"] = password_hash.hash(password)
```

### Anti-Pattern 2: Hardcoded Secret Keys

**What:** Hardcoding JWT secret keys in source code

**Why bad:** If code is exposed, anyone can forge tokens

**Instead:** Use environment variables

```python
# BAD
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

# GOOD
from app.config import settings
SECRET_KEY = settings.SECRET_KEY  # Loaded from environment
```

### Anti-Pattern 3: Missing User Context in Routes

**What:** Routes that don't validate user context

**Why bad:** Users can access other users' data

**Instead:** Always use `Depends(get_current_user)` on protected routes

```python
# BAD
@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    return project  # Anyone can access any project!

# GOOD
@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    project = await projects_col.find_one({
        "_id": ObjectId(project_id),
        "user_id": current_user.id  # User-scoped query
    })
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
```

### Anti-Pattern 4: Token Storage in Cookies Without HttpOnly

**What:** Storing JWT tokens in cookies without HttpOnly flag

**Why bad:** Vulnerable to XSS attacks

**Instead:** Use localStorage with proper security, or HttpOnly cookies

```javascript
// BAD (if using cookies without HttpOnly)
document.cookie = `token=${token}`  # Vulnerable to XSS

// GOOD
localStorage.setItem('token', token)  # Better, but still vulnerable to XSS
// OR use HttpOnly cookies (set by backend)
```

### Anti-Pattern 5: Global Auth Middleware Without Granularity

**What:** Applying auth to all routes without exceptions

**Why bad:** Public endpoints (like /token) become inaccessible

**Instead:** Use per-route dependencies or exclude public routes

```python
# BAD
app.add_middleware(AuthMiddleware)  # Blocks /token endpoint!

# GOOD
@router.post("/token")  # Public endpoint, no auth
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    ...

@router.get("/projects")  # Protected endpoint
async def get_projects(current_user: User = Depends(get_current_user)):
    ...
```

## Scalability Considerations

| Concern | At 10 users | At 100 users | At 1,000 users |
|---------|-------------|--------------|----------------|
| **JWT Token Storage** | localStorage (client-side) | localStorage (client-side) | localStorage (client-side) - no server storage needed |
| **Password Hashing** | Argon2 (CPU-intensive) | Argon2 (consider caching) | Argon2 with optimized parameters or bcrypt |
| **User Queries** | Direct MongoDB queries | Add index on user_id | Add index on user_id, consider read replicas |
| **Token Validation** | JWT decode per request | JWT decode per request (fast) | JWT decode per request (fast) - stateless scales well |
| **Session Management** | Stateless (JWT) | Stateless (JWT) | Stateless (JWT) - no session storage needed |

**Key insight:** JWT-based authentication is stateless and scales horizontally without additional infrastructure. The main bottleneck is password hashing during login, which can be optimized with caching or parameter tuning.

## Integration Points with Existing Architecture

### Backend Integration Points

| Existing Component | Integration Required | Changes Needed |
|-------------------|---------------------|----------------|
| **All Routers** (ai_providers, wp_sites, projects, posts, jobs) | Add auth dependency | Add `current_user: User = Depends(get_current_user)` to all routes |
| **All Services** (ai_service, wp_service) | Add user context | Pass user_id to service methods for data filtering |
| **Database Queries** | Add user_id filter | All queries must include `{"user_id": current_user.id}` filter |
| **Worker Tasks** (tasks.py) | Add user context | Pass user_id with job data, validate on task execution |
| **MongoDB Collections** | Add user_id field | Add `user_id` to all existing documents (migration needed) |

### Frontend Integration Points

| Existing Component | Integration Required | Changes Needed |
|-------------------|---------------------|----------------|
| **App.jsx** | Wrap with AuthProvider | Add `<AuthProvider>` around `<Routes>` |
| **All Routes** | Add ProtectedRoute wrapper | Wrap all existing routes with `<ProtectedRoute>` |
| **API Client** (client.js) | Add token interceptor | Add request/response interceptors for JWT |
| **All Components** | Add auth checks | Redirect to login if not authenticated |
| **Sidebar** | Add logout button | Add logout button that calls `useAuth().logout()` |

### Data Migration Requirements

**Existing collections need user_id field:**
- `ai_providers` - Add `user_id` field
- `wp_sites` - Add `user_id` field
- `projects` - Add `user_id` field
- `posts` - Add `user_id` field
- `jobs` - Add `user_id` field
- `default_models` - Add `user_id` field (or make global)

**Migration strategy:**
1. Create admin user from `ADMIN_PASSWORD` env var
2. Assign all existing data to admin user
3. Add unique index on `(user_id, resource_id)` for each collection
4. Update all queries to include user_id filter

## Build Order

### Phase 1: Backend Foundation (No Breaking Changes)
1. **User Service** - Create user CRUD, password hashing, JWT generation
2. **Auth Router** - Create `/token` endpoint, `/api/users` CRUD
3. **Auth Dependencies** - Create `get_current_user()` dependency
4. **Database Migration** - Add `users` collection, add `user_id` to existing collections

### Phase 2: Backend Integration (Breaking Changes)
5. **Update All Routers** - Add `current_user` dependency to all routes
6. **Update All Services** - Pass user_id to service methods
7. **Update Worker Tasks** - Add user context to job processing
8. **Test Backend** - Verify all endpoints require auth

### Phase 3: Frontend Foundation
9. **AuthContext** - Create authentication context provider
10. **Login Component** - Create login form
11. **API Client Interceptor** - Add token injection and 401 handling
12. **ProtectedRoute Component** - Create route wrapper

### Phase 4: Frontend Integration
13. **Wrap App with AuthProvider** - Add context to App.jsx
14. **Add Login Route** - Add `/login` route to App.jsx
15. **Wrap All Routes** - Add ProtectedRoute to all existing routes
16. **Add Logout Button** - Add logout to Sidebar

### Phase 5: Testing & Validation
17. **End-to-End Testing** - Test login flow, protected routes, data isolation
18. **Security Testing** - Test token validation, user isolation, password hashing
19. **Performance Testing** - Verify JWT validation doesn't impact performance

## Sources

- FastAPI Security Tutorial: https://fastapi.tiangolo.com/tutorial/security/ (HIGH confidence - official docs)
- FastAPI Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/ (HIGH confidence - official docs)
- FastAPI OAuth2 with JWT: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ (HIGH confidence - official docs)
- pwdlib Documentation: https://pwdlib.readthedocs.io/ (HIGH confidence - official docs)
- PyJWT Documentation: https://pyjwt.readthedocs.io/ (HIGH confidence - official docs)
- React Context API: https://react.dev/learn/scaling-up-with-reducer-and-context (HIGH confidence - official docs)
- Axios Interceptors: https://axios-http.com/docs/interceptors (HIGH confidence - official docs)
- MongoDB Indexing: https://www.mongodb.com/docs/manual/indexes/ (HIGH confidence - official docs)
