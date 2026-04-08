import { NavLink, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { HiOutlineHome, HiOutlineCog6Tooth, HiOutlineFolderOpen, HiOutlineCpuChip, HiOutlineGlobeAlt, HiOutlineChevronDown, HiOutlineChevronRight, HiOutlineSun, HiOutlineMoon } from 'react-icons/hi2'

export default function Sidebar() {
  const location = useLocation()
  const [settingsOpen, setSettingsOpen] = useState(
    location.pathname.startsWith('/settings')
  )
  const [isDark, setIsDark] = useState(true)

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light')
    setIsDark(initialTheme === 'dark')
    document.documentElement.setAttribute('data-theme', initialTheme)
  }, [])

  const toggleTheme = () => {
    const newTheme = isDark ? 'light' : 'dark'
    setIsDark(!isDark)
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('theme', newTheme)
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">W</div>
        <div>
          <div className="sidebar-title">WP Writer</div>
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

        <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <HiOutlineHome className="nav-icon" />
          <span>Dashboard</span>
        </NavLink>

        <NavLink to="/projects" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <HiOutlineFolderOpen className="nav-icon" />
          <span>Projects</span>
        </NavLink>

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
            </div>
          )}
        </div>
      </nav>
    </aside>
  )
}
