import PropTypes from 'prop-types'

export default function TokenUsageCard({ tokenUsage, loading, error }) {
  const formatNumber = (num) => {
    if (num === null || num === undefined) return '0'
    return num.toLocaleString()
  }

  if (loading) {
    return (
      <div className="token-usage-card loading">
        <div className="loading-spinner" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="token-usage-card error">
        <div className="token-usage-error">{error}</div>
      </div>
    )
  }

  if (!tokenUsage) {
    return (
      <div className="token-usage-card empty">
        <div className="token-usage-empty">No token usage data yet</div>
      </div>
    )
  }

  const breakdown = [
    { key: 'research', label: 'Research' },
    { key: 'outline', label: 'Outline' },
    { key: 'content', label: 'Content' },
    { key: 'thumbnail', label: 'Thumbnail' },
  ]

  return (
    <div className="token-usage-card">
      <div className="token-usage-header">
        <h3 className="token-usage-title">Token Usage</h3>
      </div>

      <div className="token-usage-total">
        <div className="token-usage-total-label">Total Tokens</div>
        <div className="token-usage-total-value">{formatNumber(tokenUsage.total)}</div>
      </div>

      <div className="token-usage-breakdown">
        {breakdown.map((item) => (
          <div key={item.key} className="token-usage-row">
            <span className="token-usage-row-label">{item.label}</span>
            <span className="token-usage-row-value">{formatNumber(tokenUsage[item.key])}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

TokenUsageCard.propTypes = {
  tokenUsage: PropTypes.shape({
    research: PropTypes.number,
    outline: PropTypes.number,
    content: PropTypes.number,
    thumbnail: PropTypes.number,
    total: PropTypes.number,
  }),
  loading: PropTypes.bool,
  error: PropTypes.string,
}

TokenUsageCard.defaultProps = {
  tokenUsage: null,
  loading: false,
  error: null,
}
