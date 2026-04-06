import { useState, useEffect } from 'react'
import { HiOutlinePlus, HiOutlineTrash, HiOutlinePencil, HiOutlineXMark } from 'react-icons/hi2'
import { getSites, createSite, updateSite, deleteSite } from '../../api/client'

export default function WPSites() {
  const [sites, setSites] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState({ name: '', url: '', username: '', api_key: '' })

  useEffect(() => { load() }, [])

  const load = async () => {
    try {
      const { data } = await getSites()
      setSites(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingId) {
        await updateSite(editingId, form)
      } else {
        await createSite(form)
      }
      setShowModal(false)
      setEditingId(null)
      setForm({ name: '', url: '', username: '', api_key: '' })
      load()
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  const handleEdit = (s) => {
    setEditingId(s.id)
    setForm({ name: s.name, url: s.url, username: s.username, api_key: '' })
    setShowModal(true)
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this site?')) return
    try {
      await deleteSite(id)
      load()
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  return (
    <div className="page-enter">
      <div className="page-header">
        <h1 className="page-title">WordPress Sites</h1>
        <p className="page-description">Manage your WordPress site connections</p>
      </div>

      <div className="toolbar">
        <div />
        <button className="btn btn-primary" onClick={() => { setEditingId(null); setForm({ name: '', url: '', username: '', api_key: '' }); setShowModal(true) }}>
          <HiOutlinePlus /> Add Site
        </button>
      </div>

      {loading ? (
        <div className="loading-page"><div className="loading-spinner" /></div>
      ) : sites.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🌐</div>
          <div className="empty-state-title">No WordPress Sites</div>
          <div className="empty-state-text">Add a WordPress site to publish posts</div>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            <HiOutlinePlus /> Add Site
          </button>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>URL</th>
                <th>Username</th>
                <th>API Key</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sites.map(s => (
                <tr key={s.id}>
                  <td style={{ fontWeight: 600 }}>{s.name}</td>
                  <td><a href={s.url} target="_blank" rel="noopener" style={{ color: 'var(--accent-secondary)' }}>{s.url}</a></td>
                  <td>{s.username}</td>
                  <td style={{ fontFamily: 'monospace', color: 'var(--text-muted)' }}>{s.api_key_preview}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{new Date(s.created_at).toLocaleDateString()}</td>
                  <td>
                    <div className="action-buttons">
                      <button className="action-btn" onClick={() => handleEdit(s)} title="Edit"><HiOutlinePencil /></button>
                      <button className="action-btn danger" onClick={() => handleDelete(s.id)} title="Delete"><HiOutlineTrash /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">{editingId ? 'Edit' : 'Add'} WordPress Site</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}><HiOutlineXMark /></button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Site Name</label>
                <input className="form-input" placeholder="e.g. My Blog" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Site URL</label>
                <input className="form-input" type="url" placeholder="https://example.com" value={form.url} onChange={e => setForm({ ...form, url: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Username</label>
                <input className="form-input" placeholder="WordPress username" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Application Password</label>
                <input className="form-input" type="password" placeholder={editingId ? 'Leave blank to keep current' : 'WordPress application password'} value={form.api_key} onChange={e => setForm({ ...form, api_key: e.target.value })} required={!editingId} />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingId ? 'Update' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
