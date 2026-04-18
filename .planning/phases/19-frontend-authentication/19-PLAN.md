---
wave: 1
depends_on: []
files_modified:
  - frontend/src/contexts/AuthContext.jsx
  - frontend/src/components/Login.jsx
  - frontend/src/components/Layout.jsx
  - frontend/src/App.jsx
  - frontend/src/api/client.js
  - frontend/src/utils/auth.js
  - frontend/src/components/ProtectedRoute.jsx
  - frontend/src/components/Logout.jsx
  - frontend/src/test/auth.test.js
autonomous: true
requirements_addressed:
  - AUTH-05
  - AUTH-07
  - SEC-03
  - SEC-04
---

# Plan 01: Frontend Authentication

## Objective

Provide frontend authentication UI with login component, auth context, and protected routes. Implement login form, token storage in localStorage, auth context for state management, protected route guards, logout functionality, and axios interceptor for automatic token injection.

## Success Criteria

- User can login with valid credentials via login form
- User can logout by clearing token from localStorage
- System stores JWT token in localStorage on frontend
- Frontend redirects unauthenticated users to login page
- Frontend protects all routes with authentication check

## Tasks

### Task 01-01: Create Auth Context

<read_first>
- frontend/src/App.jsx
- .planning/phases/19-frontend-authentication/19-CONTEXT.md
</read_first>

<action>
Create frontend/src/contexts/AuthContext.jsx with authentication state management:

```jsx
import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('auth_token')
    const userStr = localStorage.getItem('auth_user')
    if (token && userStr) {
      try {
        const userData = JSON.parse(userStr)
        setUser(userData)
        setIsAuthenticated(true)
      } catch (e) {
        console.error('Failed to parse user data:', e)
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
      }
    }
    setLoading(false)
  }, [])

  const login = (token, userData) => {
    localStorage.setItem('auth_token', token)
    localStorage.setItem('auth_user', JSON.stringify(userData))
    setUser(userData)
    setIsAuthenticated(true)
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
    setUser(null)
    setIsAuthenticated(false)
  }

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
```
</action>

<acceptance_criteria>
- frontend/src/contexts/AuthContext.jsx exists
- frontend/src/contexts/AuthContext.jsx contains AuthContext
- frontend/src/contexts/AuthContext.jsx contains useAuth hook
- frontend/src/contexts/AuthContext.jsx contains AuthProvider component
- frontend/src/contexts/AuthContext.jsx contains login function
- frontend/src/contexts/AuthContext.jsx contains logout function
</acceptance_criteria>

---

### Task 01-02: Create Login Component

<read_first>
- frontend/src/components/Dashboard.jsx
- .planning/phases/19-frontend-authentication/19-CONTEXT.md
</read_first>

<action>
Create frontend/src/components/Login.jsx with login form:

```jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { login as apiLogin } from '../api/client'

const Login = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await apiLogin(username, password)
      const { access_token, refresh_token, token_type } = response.data

      // Store tokens
      localStorage.setItem('auth_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      // Get user info
      const userResponse = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${access_token}`
        }
      })
      const userData = await userResponse.json()

      login(access_token, userData)
      navigate('/')
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Login failed. Please try again.'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>WordPress AI Writer</h1>
        <h2>Login</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <button type="submit" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login
```
</action>

<acceptance_criteria>
- frontend/src/components/Login.jsx exists
- frontend/src/components/Login.jsx contains handleSubmit function
- frontend/src/components/Login.jsx contains login form with username and password fields
- frontend/src/components/Login.jsx contains error display
- frontend/src/components/Login.jsx contains loading state
</acceptance_criteria>

---

### Task 01-03: Create Logout Component

<read_first>
- frontend/src/components/Layout.jsx
- .planning/phases/19-frontend-authentication/19-CONTEXT.md
</read_first>

<action>
Create frontend/src/components/Logout.jsx with logout functionality:

```jsx
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

const Logout = () => {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <button onClick={handleLogout} className="logout-button">
      Logout
    </button>
  )
}

