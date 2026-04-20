import { NavLink, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { HiOutlineCog6Tooth, HiOutlineFolderOpen, HiOutlineCpuChip, HiOutlineGlobeAlt, HiOutlineChevronDown, HiOutlineChevronRight, HiOutlineSun, HiOutlineMoon, HiOutlineSparkles, HiOutlineChatBubbleLeftRight, HiOutlineNewspaper, HiOutlineKey } from 'react-icons/hi2'
import { getProjects } from '../api/client'
import { useAuth } from '../contexts/AuthContext'
import Logout from './Logout'
import ChangePasswordModal from './ChangePasswordModal'
import Notification from './Notification'

export default function Sidebar() {
  const location = useLocation()
  const { user } = useAuth()
  const [settingsOpen, setSettingsOpen] = useState(
    location.pathname.startsWith('/settings')
  )
  const [projectsOpen, setProjectsOpen] = useState(true)
  const [projects, setProjects] = useState([])
  const [isDark, setIsDark] = useState(true)
  const [showChangePassword, setShowChangePassword] = useState(false)
  const [notification, setNotification] = useState(null)

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light')
    setIsDark(initialTheme === 'dark')
    document.documentElement.setAttribute('data-theme', initialTheme)
  }, [])

  useEffect(() => {
    const loadProjects = async () => {
      try {
        const response = await getProjects()
        setProjects(response.data)
      } catch (e) {
        console.error('Failed to load projects:', e)
      }
    }
    loadProjects()
  }, [])

  const toggleTheme = () => {
    const newTheme = isDark ? 'light' : 'dark'
    setIsDark(!isDark)
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('theme', newTheme)
  }

  const handlePasswordChangeSuccess = () => {
    setNotification({ type: 'success', message: 'Password changed successfully!' })
    setTimeout(() => setNotification(null), 3000)
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">W</div>
        <div>
          <div className="sidebar-title">WP Content writer</div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>AI-Powered</div>
        </div>
        <button
          onClick={toggleTheme}
          className="btn-icon"
          style={{
            marginLeft: 'auto',
            background: 'var(--bg-glass)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            padding: '8px',
            borderRadius: 'var(--radius-sm)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {isDark ? <HiOutlineSun size={18} /> : <HiOutlineMoon size={18} />}
        </button>
      </div>

      <nav className="sidebar-nav">


        <div className="sidebar-subtitle">Menu</div>

        <div className="nav-section">
          <NavLink to="/projects" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <HiOutlineFolderOpen className="nav-icon" />
            <span>Projects</span>
            <span
              style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center' }}
              onClick={(e) => {
                e.preventDefault();
                setProjectsOpen(!projectsOpen);
              }}
            >
              {projectsOpen ? (
                <HiOutlineChevronDown style={{ fontSize: 14 }} />
              ) : (
                <HiOutlineChevronRight style={{ fontSize: 14 }} />
              )}
            </span>
          </NavLink>
          {projectsOpen && (
            <div className="nav-children project-list-nav">
              {projects.map(project => (
                <NavLink
                  key={project.id}
                  to={`/projects/${project.id}`}
                  className={({ isActive }) => `project-nav-item ${isActive ? 'active' : ''}`}
                >
                  {project.title}
                </NavLink>
              ))}
            </div>
          )}
        </div>

        <div className="nav-section">
          <NavLink to="/news" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <HiOutlineNewspaper className="nav-icon" />
            <span>News</span>
          </NavLink>
        </div>

        <div className="nav-section">
          <div className="nav-item" onClick={() => setSettingsOpen(!settingsOpen)}>
            <HiOutlineCog6Tooth className="nav-icon" />
            <span>Settings</span>
            {settingsOpen ? <HiOutlineChevronDown style={{ marginLeft: 'auto', fontSize: 14 }} /> : <HiOutlineChevronRight style={{ marginLeft: 'auto', fontSize: 14 }} />}
          </div>
          {settingsOpen && (
            <div className="nav-children">
              <NavLink to="/settings/ai-providers" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                <HiOutlineCpuChip className="nav-icon" />
                <span>AI Providers</span>
              </NavLink>
              <NavLink to="/settings/wp-sites" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                <HiOutlineGlobeAlt className="nav-icon" />
                <span>WordPress Sites</span>
              </NavLink>
              <NavLink to="/settings/default-models" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                <HiOutlineSparkles className="nav-icon" />
                <span>Default Models</span>
              </NavLink>
            </div>
          )}
        </div>
      </nav>

      <div className="sidebar-footer" style={{ padding: '16px', borderTop: '1px solid var(--border-color)' }}>
        <div className="user-info" style={{ marginBottom: '12px' }}>
          <span className="user-name" style={{ display: 'block', fontWeight: 600, color: 'var(--text-primary)' }}>{user?.username || 'Guest'}</span>
          <span className="user-role" style={{ display: 'block', fontSize: '12px', color: 'var(--text-muted)' }}>{user?.role || ''}</span>
        </div>
        <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
          <button
            onClick={() => setShowChangePassword(true)}
            className="btn btn-secondary btn-sm"
            style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
          >
            <HiOutlineKey size={14} />
            Change Password
          </button>
          <Logout />
        </div>
        <a
          href="https://t.me/hoantdh"
          target="_blank"
          rel="noopener noreferrer"
          className="nav-item"
          style={{
            background: 'var(--bg-glass)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            color: 'var(--accent-primary)',
            fontWeight: '600'
          }}
        >
          <HiOutlineChatBubbleLeftRight className="nav-icon" />
          <span>Nhắn tin cho Chồng iu</span>
        </a>
        <div style={{ textAlign: 'center', marginTop: '12px', fontSize: '11px', color: 'var(--text-muted)', letterSpacing: '0.5px' }}>
          Version v1.0.0
        </div>
      </div>
      {notification && (
        <Notification
          type={notification.type}
          message={notification.message}
          onDismiss={() => setNotification(null)}
        />
      )}
      <ChangePasswordModal
        isOpen={showChangePassword}
        onClose={() => setShowChangePassword(false)}
        onSuccess={handlePasswordChangeSuccess}
      />
    </aside>
  )
}
