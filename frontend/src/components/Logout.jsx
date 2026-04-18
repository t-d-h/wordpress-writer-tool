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