export default Logout
```
</action>

<acceptance_criteria>
- frontend/src/components/Logout.jsx exists
- frontend/src/components/Logout.jsx contains handleLogout function
- frontend/src/components/Logout.jsx contains logout button
</acceptance_criteria>

---

### Task 01-04: Create Protected Route Component

<read_first>
- frontend/src/App.jsx
- .planning/phases/19-frontend-authentication/19-CONTEXT.md
</read_first>

<action>
Create frontend/src/components/ProtectedRoute.jsx with route guard:

```jsx
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default ProtectedRoute
```
</action>

<acceptance_criteria>
- frontend/src/components/ProtectedRoute.jsx exists
- frontend/src/components/ProtectedRoute.jsx contains ProtectedRoute component
- frontend/src/components/ProtectedRoute.jsx contains loading state check
- frontend/src/components/ProtectedRoute.jsx contains authentication check
- frontend/src/components/ProtectedRoute.jsx contains redirect to /login
</acceptance_criteria>

---

### Task 01-05: Update App.jsx with Protected Routes

<read_first>
- frontend/src/App.jsx
- .planning/phases/19-frontend-authentication/19-CONTEXT.md
</read_first>

<action>
Update frontend/src/App.jsx to include AuthProvider and protected routes:

```jsx
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Dashboard from './components/Dashboard'
import Projects from './components/Projects'
import Posts from './components/Posts'
import PostView from './components/PostView'
import Settings from './components/Settings'
import Login from './components/Login'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="projects" element={<Projects />} />
            <Route path="projects/:id" element={<PostView />} />
            <Route path="posts" element={<Posts />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
```
</action>

<acceptance_criteria>
- frontend/src/App.jsx contains AuthProvider import
- frontend/src/App.jsx contains AuthProvider wrapping Router
- frontend/src/App.jsx contains ProtectedRoute import
- frontend/src/App.jsx contains /login route
- frontend/src/App.jsx contains protected routes with ProtectedRoute wrapper
- frontend/src/App.jsx contains Navigate to /login for root path
</acceptance_criteria>

---

### Task 01-06: Update Layout with Logout Button

<read_first>
- frontend/src/components/Layout.jsx
- .planning/phases/19-frontend-authentication/19-CONTEXT.md
</read_first>

<action>
Update frontend/src/components/Layout.jsx to include logout button:

```jsx
import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import Logout from './Logout'

const Layout = () => {
  const { user } = useAuth()
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>WordPress AI Writer</h1>
        </div>
        <nav className="sidebar-nav">
          <Link to="/dashboard" className={isActive('/dashboard') ? 'active' : ''}>
            Dashboard
          </Link>
          <Link to="/projects" className={isActive('/projects') ? 'active' : ''}>
            Projects
          </Link>
          <Link to="/posts" className={isActive('/posts') ? 'active' : ''}>
            Posts
          </Link>
          <Link to="/settings" className={isActive('/settings') ? 'active' : ''}>
            Settings
          </Link>
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <span className="user-name">{user?.username || 'Guest'}</span>
            <span className="user-role">{user?.role || ''}</span>
          </div>
          <Logout />
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
```
</action>

<acceptance_criteria>
- frontend/src/components/Layout.jsx contains useAuth import
- frontend/src/components/Layout.jsx contains Logout import
- frontend/src/components/Layout.jsx contains user info display
- frontend/src/components/Layout.jsx contains Logout button in sidebar footer
</acceptance_criteria>

---

### Task 01-07: Add Axios Interceptor for Token Injection

<read_first>
- frontend/src/api/client.js
- .planning/phases/19-frontend-authentication/19-CONTEXT.md
</read_first>

<action>
Update frontend/src/api/client.js to add axios interceptor for automatic token injection:

```jsx
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to inject token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    return Promise.reject(error)
  }
)

// API functions
export const login = async (username, password) => {
  const params = new URLSearchParams()
  params.append('username', username)
  params.append('password', password)

  return apiClient.post('/api/auth/login', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

export const getDashboardStats = async () => {
  return apiClient.get('/api/dashboard/stats')
}

export const getProjects = async () => {
  return apiClient.get('/api/projects')
}

export const getProject = async (id) => {
  return apiClient.get(`/api/projects/${id}`)
}

export const createProject = async (data) => {
  return apiClient.post('/api/projects', data)
}

export const updateProject = async (id, data) => {
  return apiClient.put(`/api/projects/${id}`, data)
}

export const deleteProject = async (id) => {
  return apiClient.delete(`/api/projects/${id}`)
}

export const getPosts = async (projectId) => {
  return apiClient.get(`/api/projects/${projectId}/posts`)
}

export const getPost = async (projectId, postId) => {
  return apiClient.get(`/api/projects/${projectId}/posts/${postId}`)
}

export const createPost = async (projectId, data) => {
  return apiClient.post(`/api/projects/${projectId}/posts`, data)
}

export const updatePost = async (projectId, postId, data) => {
  return apiClient.put(`/api/projects/${projectId}/posts/${postId}`, data)
}

export const deletePost = async (projectId, postId) => {
  return apiClient.delete(`/api/projects/${projectId}/posts/${postId}`)
}

export default apiClient
```
</action>

<acceptance_criteria>
- frontend/src/api/client.js contains apiClient.interceptors.request.use
- frontend/src/apiClient.interceptors.request.use adds Authorization header with Bearer token
- frontend/src/api/client.js contains apiClient.interceptors.response.use
- frontend/src/apiClient.interceptors.response.use handles 401 errors
- frontend/src/api/client.js contains login function
- frontend/src/api/client.js contains localStorage.removeItem for auth_token and auth_user
</acceptance_criteria>

---

### Task 01-08: Create Authentication Tests

<read_first>
- frontend/src/test/auth.test.js
- .planning/phases/19-frontend-authentication/19-CONTEXT.md
</read_first>

<action>
Create frontend/src/test/auth.test.js with authentication tests:

```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { AuthProvider, useAuth } from '../contexts/AuthContext'
import Login from '../components/Login'
import Logout from '../components/Logout'
import ProtectedRoute from '../components/ProtectedRoute'

describe('AuthContext', () => {
  it('provides user and authentication state', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      </BrowserRouter>
    )
  })

  it('stores token in localStorage on login', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      </BrowserRouter>
    )
  })

  it('clears token from localStorage on logout', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      </BrowserRouter>
    )
  })
})

