import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { HiOutlineArrowLeft, HiOutlineArrowPath, HiOutlineRocketLaunch, HiOutlineStop, HiOutlineCheckCircle, HiOutlineClock, HiOutlineXCircle } from 'react-icons/hi2'
import { getPost, publishPost, unpublishPost, generateThumbnail, generateSectionImages, getJobsByPost } from '../../api/client'

export default function PostView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [post, setPost] = useState(null)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { load() }, [id])

  useEffect(() => {
    const hasRunning = jobs.some(j => j.status === 'pending' || j.status === 'running')
    if (hasRunning) {
      const interval = setInterval(load, 3000)
      return () => clearInterval(interval)
    }
  }, [jobs])

  const load = async () => {
    try {
      const [postRes, jobsRes] = await Promise.all([getPost(id), getJobsByPost(id)])
      setPost(postRes.data)
      setJobs(jobsRes.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleAction = async (action) => {
    try {
      const actions = {
        publish: () => publishPost(id),
        unpublish: () => unpublishPost(id),
        thumbnail: () => generateThumbnail(id),
        section_images: () => generateSectionImages(id),
      }
      await actions[action]?.()
      load()
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  if (loading) return <div className="loading-page"><div className="loading-spinner" /></div>
  if (!post) return <div className="empty-state"><div className="empty-state-title">Post not found</div></div>

  const pipelineSteps = [
    { key: 'research', label: 'Research', done: post.research_done },
    { key: 'outline', label: 'Outline', done: !!post.outline },
    { key: 'content', label: 'Content', done: post.content_done },
    { key: 'thumbnail', label: 'Thumbnail', done: post.thumbnail_done },
    { key: 'section_images', label: 'Section Images', done: post.sections_done },
  ]

  const getStepStatus = (key) => {
    const job = jobs.find(j => j.job_type === key)
    if (!job) return 'idle'
    return job.status
  }

  const tu = post.token_usage || {}

  return (
    <div className="page-enter">
      <button className="btn btn-secondary" onClick={() => navigate(-1)} style={{ marginBottom: 20 }}>
        <HiOutlineArrowLeft /> Back
      </button>

      <div className="page-header">
        <h1 className="page-title">{post.title || post.topic}</h1>
        <div className="page-header-actions">
          <span className={`status-badge status-${post.status}`}>{post.status.replace('_', ' ')}</span>
          {post.content_done && post.status !== 'published' && (
            <button className="btn btn-success btn-sm" onClick={() => handleAction('publish')}><HiOutlineRocketLaunch /> Publish</button>
          )}
          {post.status === 'published' && (
            <button className="btn btn-danger btn-sm" onClick={() => handleAction('unpublish')}><HiOutlineStop /> Unpublish</button>
          )}
          {post.title && !post.thumbnail_done && (
            <button className="btn btn-secondary btn-sm" onClick={() => handleAction('thumbnail')}><HiOutlineArrowPath /> Generate Thumbnail</button>
          )}
          {post.content_done && !post.sections_done && (
            <button className="btn btn-secondary btn-sm" onClick={() => handleAction('section_images')}><HiOutlineArrowPath /> Generate Section Images</button>
          )}
        </div>
      </div>

      <div className="token-usage" style={{ marginBottom: 24 }}>
        <div className="token-item">
          <div className="token-label">Research</div>
          <div className="token-value">{(tu.research || 0).toLocaleString()}</div>
        </div>
        <div className="token-item">
          <div className="token-label">Outline</div>
          <div className="token-value">{(tu.outline || 0).toLocaleString()}</div>
        </div>
        <div className="token-item">
          <div className="token-label">Content</div>
          <div className="token-value">{(tu.content || 0).toLocaleString()}</div>
        </div>
        <div className="token-item">
          <div className="token-label">Thumbnail</div>
          <div className="token-value">{(tu.thumbnail || 0).toLocaleString()}</div>
        </div>
        <div className="token-item">
          <div className="token-label">Section Images</div>
          <div className="token-value">{(tu.section_images || 0).toLocaleString()}</div>
        </div>
        <div className="token-item">
          <div className="token-label">Total</div>
          <div className="token-value">{(tu.total || 0).toLocaleString()}</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: 'var(--text-heading)' }}>Pipeline Progress</h3>
        <div className="pipeline-steps">
          {pipelineSteps.map((step, index) => {
            const status = getStepStatus(step.key)
            const cls = step.done ? 'done' : status === 'running' ? 'active' : status === 'failed' ? 'error' : ''
            const isLast = index === pipelineSteps.length - 1
            return (
              <div key={step.key} className="pipeline-step-wrapper">
                <div className={`pipeline-step ${cls}`}>
                  <div className="pipeline-step-icon">
                    {step.done ? <HiOutlineCheckCircle /> : status === 'running' ? <span className="loading-spinner" style={{ width: 20, height: 20 }} /> : status === 'failed' ? <HiOutlineXCircle /> : <HiOutlineClock />}
                  </div>
                  <div className="pipeline-step-label">{step.label}</div>
                  <div className="pipeline-step-status">
                    {status === 'running' ? 'Running...' : status === 'failed' ? 'Failed' : step.done ? 'Completed' : 'Pending'}
                  </div>
                </div>
                {!isLast && <div className="pipeline-connector" />}
              </div>
            )
          })}
        </div>
      </div>

      {post.research_data && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: 'var(--text-heading)' }}>Research</h3>
          {post.research_data.target_audience && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>Target Audience</div>
              <div style={{ fontSize: 14 }}>{post.research_data.target_audience}</div>
            </div>
          )}
          {post.research_data.keywords && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>Keywords</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {post.research_data.keywords.map((kw, i) => (
                  <span key={i} style={{ padding: '2px 10px', background: 'rgba(108,92,231,0.1)', border: '1px solid rgba(108,92,231,0.2)', borderRadius: 20, fontSize: 12 }}>{kw}</span>
                ))}
              </div>
            </div>
          )}
          {post.research_data.key_points && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>Key Points</div>
              <ul style={{ paddingLeft: 20, fontSize: 14 }}>
                {post.research_data.key_points.map((p, i) => <li key={i} style={{ marginBottom: 4 }}>{p}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}

      {post.outline && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: 'var(--text-heading)' }}>Outline</h3>
          {post.meta_description && (
            <div style={{ marginBottom: 12, fontSize: 14, fontStyle: 'italic', color: 'var(--text-secondary)' }}>
              {post.meta_description}
            </div>
          )}
          {post.outline.introduction && (
            <div style={{ marginBottom: 16, padding: 16, background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>Introduction</div>
              <div style={{ fontSize: 13 }}><strong>Hook:</strong> {post.outline.introduction.hook}</div>
              <div style={{ fontSize: 13 }}><strong>Problem:</strong> {post.outline.introduction.problem}</div>
              <div style={{ fontSize: 13 }}><strong>Promise:</strong> {post.outline.introduction.promise}</div>
            </div>
          )}
          {post.outline.sections?.map((sec, i) => (
            <div key={i} style={{ padding: '8px 0', borderBottom: '1px solid var(--border-color)' }}>
              <div style={{ fontWeight: 600 }}>{i + 1}. {sec.title}</div>
              {sec.key_points && (
                <ul style={{ paddingLeft: 24, fontSize: 13, color: 'var(--text-secondary)' }}>
                  {sec.key_points.map((p, j) => <li key={j}>{p}</li>)}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}

      {post.content && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: 'var(--text-heading)' }}>Content Preview</h3>
          <div className="post-preview" dangerouslySetInnerHTML={{ __html: post.content }} />
        </div>
      )}

      {jobs.length > 0 && (
        <div className="card">
          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: 'var(--text-heading)' }}>Job History</h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Error</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map(j => (
                  <tr key={j.job_id}>
                    <td style={{ fontWeight: 600, textTransform: 'capitalize' }}>{j.job_type.replace('_', ' ')}</td>
                    <td><span className={`status-badge status-${j.status}`}>{j.status}</span></td>
                    <td style={{ color: 'var(--danger)', fontSize: 12 }}>{j.error || '—'}</td>
                    <td style={{ color: 'var(--text-muted)', fontSize: 13 }}>{j.created_at ? new Date(j.created_at).toLocaleString() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
