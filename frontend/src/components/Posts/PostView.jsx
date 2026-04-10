import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { HiOutlineArrowLeft, HiOutlineArrowPath, HiOutlineRocketLaunch, HiOutlineStop, HiOutlineCheckCircle, HiOutlineClock, HiOutlineXCircle, HiOutlineCloudArrowUp, HiOutlineSparkles } from 'react-icons/hi2'
import { getPost, publishPost, unpublishPost, generateOutline, generateContent, generateThumbnail, generateThumbnailWithOptions, generateSectionImages, getJobsByPost, getProviders, uploadThumbnail } from '../../api/client'

export default function PostView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [post, setPost] = useState(null)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [expandedStage, setExpandedStage] = useState(null)
  const [thumbnailTab, setThumbnailTab] = useState('generate')
  const [thumbnailForm, setThumbnailForm] = useState({ providerId: '', modelName: '' })
  const [uploadingThumbnail, setUploadingThumbnail] = useState(false)
  const [generatingThumbnail, setGeneratingThumbnail] = useState(false)
  const [providers, setProviders] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [filePreview, setFilePreview] = useState(null)

  useEffect(() => { load() }, [id])

  useEffect(() => {
    const hasRunning = jobs.some(j => j.status === 'pending' || j.status === 'running')
    if (hasRunning) {
      const interval = setInterval(load, 3000)
      return () => clearInterval(interval)
    }
  }, [jobs])

  useEffect(() => {
    getProviders().then(res => setProviders(res.data)).catch(console.error)
  }, [])

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
        outline: () => generateOutline(id),
        content: () => generateContent(id),
        thumbnail: () => generateThumbnail(id),
        section_images: () => generateSectionImages(id),
      }
      await actions[action]?.()
      load()
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  const handleStageClick = (stepKey, isDone) => {
    if (!isDone) return
    setExpandedStage(expandedStage === stepKey ? null : stepKey)
  }

  const handleGenerateThumbnail = async () => {
    try {
      setGeneratingThumbnail(true)
      await generateThumbnailWithOptions(id, thumbnailForm.providerId, thumbnailForm.modelName)
      load()
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    } finally {
      setGeneratingThumbnail(false)
    }
  }

  const handleUploadThumbnail = async () => {
    if (!selectedFile) {
      alert('Please select a file to upload')
      return
    }
    try {
      setUploadingThumbnail(true)
      await uploadThumbnail(id, selectedFile)
      setSelectedFile(null)
      setFilePreview(null)
      load()
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    } finally {
      setUploadingThumbnail(false)
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
      setFilePreview(URL.createObjectURL(file))
    }
  }

  if (loading) return <div className="loading-page"><div className="loading-spinner" /></div>
  if (!post) return <div className="empty-state"><div className="empty-state-title">Post not found</div></div>

  const pipelineSteps = [
    { key: 'research', label: 'Research', done: post.research_done },
    { key: 'outline', label: 'Outline', done: !!post.outline },
    { key: 'content', label: 'Content', done: post.content_done },
    { key: 'thumbnail', label: 'Thumbnail', done: post.thumbnail_done || !!post.thumbnail_url },
    { key: 'section_images', label: 'Section Images', done: post.sections_done || (post.sections && post.sections.some(s => s.image_url)) },
    { key: 'publish', label: 'Upload to WordPress', done: post.status === 'published' },
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
          {post.research_done && !post.outline && (
            <button className="btn btn-secondary btn-sm" onClick={() => handleAction('outline')} disabled={getStepStatus('outline') === 'running'}><HiOutlineRocketLaunch /> Generate Outline</button>
          )}
          {post.outline && !post.content_done && (
            <button className="btn btn-secondary btn-sm" onClick={() => handleAction('content')} disabled={getStepStatus('content') === 'running'}><HiOutlineRocketLaunch /> Generate Content</button>
          )}
          {post.content_done && post.status !== 'published' && (
            <button className="btn btn-success btn-sm" onClick={() => handleAction('publish')}><HiOutlineRocketLaunch /> Publish</button>
          )}
          {post.status === 'published' && (
            <button className="btn btn-danger btn-sm" onClick={() => handleAction('unpublish')}><HiOutlineStop /> Unpublish</button>
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
            const isExpanded = expandedStage === step.key
            return (
              <div key={step.key} className="pipeline-step-wrapper">
                <div
                  className={`pipeline-step ${cls} ${isExpanded ? 'expanded' : ''} ${step.done ? 'clickable' : ''}`}
                  onClick={() => handleStageClick(step.key, step.done)}
                >
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

      {expandedStage && (
        <div className="card" style={{ marginBottom: 24 }}>
          {expandedStage === 'research' && post.research_data && (
            <>
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
            </>
          )}
          {expandedStage === 'outline' && post.outline && (
            <>
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
            </>
          )}
          {expandedStage === 'content' && post.content && (
            <>
              <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: 'var(--text-heading)' }}>Content Preview</h3>
              <div className="post-preview" dangerouslySetInnerHTML={{ __html: post.content }} />
            </>
          )}
          {expandedStage === 'thumbnail' && (
            <>
              <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: 'var(--text-heading)' }}>Thumbnail</h3>
              {post.thumbnail_url ? (
                <img src={post.thumbnail_url} alt="Thumbnail" style={{ maxWidth: '100%', borderRadius: 'var(--radius-md)', marginBottom: 16 }} />
              ) : (
                <div style={{ padding: 32, textAlign: 'center', color: 'var(--text-muted)', background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)', marginBottom: 16 }}>
                  No thumbnail generated yet
                </div>
              )}
              <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
                <button className="btn btn-secondary btn-sm" onClick={() => setThumbnailTab('generate')}>
                  <HiOutlineSparkles /> Generate Image
                </button>
                <button className="btn btn-secondary btn-sm" onClick={() => setThumbnailTab('upload')}>
                  <HiOutlineCloudArrowUp /> Upload Image
                </button>
              </div>
              {thumbnailTab === 'generate' && (
                <div style={{ padding: 20, background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)', marginBottom: 16 }}>
                  <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16, color: 'var(--text-heading)' }}>Generate Thumbnail with AI</h4>
                  <div className="form-group">
                    <label className="form-label">AI Provider</label>
                    <select
                      className="form-select"
                      value={thumbnailForm.providerId}
                      onChange={(e) => setThumbnailForm({ ...thumbnailForm, providerId: e.target.value, modelName: '' })}
                    >
                      <option value="">Select provider</option>
                      {providers.filter(p => p.provider_type === 'gemini' || p.provider_type === 'openai').map(p => (
                        <option key={p.id} value={p.id}>{p.name} ({p.provider_type})</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Model</label>
                    <select
                      className="form-select"
                      value={thumbnailForm.modelName}
                      onChange={(e) => setThumbnailForm({ ...thumbnailForm, modelName: e.target.value })}
                      disabled={!thumbnailForm.providerId}
                    >
                      <option value="">Select model</option>
                      {thumbnailForm.providerId && (() => {
                        const provider = providers.find(p => p.id === thumbnailForm.providerId)
                        if (!provider) return null
                        const models = provider.provider_type === 'gemini'
                          ? ['gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-1.5-flash']
                          : ['dall-e-3', 'dall-e-2']
                        return models.map(m => <option key={m} value={m}>{m}</option>)
                      })()}
                    </select>
                  </div>
                  <button
                    className="btn btn-primary"
                    onClick={handleGenerateThumbnail}
                    disabled={!thumbnailForm.providerId || !thumbnailForm.modelName || generatingThumbnail}
                  >
                    {generatingThumbnail ? <span className="loading-spinner" style={{ width: 16, height: 16 }} /> : <HiOutlineSparkles />}
                    {generatingThumbnail ? ' Generating...' : ' Generate'}
                  </button>
                </div>
              )}
              {thumbnailTab === 'upload' && (
                <div style={{ padding: 20, background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)', marginBottom: 16 }}>
                  <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16, color: 'var(--text-heading)' }}>Upload Thumbnail Image</h4>
                  <div className="form-group">
                    <label className="form-label">Image File</label>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileSelect}
                      style={{ display: 'none' }}
                      id="thumbnail-upload"
                    />
                    <label
                      htmlFor="thumbnail-upload"
                      className="file-upload"
                      style={{
                        display: 'block',
                        padding: 32,
                        border: '2px dashed var(--border-color)',
                        borderRadius: 'var(--radius-md)',
                        textAlign: 'center',
                        cursor: 'pointer',
                        transition: 'all var(--transition-fast)'
                      }}
                    >
                      {selectedFile ? (
                        <>
                          <div style={{ fontSize: 14, marginBottom: 8 }}>{selectedFile.name}</div>
                          {filePreview && <img src={filePreview} alt="Preview" style={{ maxWidth: '100%', maxHeight: 200, borderRadius: 'var(--radius-sm)' }} />}
                        </>
                      ) : (
                        <>
                          <HiOutlineCloudArrowUp style={{ fontSize: 32, marginBottom: 8, color: 'var(--text-muted)' }} />
                          <div style={{ fontSize: 14, color: 'var(--text-muted)' }}>Click to select an image</div>
                        </>
                      )}
                    </label>
                  </div>
                  <button
                    className="btn btn-primary"
                    onClick={handleUploadThumbnail}
                    disabled={!selectedFile || uploadingThumbnail}
                  >
                    {uploadingThumbnail ? <span className="loading-spinner" style={{ width: 16, height: 16 }} /> : <HiOutlineCloudArrowUp />}
                    {uploadingThumbnail ? ' Uploading...' : ' Upload'}
                  </button>
                </div>
              )}
            </>
          )}
          {expandedStage === 'section_images' && post.sections && post.sections.length > 0 && post.sections.some(s => s.image_url) && (
            <>
              <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: 'var(--text-heading)' }}>Section Images</h3>
              {post.sections.filter(s => s.image_url).map((section, i) => (
                <div key={i} style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>{section.title}</div>
                  <img src={section.image_url} alt={section.title} style={{ maxWidth: '100%', borderRadius: 'var(--radius-md)' }} />
                </div>
              ))}
            </>
          )}
          {expandedStage === 'publish' && (
            <>
              <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: 'var(--text-heading)' }}>Upload to WordPress</h3>
              {post.status === 'published' ? (
                <div style={{ padding: 16, background: 'rgba(39, 174, 96, 0.1)', color: 'var(--success)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(39, 174, 96, 0.2)' }}>
                  This post has been successfully published to WordPress.
                  {post.wp_post_id && <div style={{ marginTop: 8, fontSize: 14 }}>Post ID: {post.wp_post_id}</div>}
                </div>
              ) : (
                <div style={{ padding: 16, background: 'var(--bg-glass)', color: 'var(--text-muted)', borderRadius: 'var(--radius-md)' }}>
                  Post has not been uploaded to WordPress yet.
                  {post.content_done && (
                    <div style={{ marginTop: 16 }}>
                      <button className="btn btn-success" onClick={() => handleAction('publish')} disabled={getStepStatus('publish') === 'running'}>
                        <HiOutlineRocketLaunch /> Publish Now
                      </button>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
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