describe('Login Component', () => {
  it('renders login form', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    )
    expect(screen.getByText('Login')).toBeInTheDocument()
    expect(screen.getByLabelText('Username')).toBeInTheDocument()
    expect(screen.getByLabelText('Password')).toBeInTheDocument()
  })

  it('submits login form with credentials', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    )
  })

  it('displays error message on failed login', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    )
  })
})

describe('Logout Component', () => {
  it('renders logout button', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Logout />
        </AuthProvider>
      </BrowserRouter>
    )
    expect(screen.getByText('Logout')).toBeInTheDocument()
  })

  it('clears token and redirects on logout', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Logout />
        </AuthProvider>
      </BrowserRouter>
    )
  })
})

describe('ProtectedRoute Component', () => {
  it('redirects to login when not authenticated', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <ProtectedRoute>
            <div>Protected Content</div>
          </ProtectedRoute>
        </AuthProvider>
      </BrowserRouter>
    )
  })

  it('renders protected content when authenticated', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <ProtectedRoute>
            <div>Protected Content</div>
          </ProtectedRoute>
        </AuthProvider>
      </BrowserRouter>
    )
  })

  it('shows loading state while checking authentication', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <ProtectedRoute>
            <div>Protected Content</div>
          </ProtectedRoute>
        </AuthProvider>
      </BrowserRouter>
    )
  })
})

function TestComponent() {
  const { user, isAuthenticated, login, logout } = useAuth()
  return (
    <div>
      <div data-testid="user">{JSON.stringify(user)}</div>
      <div data-testid="isAuthenticated">{isAuthenticated.toString()}</div>
      <button onClick={() => login('test-token', { username: 'test', role: 'user' })}>
        Login
      </button>
      <button onClick={logout}>Logout</button>
    </div>
  )
}
```
</action>

<acceptance_criteria>
- frontend/src/test/auth.test.js exists
- frontend/src/test/auth.test.js contains AuthContext tests
- frontend/src/test/auth.test.js contains Login component tests
- frontend/src/test/auth.test.js contains Logout component tests
- frontend/src/test/auth.test.js contains ProtectedRoute tests
</acceptance_criteria>

---

## Verification

### Automated Tests

Run authentication tests:
```bash
cd frontend && npm test
```

Expected: All tests pass

### Manual Verification

1. **Login functionality**:
   - Navigate to /login
   - Enter valid username and password
   - Click Login button
   - Expected: Redirects to /dashboard, token stored in localStorage

2. **Logout functionality**:
   - Click Logout button in sidebar
   - Expected: Token cleared from localStorage, redirects to /login

3. **Protected routes**:
   - Try to access /dashboard without logging in
   - Expected: Redirects to /login
   - Login and try again
   - Expected: Access granted

4. **Token storage**:
   - Login successfully
   - Check localStorage for auth_token and auth_user
   - Expected: Both keys present with valid data

5. **Token injection**:
   - Login successfully
   - Make API request
   - Check network tab for Authorization header
   - Expected: Bearer token present in header

### Integration Checks

- [ ] User can login with valid credentials via login form
- [ ] User can logout by clearing token from localStorage
- [ ] System stores JWT token in localStorage on frontend
- [ ] Frontend redirects unauthenticated users to login page
- [ ] Frontend protects all routes with authentication check
- [ ] Axios interceptor automatically injects JWT token in API requests
- [ ] 401 errors redirect to login page

---

## Threat Model

### Security Considerations

| Threat | Mitigation | Status |
|--------|------------|--------|
| XSS token theft | Store token in localStorage (vulnerable to XSS) | ⚠️ Acceptable for MVP, httpOnly cookies in future |
| CSRF attacks | Not applicable with JWT in Authorization header | ✓ Not vulnerable |
| Token leakage in logs | Never log full tokens in tests | ✓ Implemented in tests |
| Session hijacking | Short access token expiration (120 minutes) | ✓ Implemented in Phase 17 |
| Unauthorized access | Protected routes check authentication | ✓ Implemented in ProtectedRoute |
| Token expiration | 401 errors redirect to login | ✓ Implemented in interceptor |

### ASVS Compliance

| ASVS Category | Control | Status |
|---------------|---------|--------|
| V2 Authentication | JWT tokens with Argon2 password hashing (Phase 17) | ✓ |
| V3 Session Management | JWT access tokens (120min) + refresh tokens (30 days) | ✓ |
| V4 Access Control | Protected routes with authentication check | ✓ |
| V5 Input Validation | Login form validation | ✓ |
| V6 Cryptography | PyJWT with HS256 (Phase 17) | ✓ |

---

## Notes

- Token storage in localStorage is acceptable for MVP (httpOnly cookies in future)
- Login form uses username/password fields with validation
- Auth context provides user object, login/logout functions, loading state
- Protected routes redirect to /login if not authenticated
- Logout clears tokens and redirects to /login
- Axios interceptor adds Authorization header with Bearer token
- 401 errors redirect to login page
- User info displayed in sidebar footer (username and role)
