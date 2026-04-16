import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import PropTypes from 'prop-types'
import { HiOutlinePlus, HiOutlineXMark, HiOutlineCheckCircle, HiOutlineXCircle, HiOutlineClock, HiOutlineSparkles, HiArrowPath } from 'react-icons/hi2'
import { getProject, getProjectStats, getPostsByProject, createPost, createBulkPosts, deletePost, publishPost, unpublishPost, generateOutline, generateContent, generateThumbnail, getProviders, getProviderModels, getDefaultModels, getProjectTokenUsage, getProjectPosts, getSitePosts } from '../../api/client'
import TokenUsageCard from './TokenUsageCard'

export default function ProjectDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [stats, setStats] = useState({ draft: 0, waiting_approve: 0, published: 0, failed: 0, total: 0 })
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [tokenUsage, setTokenUsage] = useState(null)
  const [loadingTokenUsage, setLoadingTokenUsage] = useState(false)
  const [tokenUsageError, setTokenUsageError] = useState(null)
  const [activeTab, setActiveTab] = useState('content')
  const [statusFilter, setStatusFilter] = useState('all')
  const [sortBy, setSortBy] = useState('date-desc')
  const [searchQuery, setSearchQuery] = useState('')
  const [wpPosts, setWpPosts] = useState([])
  const [loadingWpPosts, setLoadingWpPosts] = useState(false)
  const [wpPostsError, setWpPostsError] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [createMode, setCreateMode] = useState('single')
  const [singleForm, setSingleForm] = useState({
    topic: '',
    additional_requests: '',
    ai_provider_id: '',
    model_name: '',
    auto_publish: false,
    thumbnail_source: 'ai',
    thumbnail_provider_id: '',
    thumbnail_model_name: '',
    target_word_count: 500,
    target_section_count: 4,
    thumbnail_file: null,
    language: 'vietnamese'
  })
  const [bulkForm, setBulkForm] = useState({
    topics: '',
    additional_requests: '',
    ai_provider_id: '',
    model_name: '',
    auto_publish: false,
    thumbnail_source: 'ai',
    thumbnail_provider_id: '',
    thumbnail_model_name: '',
    target_word_count: 500,
    target_section_count: 4,
    thumbnail_file: null,
    language: 'vietnamese'
  })
  const [providers, setProviders] = useState([])
  const [contentModels, setContentModels] = useState([])
  const [loadingContentModels, setLoadingContentModels] = useState(false)
  const [contentModelError, setContentModelError] = useState(null)
  const [thumbnailModels, setThumbnailModels] = useState([])
  const [loadingThumbnailModels, setLoadingThumbnailModels] = useState(false)
  const [thumbnailModelError, setThumbnailModelError] = useState(null)
  const [defaultModels, setDefaultModels] = useState({
    writing_provider_id: '',
    writing_model_name: '',
    image_provider_id: '',
    image_model_name: '',
    video_provider_id: '',
    video_model_name: '',
  })

  useEffect(() => { load() }, [id])

  useEffect(() => {
    if (showCreateModal) {
      // Initialize form with default values when opening modal
      if (createMode === 'single') {
        setSingleForm({
          topic: '',
          additional_requests: '',
          ai_provider_id: defaultModels.writing_provider_id || '',
          model_name: defaultModels.writing_model_name || '',
          auto_publish: false,
          thumbnail_source: 'ai',
          thumbnail_provider_id: defaultModels.image_provider_id || '',
          thumbnail_model_name: defaultModels.image_model_name || '',
          target_word_count: 500,
          target_section_count: 4,
          thumbnail_file: null,
          language: 'vietnamese'
        })
      } else {
        setBulkForm({
          topics: '',
          additional_requests: '',
          ai_provider_id: defaultModels.writing_provider_id || '',
          model_name: defaultModels.writing_model_name || '',
          auto_publish: false,
          thumbnail_source: 'ai',
          thumbnail_provider_id: defaultModels.image_provider_id || '',
          thumbnail_model_name: defaultModels.image_model_name || '',
          target_word_count: 500,
          target_section_count: 4,
          thumbnail_file: null,
          language: 'vietnamese'
        })
      }

      // Fetch models for the default providers
      const fetchDefaultModels = async () => {
        if (createMode === 'single') {
          if (defaultModels.writing_provider_id) {
            await fetchModelsForProvider(defaultModels.writing_provider_id, 'content')
          }
          if (defaultModels.image_provider_id) {
            await fetchModelsForProvider(defaultModels.image_provider_id, 'thumbnail')
          }
        } else {
          if (defaultModels.writing_provider_id) {
            await fetchModelsForProvider(defaultModels.writing_provider_id, 'content')
          }
          if (defaultModels.image_provider_id) {
            await fetchModelsForProvider(defaultModels.image_provider_id, 'thumbnail')
          }
        }
      }
      fetchDefaultModels()
    } else {
      // Reset form when closing modal
      setSingleForm({
        topic: '',
        additional_requests: '',
        ai_provider_id: '',
        model_name: '',
        auto_publish: false,
        thumbnail_source: 'ai',
        thumbnail_provider_id: '',
        thumbnail_model_name: '',
        target_word_count: 500,
        target_section_count: 4,
        thumbnail_file: null,
        language: 'vietnamese'
      })
      setBulkForm({
        topics: '',
        additional_requests: '',
        ai_provider_id: '',
        model_name: '',
        auto_publish: false,
        thumbnail_source: 'ai',
        thumbnail_provider_id: '',
        thumbnail_model_name: '',
        target_word_count: 500,
        target_section_count: 4,
        thumbnail_file: null,
        language: 'vietnamese'
      })
    }
  }, [showCreateModal, createMode])

  useEffect(() => {
    if (activeTab === 'all-posts' && project && project.wp_site_id) {
      loadWpPosts()
    }
  }, [activeTab, id, project?.wp_site_id, statusFilter, sortBy, searchQuery])

  const load = async () => {
    try {
      const [projRes, statsRes, postsRes, providersRes, defaultsRes] = await Promise.all([
        getProject(id),
        getProjectStats(id),
        getPostsByProject(id),
        getProviders(),
        getDefaultModels(),
      ])
      setProject(projRes.data)
      setStats(statsRes.data)
      setPosts(postsRes.data.posts || [])
      setProviders(providersRes.data)
      if (defaultsRes.data && defaultsRes.data.id) {
        setDefaultModels({
          writing_provider_id: defaultsRes.data.writing_provider_id || '',
          writing_model_name: defaultsRes.data.writing_model_name || '',
          image_provider_id: defaultsRes.data.image_provider_id || '',
          image_model_name: defaultsRes.data.image_model_name || '',
          video_provider_id: defaultsRes.data.video_provider_id || '',
          video_model_name: defaultsRes.data.video_model_name || '',
        })

        setSingleForm(prev => ({
          ...prev,
          ai_provider_id: defaultsRes.data.writing_provider_id || '',
          model_name: defaultsRes.data.writing_model_name || '',
          thumbnail_provider_id: defaultsRes.data.image_provider_id || '',
          thumbnail_model_name: defaultsRes.data.image_model_name || '',
        }))

        setBulkForm(prev => ({
          ...prev,
          ai_provider_id: defaultsRes.data.writing_provider_id || '',
          model_name: defaultsRes.data.writing_model_name || '',
          thumbnail_provider_id: defaultsRes.data.image_provider_id || '',
          thumbnail_model_name: defaultsRes.data.image_model_name || '',
        }))
      }

      // Load token usage data
      setLoadingTokenUsage(true)
      setTokenUsageError(null)
      try {
        const tokenUsageData = await getProjectTokenUsage(id)
        setTokenUsage(tokenUsageData)
      } catch (e) {
        console.error('Failed to load token usage:', e)
        setTokenUsageError('Unable to load token usage')
      } finally {
        setLoadingTokenUsage(false)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const loadWpPosts = async () => {
    if (!project || !project.wp_site_id) return

    setLoadingWpPosts(true)
    setWpPostsError(null)
    try {
      const { data } = await getSitePosts(
        project.wp_site_id,
        100,
        1,
        statusFilter === 'all' ? null : statusFilter,
        searchQuery || null,
        sortBy.split('-')[0],
        sortBy.split('-')[1]
      )
      setWpPosts(data.posts || [])
    } catch (e) {
      console.error('Failed to load WordPress posts:', e)
      setWpPostsError('Failed to load posts from WordPress')
    } finally {
      setLoadingWpPosts(false)
    }
  }

  const handleCreateSingle = async (e) => {
    e.preventDefault()

      if (singleForm.thumbnail_source === 'ai' && singleForm.thumbnail_provider_id) {
        const provider = providers.find(p => p.id === singleForm.thumbnail_provider_id)
        if (provider && provider.provider_type === 'openai_compatible' && !singleForm.thumbnail_model_name) {
          alert('Please select a model for thumbnail generation')
          return
        }
      }

      if (singleForm.ai_provider_id) {
        const provider = providers.find(p => p.id === singleForm.ai_provider_id)
        if (provider && provider.provider_type === 'openai_compatible' && !singleForm.model_name) {
          alert('Please select a model for content generation')
          return
        }
      }

      try {
        const formData = new FormData()
        formData.append('project_id', id)
        formData.append('topic', singleForm.topic)
        formData.append('additional_requests', singleForm.additional_requests)
        if (singleForm.ai_provider_id) formData.append('ai_provider_id', singleForm.ai_provider_id)
        if (singleForm.model_name) formData.append('model_name', singleForm.model_name)
        formData.append('auto_publish', singleForm.auto_publish)
        formData.append('thumbnail_source', singleForm.thumbnail_source)
        if (singleForm.thumbnail_provider_id) formData.append('thumbnail_provider_id', singleForm.thumbnail_provider_id)
        if (singleForm.thumbnail_model_name) formData.append('thumbnail_model_name', singleForm.thumbnail_model_name)
        if (singleForm.target_word_count) formData.append('target_word_count', singleForm.target_word_count)
        if (singleForm.target_section_count) formData.append('target_section_count', singleForm.target_section_count)
        formData.append('language', singleForm.language)

      const response = await createPost(Object.fromEntries(formData))

      setShowCreateModal(false)
      setSingleForm({
        topic: '',
        additional_requests: '',
        ai_provider_id: '',
        model_name: '',
        auto_publish: false,
        thumbnail_source: 'ai',
        thumbnail_provider_id: '',
        thumbnail_model_name: '',
        target_word_count: 500,
        target_section_count: 4,
        thumbnail_file: null,
        language: 'vietnamese'
      })
      load()
      if (response?.data?.id) {
        navigate(`/posts/${response.data.id}`)
      }
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  const handleCreateBulk = async (e) => {
    e.preventDefault()
    const topics = bulkForm.topics.split('\n').map(t => t.trim()).filter(Boolean)
    if (topics.length === 0) { alert('Enter at least one topic'); return }

    if (bulkForm.thumbnail_source === 'ai' && bulkForm.thumbnail_provider_id) {
      const provider = providers.find(p => p.id === bulkForm.thumbnail_provider_id)
      if (provider && provider.provider_type === 'openai_compatible' && !bulkForm.thumbnail_model_name) {
        alert('Please select a model for thumbnail generation')
        return
      }
    }

    if (bulkForm.ai_provider_id) {
      const provider = providers.find(p => p.id === bulkForm.ai_provider_id)
      if (provider && provider.provider_type === 'openai_compatible' && !bulkForm.model_name) {
        alert('Please select a model for content generation')
        return
      }
    }

    try {
      await createBulkPosts({
        project_id: id,
        topics,
        additional_requests: bulkForm.additional_requests,
        ai_provider_id: bulkForm.ai_provider_id,
        model_name: bulkForm.model_name,
        auto_publish: bulkForm.auto_publish,
        thumbnail_source: bulkForm.thumbnail_source,
        thumbnail_provider_id: bulkForm.thumbnail_provider_id,
        thumbnail_model_name: bulkForm.thumbnail_model_name,
        target_word_count: bulkForm.target_word_count,
        target_section_count: bulkForm.target_section_count,
        language: bulkForm.language,
      })
      setShowCreateModal(false)
      setBulkForm({
        topics: '',
        additional_requests: '',
        ai_provider_id: '',
        model_name: '',
        auto_publish: false,
        thumbnail_source: 'ai',
        thumbnail_provider_id: '',
        thumbnail_model_name: '',
        target_word_count: 500,
        target_section_count: 4,
        thumbnail_file: null,
        language: 'vietnamese'
      })
      load()
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  const handleAction = async (action, postId) => {
    try {
      const actions = {
        delete: () => { if (confirm('Delete this post?')) return deletePost(postId); return null },
        publish: () => publishPost(postId, true),
        unpublish: () => unpublishPost(postId),
        outline: () => generateOutline(postId),
        content: () => generateContent(postId),
        thumbnail: () => generateThumbnail(postId),
      }
      const result = await actions[action]?.()
      if (result !== null) load()
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  const handleProviderChange = (providerId, formType) => {
    if (formType === 'single') {
      setSingleForm({ ...singleForm, ai_provider_id: providerId, model_name: '' })
    } else {
      setBulkForm({ ...bulkForm, ai_provider_id: providerId, model_name: '' })
    }
  }

  const fetchModelsForProvider = async (providerId, section) => {
    const provider = providers.find(p => p.id === providerId)
    if (!provider || provider.provider_type !== 'openai_compatible') {
      if (section === 'content') {
        setContentModels([])
        setContentModelError(null)
      } else if (section === 'thumbnail') {
        setThumbnailModels([])
        setThumbnailModelError(null)
      }
      return
    }

    if (section === 'content') {
      setLoadingContentModels(true)
      setContentModelError(null)
    } else if (section === 'thumbnail') {
      setLoadingThumbnailModels(true)
      setThumbnailModelError(null)
    }

    try {
      const response = await getProviderModels(providerId)
      const models = response.data.models || []
      if (section === 'content') {
        setContentModels(models)
        if (models.length === 0) {
          setContentModelError('No models available for this provider')
        }
      } else if (section === 'thumbnail') {
        setThumbnailModels(models)
        if (models.length === 0) {
          setThumbnailModelError('No models available for this provider')
        }
      }
    } catch (e) {
      console.error('Failed to fetch models:', e)
      const errorMsg = 'Failed to fetch models. Please check your provider configuration.'
      if (section === 'content') {
        setContentModels([])
        setContentModelError(errorMsg)
      } else if (section === 'thumbnail') {
        setThumbnailModels([])
        setThumbnailModelError(errorMsg)
      }
    } finally {
      if (section === 'content') {
        setLoadingContentModels(false)
      } else if (section === 'thumbnail') {
        setLoadingThumbnailModels(false)
      }
    }
  }

  if (loading) return <div className="loading-page"><div className="loading-spinner" /></div>
  if (!project) return <div className="empty-state"><div className="empty-state-title">Project not found</div></div>

  const statCards = [
    { key: 'published', label: 'Published', value: stats.published },
    { key: 'waiting', label: 'Waiting Approve', value: stats.waiting_approve },
    { key: 'draft', label: 'Draft', value: stats.draft },
    { key: 'failed', label: 'Failed', value: stats.failed },
  ]

  return (
    <div className="page-enter">
      <div className="page-header">
        <h1 className="page-title">{project.title}</h1>
        <p className="page-description">{project.description || 'No description'} · {project.wp_site_name}</p>
      </div>

      <div className="tabs">
        <button className={`tab ${activeTab === 'general' ? 'active' : ''}`} onClick={() => setActiveTab('general')}>General</button>
        <button className={`tab ${activeTab === 'content' ? 'active' : ''}`} onClick={() => setActiveTab('content')}>Content</button>
        <button className={`tab ${activeTab === 'all-posts' ? 'active' : ''}`} onClick={() => setActiveTab('all-posts')}>All Posts</button>
      </div>

      {activeTab === 'general' && (
        <>
          <TokenUsageCard
            tokenUsage={tokenUsage}
            loading={loadingTokenUsage}
            error={tokenUsageError}
          />
          <div className="stats-grid">
            {statCards.map(c => (
              <div key={c.key} className={`stat-card ${c.key}`}>
                <div className="stat-label">{c.label}</div>
                <div className="stat-value">{c.value}</div>
              </div>
            ))}
          </div>
        </>
      )}

      {activeTab === 'content' && (
        <>
          <div className="toolbar">
            <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>{stats.total} post{stats.total !== 1 ? 's' : ''}</div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-secondary" onClick={() => load()}>
                <HiArrowPath /> Refresh
              </button>
              <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
                <HiOutlinePlus /> Create Post
              </button>
            </div>
          </div>

          {posts.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📝</div>
              <div className="empty-state-title">No Posts Yet</div>
              <div className="empty-state-text">Create your first post to get started</div>
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Title / Topic</th>
                    <th>Research</th>
                    <th>Outline</th>
                    <th>Content</th>
                    <th>Thumb</th>
                    <th>Uploaded</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                 <tbody>
                     {Array.isArray(posts) && posts.map(p => (
                       <tr key={p.id}>
                        <td>
                          <button
                            className="link-button"
                            onClick={() => navigate(`/posts/${p.id}`)}
                            style={{ fontWeight: 600, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--primary)', padding: 0, textAlign: 'left', fontSize: 'inherit' }}
                          >
                            {p.title || p.topic}
                          </button>
                        </td>
                        <td><LanguageBadge language={p.language} /></td>
                        <td><JobStatusBadge jobs={p.jobs} jobType="research" /></td>
                        <td><JobStatusBadge jobs={p.jobs} jobType="outline" /></td>
                        <td><JobStatusBadge jobs={p.jobs} jobType="content" /></td>
                        <td><JobStatusBadge jobs={p.jobs} jobType="thumbnail" /></td>
                        <td><BoolBadge value={!!p.wp_post_id} /></td>
                        <td><span className={`status-badge status-${p.status}`}>{p.status.replace('_', ' ')}</span></td>
                        <td>
                          <div className="action-buttons">
                            <button className="action-btn" onClick={() => navigate(`/posts/${p.id}`)}>View</button>
                            {p.status === 'published' ? (
                              <button className="action-btn" onClick={() => handleAction('unpublish', p.id)}>Unpublish</button>
                            ) : (
                              <button className="action-btn" onClick={() => handleAction('publish', p.id)}>Publish</button>
                            )}
                            {p.wp_post_id && project.wp_site_url && (
                              <a
                                className="action-btn"
                                href={`${project.wp_site_url}/?p=${p.wp_post_id}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{ textDecoration: 'none', display: 'inline-block' }}
                              >
                                View on WordPress
                              </a>
                            )}
                            <button className="action-btn danger" onClick={() => handleAction('delete', p.id)}>Delete</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {activeTab === 'all-posts' && (
        <>
          {loadingWpPosts ? (
            <div className="loading-page"><div className="loading-spinner" /></div>
          ) : wpPostsError ? (
            <div className="empty-state">
              <div className="empty-state-icon">⚠️</div>
              <div className="empty-state-title">Error Loading Posts</div>
              <div className="empty-state-text">{wpPostsError}</div>
            </div>
          ) : (
            <>
              <div className="toolbar" style={{ marginBottom: 20 }}>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center', flex: 1 }}>
                  <select
                    className="form-input"
                    style={{ width: 'auto', padding: '8px 12px' }}
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                  >
                    <option value="all">All Status</option>
                    <option value="published">Published</option>
                    <option value="draft">Draft</option>
                    <option value="pending">Pending</option>
                    <option value="failed">Failed</option>
                  </select>
                  <select
                    className="form-input"
                    style={{ width: 'auto', padding: '8px 12px' }}
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                  >
                    <option value="date-desc">Newest First</option>
                    <option value="date-asc">Oldest First</option>
                    <option value="title-asc">Title (A-Z)</option>
                    <option value="title-desc">Title (Z-A)</option>
                    <option value="status">Status</option>
                  </select>
                  <input
                    className="form-input"
                    type="text"
                    placeholder="Search by title..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={{ flex: 1, maxWidth: 300, padding: '8px 12px' }}
                  />
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <button className="btn btn-secondary" onClick={() => loadWpPosts()}>
                    <HiArrowPath /> Refresh
                  </button>
                  <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>
                    {wpPosts.length} post{wpPosts.length !== 1 ? 's' : ''}
                  </div>
                </div>
              </div>

              {wpPosts.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-state-icon">📄</div>
                  <div className="empty-state-title">No Posts Found</div>
                  <div className="empty-state-text">
                    {searchQuery || statusFilter !== 'all'
                      ? 'No posts match your filter, sort, or search criteria'
                      : 'No WordPress posts found for this project'}
                  </div>
                </div>
              ) : (
                <div className="table-container">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Title / Topic</th>
                        <th>URL</th>
                        <th>Categories</th>
                        <th>Tags</th>
                        <th>Date</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {wpPosts.map(post => (
                        <tr key={post.id}>
                          <td>
                            <button
                              onClick={() => window.open(post.link, '_blank')}
                              style={{ background: 'none', border: 'none', color: 'var(--accent-primary)', cursor: 'pointer', textAlign: 'left', padding: 0, fontSize: 14 }}
                            >
                              {post.title?.rendered || 'Untitled'}
                            </button>
                          </td>
                          <td>
                            {post.link ? (
                              <a
                                href={post.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{ color: 'var(--text-muted)', fontSize: 12, textDecoration: 'none' }}
                              >
                                {post.link}
                              </a>
                            ) : '-'}
                          </td>
                          <td>
                            {post._embedded?.['wp:term']?.[0]?.map(cat => cat.name).join(', ') || '-'}
                          </td>
                          <td>
                            {post._embedded?.['wp:term']?.[1]?.map(tag => tag.name).join(', ') || '-'}
                          </td>
                          <td>
                            {post.date ? new Date(post.date).toLocaleDateString() : '-'}
                          </td>
                          <td>
                            <span className={`status-badge status-${post.status}`}>
                              {post.status}
                            </span>
                          </td>
                          <td>
                            <button
                              onClick={() => window.open(`${project.wp_site_url}/wp-admin/post.php?post=${post.id}&action=edit`, '_blank')}
                              style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 4, fontSize: 12 }}
                            >
                              Edit
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </>
      )}

       {/* Create Post Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal modal-lg" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Create Post</h2>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}><HiOutlineXMark /></button>
            </div>

            <div className="tabs" style={{ marginBottom: 20 }}>
              <button className={`tab ${createMode === 'single' ? 'active' : ''}`} onClick={() => setCreateMode('single')}>Single Post</button>
              <button className={`tab ${createMode === 'bulk' ? 'active' : ''}`} onClick={() => setCreateMode('bulk')}>Bulk Posts</button>
            </div>

            {createMode === 'single' ? (
              <form onSubmit={handleCreateSingle}>
                {/* Publishing Options */}
                <div style={{ marginBottom: 24, paddingBottom: 16, borderBottom: '1px solid var(--border)' }}>
                  <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text-muted)' }}>Publishing Options</h3>
                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={singleForm.auto_publish}
                        onChange={e => setSingleForm({ ...singleForm, auto_publish: e.target.checked })}
                        style={{ cursor: 'pointer' }}
                      />
                      <span>Auto-publish after content generation</span>
                    </label>
                    <small style={{ display: 'block', marginTop: 4, color: 'var(--text-muted)' }}>If unchecked, post will be saved as draft</small>
                  </div>
                </div>

                {/* Thumbnail Options */}
                <div style={{ marginBottom: 24, paddingBottom: 16, borderBottom: '1px solid var(--border)' }}>
                  <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text-muted)' }}>Thumbnail Options</h3>
                  <div className="form-group" style={{ marginBottom: 12 }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                      <input
                        type="radio"
                        name="thumbnail_source"
                        value="ai"
                        checked={singleForm.thumbnail_source === 'ai'}
                        onChange={e => setSingleForm({ ...singleForm, thumbnail_source: e.target.value })}
                        style={{ cursor: 'pointer' }}
                      />
                      <span>Generate with AI</span>
                    </label>
                    {singleForm.thumbnail_source === 'ai' && (
                      <div style={{ marginLeft: 24, marginTop: 8, color: 'var(--text-muted)', fontSize: 13 }}>
                        Will be generated using default model settings
                      </div>
                    )}
                  </div>
                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                      <input
                        type="radio"
                        name="thumbnail_source"
                        value="upload"
                        checked={singleForm.thumbnail_source === 'upload'}
                        onChange={e => setSingleForm({ ...singleForm, thumbnail_source: e.target.value })}
                        style={{ cursor: 'pointer' }}
                      />
                      <span>Upload Image Later</span>
                    </label>
                    {singleForm.thumbnail_source === 'upload' && (
                      <div style={{ marginLeft: 24, marginTop: 8, color: 'var(--text-muted)', fontSize: 13 }}>
                        You can upload the thumbnail image in the post detail view after creation
                      </div>
                    )}
                  </div>
                </div>

                {/* Content Length Options */}
                <div style={{ marginBottom: 24, paddingBottom: 16, borderBottom: '1px solid var(--border)' }}>
                  <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text-muted)' }}>Content Length Options</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                    <div className="form-group">
                      <label className="form-label">Target Word Count</label>
                      <input
                        className="form-input"
                        type="number"
                        value={singleForm.target_word_count}
                        onChange={e => setSingleForm({ ...singleForm, target_word_count: parseInt(e.target.value) || 500 })}
                        min={100}
                        step={100}
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Target Section Count</label>
                      <input
                        className="form-input"
                        type="number"
                        value={singleForm.target_section_count}
                        onChange={e => setSingleForm({ ...singleForm, target_section_count: parseInt(e.target.value) || 4 })}
                        min={2}
                        max={20}
                      />
                    </div>
                  </div>
                </div>


                <div className="form-group">
                  <label className="form-label">Topic</label>
                  <input className="form-input" placeholder="e.g. How to Improve Your Website SEO" value={singleForm.topic} onChange={e => setSingleForm({ ...singleForm, topic: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Language</label>
                  <div style={{ display: 'flex', gap: 16, marginTop: 8 }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                      <input
                        type="radio"
                        name="language"
                        value="vietnamese"
                        checked={singleForm.language === 'vietnamese'}
                        onChange={e => setSingleForm({ ...singleForm, language: e.target.value })}
                        style={{ cursor: 'pointer' }}
                      />
                      <span>Tiếng Việt</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                      <input
                        type="radio"
                        name="language"
                        value="english"
                        checked={singleForm.language === 'english'}
                        onChange={e => setSingleForm({ ...singleForm, language: e.target.value })}
                        style={{ cursor: 'pointer' }}
                      />
                      <span>English</span>
                    </label>
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Additional Requests (Optional)</label>
                  <textarea className="form-textarea" placeholder="Any specific requirements..." value={singleForm.additional_requests} onChange={e => setSingleForm({ ...singleForm, additional_requests: e.target.value })} />
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary">Create & Start Research</button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleCreateBulk}>
                {/* Publishing Options */}
                <div style={{ marginBottom: 24, paddingBottom: 16, borderBottom: '1px solid var(--border)' }}>
                  <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text-muted)' }}>Publishing Options</h3>
                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={bulkForm.auto_publish}
                        onChange={e => setBulkForm({ ...bulkForm, auto_publish: e.target.checked })}
                        style={{ cursor: 'pointer' }}
                      />
                      <span>Auto-publish after content generation</span>
                    </label>
                    <small style={{ display: 'block', marginTop: 4, color: 'var(--text-muted)' }}>If unchecked, posts will be saved as draft</small>
                  </div>
                </div>

                {/* Thumbnail Options */}
                <div style={{ marginBottom: 24, paddingBottom: 16, borderBottom: '1px solid var(--border)' }}>
                  <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text-muted)' }}>Thumbnail Options</h3>
                  <div className="form-group" style={{ marginBottom: 12 }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                      <input
                        type="radio"
                        name="thumbnail_source"
                        value="ai"
                        checked={bulkForm.thumbnail_source === 'ai'}
                        onChange={e => setBulkForm({ ...bulkForm, thumbnail_source: e.target.value })}
                        style={{ cursor: 'pointer' }}
                      />
                      <span>Generate with AI</span>
                    </label>
                    {bulkForm.thumbnail_source === 'ai' && (
                      <div style={{ marginLeft: 24, marginTop: 8, color: 'var(--text-muted)', fontSize: 13 }}>
                        Will be generated using default model settings
                      </div>
                    )}
                  </div>
                  <div className="form-group">
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                      <input
                        type="radio"
                        name="thumbnail_source"
                        value="upload"
                        checked={bulkForm.thumbnail_source === 'upload'}
                        onChange={e => setBulkForm({ ...bulkForm, thumbnail_source: e.target.value })}
                        style={{ cursor: 'pointer' }}
                      />
                      <span>Upload Image Later</span>
                    </label>
                    {bulkForm.thumbnail_source === 'upload' && (
                      <div style={{ marginLeft: 24, marginTop: 8, color: 'var(--text-muted)', fontSize: 13 }}>
                        You can upload the thumbnail image in the post detail view after creation
                      </div>
                    )}
                  </div>
                </div>

                {/* Content Length Options */}
                <div style={{ marginBottom: 24, paddingBottom: 16, borderBottom: '1px solid var(--border)' }}>
                  <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text-muted)' }}>Content Length Options</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                    <div className="form-group">
                      <label className="form-label">Target Word Count</label>
                      <input
                        className="form-input"
                        type="number"
                        value={bulkForm.target_word_count}
                        onChange={e => setBulkForm({ ...bulkForm, target_word_count: parseInt(e.target.value) || 500 })}
                        min={100}
                        step={100}
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Target Section Count</label>
                      <input
                        className="form-input"
                        type="number"
                        value={bulkForm.target_section_count}
                        onChange={e => setBulkForm({ ...bulkForm, target_section_count: parseInt(e.target.value) || 4 })}
                        min={2}
                        max={20}
                      />
                    </div>
                  </div>
                </div>


                <div className="form-group">
                  <label className="form-label">Topics (one per line)</label>
                  <textarea className="form-textarea" style={{ minHeight: 150 }} placeholder={"Topic 1\nTopic 2\nTopic 3"} value={bulkForm.topics} onChange={e => setBulkForm({ ...bulkForm, topics: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Language</label>
                  <div style={{ display: 'flex', gap: 16, marginTop: 8 }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                      <input
                        type="radio"
                        name="language"
                        value="vietnamese"
                        checked={bulkForm.language === 'vietnamese'}
                        onChange={e => setBulkForm({ ...bulkForm, language: e.target.value })}
                        style={{ cursor: 'pointer' }}
                      />
                      <span>Tiếng Việt</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                      <input
                        type="radio"
                        name="language"
                        value="english"
                        checked={bulkForm.language === 'english'}
                        onChange={e => setBulkForm({ ...bulkForm, language: e.target.value })}
                        style={{ cursor: 'pointer' }}
                      />
                      <span>English</span>
                    </label>
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Additional Requests (Optional)</label>
                  <textarea className="form-textarea" placeholder="Applied to all posts..." value={bulkForm.additional_requests} onChange={e => setBulkForm({ ...bulkForm, additional_requests: e.target.value })} />
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary">Create All & Start Research</button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function BoolBadge({ value }) {
  return (
    <span className={`bool-indicator ${value ? 'bool-true' : 'bool-false'}`}>
      {value ? <HiOutlineCheckCircle /> : <HiOutlineXCircle />}
    </span>
  )
}

function JobStatusBadge({ jobs, jobType }) {
  const job = jobs?.find(j => j.job_type === jobType)
  if (!job) return <span className="status-badge status-idle">—</span>
  
  const statusConfig = {
    pending: { icon: <HiOutlineClock />, class: 'status-pending' },
    running: { icon: <HiArrowPath className="spin" />, class: 'status-running' },
    completed: { icon: <HiOutlineCheckCircle />, class: 'status-completed' },
    failed: { icon: <HiOutlineXCircle />, class: 'status-failed' },
  }
  
  const config = statusConfig[job.status] || { icon: null, class: 'status-idle' }
  
  return (
    <span className={`status-badge ${config.class}`}>
      {config.icon}
    </span>
  )
}

BoolBadge.propTypes = {
  value: PropTypes.bool.isRequired
}

JobStatusBadge.propTypes = {
  jobs: PropTypes.array.isRequired,
  jobType: PropTypes.string.isRequired
}

function LanguageBadge({ language }) {
  const langConfig = {
    vietnamese: { label: 'Tiếng Việt', color: 'var(--success)' },
    english: { label: 'English', color: 'var(--primary)' },
  }
  const config = langConfig[language] || langConfig.english

  return (
    <span className="status-badge" style={{ background: `${config.color}20`, color: config.color, border: `1px solid ${config.color}40` }}>
      {config.label}
    </span>
  )
}

LanguageBadge.propTypes = {
  language: PropTypes.string
}
