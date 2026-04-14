import PropTypes from 'prop-types'

export default function PostCard({ post, onEdit }) {
  if (!post) {
    return null
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const originBadge = post.origin === 'tool' ? 'Tool' : 'Existing'
  const originClass = post.origin === 'tool' ? 'origin-tool' : 'origin-existing'

  const handleEdit = () => {
    if (onEdit) {
      onEdit(post)
    }
  }

  return (
    <div className="stat-card post-card">
      <div className="post-card-header">
        <span className={`origin-badge ${originClass}`}>{originBadge}</span>
        <span className={`status-badge status-${post.status}`}>
          {post.status.replace('_', ' ')}
        </span>
      </div>
      <h3 className="post-card-title">{post.title || 'Untitled'}</h3>
      <div className="post-card-meta">
        <span className="post-card-date">{formatDate(post.created_at || post.updated_at)}</span>
      </div>
      {post.wp_post_id && (
        <button className="btn btn-secondary btn-sm" onClick={handleEdit}>
          Edit in WordPress
        </button>
      )}
    </div>
  )
}

PostCard.propTypes = {
  post: PropTypes.object,
  onEdit: PropTypes.func
}
