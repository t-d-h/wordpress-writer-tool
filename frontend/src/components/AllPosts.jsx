import { useState, useEffect } from 'react'
import { HiOutlinePencil, HiOutlineArrowPath, HiOutlineMagnifyingGlass } from 'react-icons/hi2'
import { getSites, getSitePosts } from '../api/client'

export default function AllPosts() {
  const [sites, setSites] = useState([])
  const [selectedSite, setSelectedSite] = useState(null)
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [fetchingPosts, setFetchingPosts] = useState(false)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [statusFilter, setStatusFilter] = useState('any')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState('date')
  const [sortOrder, setSortOrder] = useState('desc')
  const [error, setError] = useState(null)

  useEffect(() => {
    loadSites()
  }, [])

  useEffect(() => {
    if (selectedSite) {
      loadPosts()
    }
  }, [selectedSite, page, statusFilter, searchQuery, sortBy, sortOrder])

  const loadSites = async () => {
    try {
      const { data } = await getSites()
      setSites(data)
      if (data.length > 0 && !selectedSite) {
        setSelectedSite(data[0])
      }
    } catch (e) {
      console.error('Failed to load sites:', e)
      setError('Failed to load WordPress sites')
    } finally {
      setLoading(false)
    }
  }

  const loadPosts = async () => {
    if (!selectedSite) return

    setFetchingPosts(true)
    setError(null)
    try {
      const { data } = await getSitePosts(
        selectedSite.id,
        100,
        page,
        statusFilter === 'any' ? null : statusFilter,
        searchQuery || null,
        sortBy,
        sortOrder
      )
      setPosts(data.posts || [])
      setTotal(data.total || 0)
    } catch (e) {
      console.error('Failed to load posts:', e)
      setError('Failed to load posts from WordPress')
    } finally {
      setFetchingPosts(false)
    }
  }

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value)
    setPage(1)
  }

  const handleSortChange = (e) => {
    const value = e.target.value
    const [sortBy, sortOrder] = value.split('-')
    setSortBy(sortBy)
    setSortOrder(sortOrder)
    setPage(1)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString()
  }

  const getEditUrl = (postId) => {
    if (!selectedSite?.url) return '#'
    const baseUrl = selectedSite.url.replace(/\/$/, '')
    return `${baseUrl}/wp-admin/post.php?post=${postId}&action=edit`
  }

  const getCategoryNames = (categories) => {
    if (!categories || categories.length === 0) return '-'
    return categories.map(c => c.name).join(', ')
  }

  const getTagNames = (tags) => {
    if (!tags || tags.length === 0) return '-'
    return tags.map(t => t.name).join(', ')
  }

  if (loading) {
    return <div className="loading-page"><div className="loading-spinner" /></div>
  }

  return (
    <div className="page-enter">
      <div className="page-header">
        <h1 className="page-title">All Posts</h1>
        <p className="page-description">View and manage all posts on your WordPress site</p>
      </div>

      <div className="toolbar">
        <div className="toolbar-group">
          <label className="form-label" style={{ marginRight: '8px' }}>Site:</label>
          <select
            className="form-select"
            value={selectedSite?.id || ''}
            onChange={(e) => {
              const site = sites.find(s => s.id === e.target.value)
              setSelectedSite(site)
              setPage(1)
            }}
            style={{ minWidth: '200px' }}
          >
            {sites.map(site => (
              <option key={site.id} value={site.id}>{site.name}</option>
            ))}
          </select>
        </div>

        <div className="toolbar-group">
          <label className="form-label" style={{ marginRight: '8px' }}>Status:</label>
          <select
            className="form-select"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value)
              setPage(1)
            }}
            style={{ minWidth: '150px' }}
          >
            <option value="any">All</option>
            <option value="publish">Published</option>
            <option value="draft">Draft</option>
            <option value="pending">Pending</option>
          </select>
        </div>

        <div className="toolbar-group">
          <label className="form-label" style={{ marginRight: '8px' }}>Search:</label>
          <input
            type="text"
            className="form-input"
            placeholder="Search by title..."
            value={searchQuery}
            onChange={handleSearchChange}
            style={{ width: '200px', minWidth: '150px' }}
          />
        </div>

        <div className="toolbar-group">
          <label className="form-label" style={{ marginRight: '8px' }}>Sort:</label>
          <select
            className="form-select"
            value={`${sortBy}-${sortOrder}`}
            onChange={handleSortChange}
            style={{ width: '180px', minWidth: '140px' }}
          >
            <option value="date-desc">Date (Newest)</option>
            <option value="date-asc">Date (Oldest)</option>
            <option value="title-asc">Title (A-Z)</option>
            <option value="title-desc">Title (Z-A)</option>
            <option value="status-asc">Status</option>
          </select>
        </div>

        <button
          className="btn btn-secondary"
          onClick={loadPosts}
          disabled={fetchingPosts}
        >
          <HiOutlineArrowPath /> {fetchingPosts ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      {!selectedSite ? (
        <div className="empty-state">
          <div className="empty-state-icon">🌐</div>
          <div className="empty-state-title">No WordPress Site</div>
          <div className="empty-state-text">Add a WordPress site to view posts</div>
        </div>
      ) : fetchingPosts && posts.length === 0 ? (
        <div className="loading-page"><div className="loading-spinner" /></div>
      ) : posts.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📝</div>
          <div className="empty-state-title">No Posts Found</div>
          <div className="empty-state-text">This site has no posts yet</div>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>URL</th>
                <th>Categories</th>
                <th>Tags</th>
                <th>Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {posts.map(post => (
                <tr key={post.id}>
                  <td style={{ fontWeight: 600 }}>{post.title.rendered || '(Untitled)'}</td>
                  <td>
                    <a href={post.link} target="_blank" rel="noopener" style={{ color: 'var(--accent-secondary)' }}>
                      {post.link}
                    </a>
                  </td>
                  <td style={{ fontSize: '13px' }}>{getCategoryNames(post._embedded?.['wp:term']?.[0])}</td>
                  <td style={{ fontSize: '13px' }}>{getTagNames(post._embedded?.['wp:term']?.[1])}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{formatDate(post.date)}</td>
                  <td>
                    <span className={`status-badge ${post.status}`}>
                      {post.status}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <a
                        href={getEditUrl(post.id)}
                        target="_blank"
                        rel="noopener"
                        className="action-btn"
                        title="Edit in WordPress"
                      >
                        <HiOutlinePencil />
                      </a>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {total > 100 && (
            <div className="pagination">
              <button
                className="btn btn-secondary"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </button>
              <span style={{ margin: '0 16px' }}>
                Page {page} of {Math.ceil(total / 100)}
              </span>
              <button
                className="btn btn-secondary"
                onClick={() => setPage(p => p + 1)}
                disabled={page * 100 >= total}
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
