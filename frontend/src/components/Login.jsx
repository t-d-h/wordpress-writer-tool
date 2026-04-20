import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { login as apiLogin } from '../api/client'
import PasswordInput from './PasswordInput'

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
    <div className="login-page page-enter">
      <div className="card">
        <div className="page-header">
          <h1 className="page-title">WordPress AI Writer</h1>
          <p className="page-description">Sign in to your account</p>
        </div>
        {error && <div className="error-banner">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="username">Username</label>
            <input
              id="username"
              className="form-input"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <PasswordInput
              id="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login
