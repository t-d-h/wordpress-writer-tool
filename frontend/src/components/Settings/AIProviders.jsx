import { useState, useEffect } from 'react'
import { HiOutlinePlus, HiOutlineTrash, HiOutlinePencil, HiOutlineXMark } from 'react-icons/hi2'
import { getProviders, createProvider, updateProvider, deleteProvider, verifyProvider } from '../../api/client'

export default function AIProviders() {
  const [providers, setProviders] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState({ name: '', provider_type: 'gemini', api_key: '' })
  const [verifying, setVerifying] = useState(false)
  const [verifyResult, setVerifyResult] = useState(null)

  useEffect(() => { load() }, [])

  const load = async () => {
    try {
      const { data } = await getProviders()
      setProviders(data)
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
        await updateProvider(editingId, form)
      } else {
        await createProvider(form)
      }
      setShowModal(false)
      setEditingId(null)
      setForm({ name: '', provider_type: 'gemini', api_key: '' })
      load()
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  const handleEdit = (p) => {
    setEditingId(p.id)
    setForm({ name: p.name, provider_type: p.provider_type, api_key: '' })
    setShowModal(true)
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this provider?')) return
    try {
      await deleteProvider(id)
      load()
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  const handleTestProvider = async () => {
    if (!form.provider_type || !form.api_key) {
      setVerifyResult({ ok: false, message: 'Please select a Provider and enter an API Key first.' })
      return
    }
    setVerifying(true)
    setVerifyResult(null)
    try {
      await verifyProvider({ provider_type: form.provider_type, api_key: form.api_key })
      const label = form.provider_type.charAt(0).toUpperCase() + form.provider_type.slice(1)
      setVerifyResult({ ok: true, message: `API key verified! Connection to ${label} is working.` })
    } catch (e) {
      setVerifyResult({ ok: false, message: e.response?.data?.detail || e.message })
    } finally {
      setVerifying(false)
    }
  }

  const providerLabels = { openai: 'OpenAI', gemini: 'Gemini', anthropic: 'Anthropic' }

  return (
    <div className="page-enter">
      <div className="page-header">
        <h1 className="page-title">AI Providers</h1>
        <p className="page-description">Manage your AI provider API keys</p>
      </div>

      <div className="toolbar">
        <div />
        <button className="btn btn-primary" onClick={() => { setEditingId(null); setForm({ name: '', provider_type: 'gemini', api_key: '' }); setShowModal(true) }}>
          <HiOutlinePlus /> Add Provider
        </button>
      </div>

      {loading ? (
        <div className="loading-page"><div className="loading-spinner" /></div>
      ) : providers.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🤖</div>
          <div className="empty-state-title">No AI Providers</div>
          <div className="empty-state-text">Add an AI provider to start generating content</div>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            <HiOutlinePlus /> Add Provider
          </button>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Provider</th>
                <th>API Key</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {providers.map(p => (
                <tr key={p.id}>
                  <td style={{ fontWeight: 600 }}>{p.name}</td>
                  <td>
                    <span className="status-badge status-completed">{providerLabels[p.provider_type]}</span>
                  </td>
                  <td style={{ fontFamily: 'monospace', color: 'var(--text-muted)' }}>{p.api_key_preview}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{new Date(p.created_at).toLocaleDateString()}</td>
                  <td>
                    <div className="action-buttons">
                      <button className="action-btn" onClick={() => handleEdit(p)} title="Edit"><HiOutlinePencil /></button>
                      <button className="action-btn danger" onClick={() => handleDelete(p.id)} title="Delete"><HiOutlineTrash /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => { setShowModal(false); setVerifyResult(null) }}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">{editingId ? 'Edit' : 'Add'} AI Provider</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}><HiOutlineXMark /></button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Name</label>
                <input className="form-input" placeholder="e.g. My Gemini Key" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Provider</label>
                <select className="form-select" value={form.provider_type} onChange={e => setForm({ ...form, provider_type: e.target.value })}>
                  <option value="gemini">Gemini</option>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">API Key</label>
                <input className="form-input" type="password" placeholder={editingId ? 'Leave blank to keep current' : 'Enter API key'} value={form.api_key} onChange={e => { setForm({ ...form, api_key: e.target.value }); setVerifyResult(null) }} required={!editingId} />
                {verifyResult && (
                  <div style={{ fontSize: '13px', marginTop: '6px', padding: '6px 10px', borderRadius: '6px', background: verifyResult.ok ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)', color: verifyResult.ok ? 'var(--accent-primary, #22c55e)' : '#ef4444', border: `1px solid ${verifyResult.ok ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}` }}>
                    {verifyResult.message}
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="button" className="btn btn-secondary" onClick={handleTestProvider} disabled={verifying} style={{ opacity: verifying ? 0.6 : 1 }}>
                  {verifying ? 'Testing...' : 'Test API Key'}
                </button>
                <button type="submit" className="btn btn-primary" disabled={verifying}>{editingId ? 'Update' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
