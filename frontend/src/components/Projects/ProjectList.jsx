import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { HiOutlinePlus, HiOutlineXMark, HiOutlineTrash, HiOutlineGlobeAlt, HiOutlinePencil } from 'react-icons/hi2'
import { getProjects, createProject, deleteProject, updateProject, getSites } from '../../api/client'

export default function ProjectList() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [sites, setSites] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [showEditModal, setShowEditModal] = useState(false)
  const [form, setForm] = useState({ title: '', description: '', wp_site_id: '' })
  const [editForm, setEditForm] = useState({ id: '', title: '', description: '', wp_site_id: '' })

  useEffect(() => { load() }, [])

  const load = async () => {
    try {
      const [projRes, siteRes] = await Promise.all([getProjects(), getSites()])
      setProjects(projRes.data)
      setSites(siteRes.data)
      if (siteRes.data.length > 0 && !form.wp_site_id) {
        setForm(f => ({ ...f, wp_site_id: siteRes.data[0].id }))
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const { data } = await createProject(form)
      setShowModal(false)
      setForm({ title: '', description: '', wp_site_id: sites[0]?.id || '' })
      navigate(`/projects/${data.id}`)
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  const openEdit = (e, project) => {
    e.stopPropagation()
    setEditForm({
      id: project.id,
      title: project.title,
      description: project.description || '',
      wp_site_id: project.wp_site_id
    })
    setShowEditModal(true)
  }

  const handleUpdate = async (e) => {
    e.preventDefault()
    try {
      await updateProject(editForm.id, {
        title: editForm.title,
        description: editForm.description
      })
      setShowEditModal(false)
      load() // Reload list without navigating away
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  const handleDelete = async (e, id) => {
    e.stopPropagation()
    const project = projects.find(p => p.id === id)
    setDeleteConfirm(project)
    setShowDeleteModal(true)
  }

  const confirmDelete = async () => {
    if (!deleteConfirm) return
    try {
      await deleteProject(deleteConfirm.id)
      setShowDeleteModal(false)
      setDeleteConfirm(null)
      load()
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  return (
    <div className="page-enter">
      <div className="page-header">
        <h1 className="page-title">Projects</h1>
        <p className="page-description">Manage your content projects</p>
      </div>

      <div className="toolbar">
        <div />
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          <HiOutlinePlus /> New Project
        </button>
      </div>

      {loading ? (
        <div className="loading-page"><div className="loading-spinner" /></div>
      ) : projects.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📁</div>
          <div className="empty-state-title">No Projects Yet</div>
          <div className="empty-state-text">Create your first project to start generating content</div>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            <HiOutlinePlus /> New Project
          </button>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map(p => (
            <div key={p.id} className="project-card" onClick={() => navigate(`/projects/${p.id}`)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div className="project-card-title">{p.title}</div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button className="action-btn" onClick={e => openEdit(e, p)} title="Edit"><HiOutlinePencil /></button>
                  <button className="action-btn danger" onClick={e => handleDelete(e, p.id)} title="Delete"><HiOutlineTrash /></button>
                </div>
              </div>
              <div className="project-card-desc">{p.description || 'No description'}</div>
              <div className="project-card-meta">
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <HiOutlineGlobeAlt /> {p.wp_site_name}
                  {p.wp_site_url && <span style={{ color: 'var(--text-muted)', fontSize: '0.9em', marginLeft: 4 }}>({p.wp_site_url})</span>}
                </span>
                <span>{new Date(p.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Create Project</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}><HiOutlineXMark /></button>
            </div>
            {sites.length === 0 ? (
              <div className="empty-state" style={{ padding: '32px 0' }}>
                <div className="empty-state-title">No WordPress Sites</div>
                <div className="empty-state-text">Add a WordPress site first in Settings</div>
              </div>
            ) : (
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label className="form-label">Project Title</label>
                  <input className="form-input" placeholder="e.g. Tech Blog Q1 2025" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Description</label>
                  <textarea className="form-textarea" placeholder="Optional description..." value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
                </div>
                <div className="form-group">
                  <label className="form-label">WordPress Site</label>
                  <select className="form-select" value={form.wp_site_id} onChange={e => setForm({ ...form, wp_site_id: e.target.value })} required>
                    {sites.map(s => <option key={s.id} value={s.id}>{s.name} ({s.url})</option>)}
                  </select>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary">Create Project</button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {showEditModal && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Edit Project</h2>
              <button className="modal-close" onClick={() => setShowEditModal(false)}><HiOutlineXMark /></button>
            </div>
            <form onSubmit={handleUpdate}>
              <div className="form-group">
                <label className="form-label">Project Title</label>
                <input className="form-input" placeholder="e.g. Tech Blog Q1 2025" value={editForm.title} onChange={e => setEditForm({ ...editForm, title: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea className="form-textarea" placeholder="Optional description..." value={editForm.description} onChange={e => setEditForm({ ...editForm, description: e.target.value })} />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowEditModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showDeleteModal && deleteConfirm && (
        <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Delete Project</h2>
              <button className="modal-close" onClick={() => setShowDeleteModal(false)}><HiOutlineXMark /></button>
            </div>
            <div style={{ padding: '24px 0' }}>
              <p style={{ marginBottom: '16px' }}>Are you sure you want to delete <strong>{deleteConfirm.title}</strong>?</p>
              <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>This will permanently delete the project and all its posts. This action cannot be undone.</p>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={() => setShowDeleteModal(false)}>Cancel</button>
              <button type="button" className="btn btn-primary danger" onClick={confirmDelete}>Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
