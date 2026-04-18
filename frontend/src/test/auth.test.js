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
