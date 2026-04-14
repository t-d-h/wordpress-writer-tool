import { NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { HiOutlineHome, HiOutlineCog6Tooth, HiOutlineFolderOpen, HiOutlineCpuChip, HiOutlineGlobeAlt, HiOutlineChevronDown, HiOutlineChevronRight, HiOutlineSun, HiOutlineMoon, HiOutlineSparkles, HiOutlineDocumentText } from 'react-icons/hi2'
import { getProjects } from '../api/client'

export default function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const [settingsOpen, setSettingsOpen] = useState(
    location.pathname.startsWith('/settings')
  )
  const [projectsOpen, setProjectsOpen] = useState(
    location.pathname.startsWith('/projects')
  )
  const [projects, setProjects] = useState([])
  const [isDark, setIsDark] = useState(true)

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
        <button
          className="btn btn-primary"
          style={{ width: '100%', marginBottom: '16px' }}
          onClick={() => navigate('/projects?create=true')}
        >
          <HiOutlineFolderOpen /> Create Project
        </button>

        <div className="sidebar-subtitle">Menu</div>

        <div className="nav-section">
          <NavLink to="/all-posts" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <HiOutlineDocumentText className="nav-icon" />
            <span>All Posts</span>
          </NavLink>
        </div>

        <div className="nav-section">
          <div className="nav-item" onClick={() => setProjectsOpen(!projectsOpen)}>
            <HiOutlineFolderOpen className="nav-icon" />
            <span>Projects</span>
            {projectsOpen ? <HiOutlineChevronDown style={{ marginLeft: 'auto', fontSize: 14 }} /> : <HiOutlineChevronRight style={{ marginLeft: 'auto', fontSize: 14 }} />}
          </div>
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
    </aside>
  )
}
