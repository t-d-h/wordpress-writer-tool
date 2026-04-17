import PropTypes from 'prop-types'

export default function TokenUsageCard({ tokenUsage, defaultModels, loading, error }) {
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

  const inputTokens = tokenUsage.input_tokens || 0;
  const outputTokens = tokenUsage.output_tokens || 0;
  const inputPrice = defaultModels?.writing_input_price_per_m_tokens || 0;
  const outputPrice = defaultModels?.writing_output_price_per_m_tokens || 0;

  const totalCost = (inputTokens / 1000000) * inputPrice + (outputTokens / 1000000) * outputPrice;

  return (
    <div className="token-usage-card">
      <div className="token-usage-header">
        <h3 className="token-usage-title">Token Usage</h3>
      </div>

      <div className="token-usage-total">
        <div className="token-usage-total-label">Total Cost</div>
        <div className="token-usage-total-value">${totalCost.toFixed(4)}</div>
      </div>

      <div className="token-usage-total" style={{ borderTop: 'none', paddingTop: 0 }}>
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
        {inputTokens > 0 && (
          <div className="token-usage-row">
            <span className="token-usage-row-label">Input Tokens</span>
            <span className="token-usage-row-value">{formatNumber(inputTokens)}</span>
          </div>
        )}
        {outputTokens > 0 && (
          <div className="token-usage-row">
            <span className="token-usage-row-label">Output Tokens</span>
            <span className="token-usage-row-value">{formatNumber(outputTokens)}</span>
          </div>
        )}
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
    input_tokens: PropTypes.number,
    output_tokens: PropTypes.number,
  }),
  defaultModels: PropTypes.shape({
    writing_input_price_per_m_tokens: PropTypes.number,
    writing_output_price_per_m_tokens: PropTypes.number,
  }),
  loading: PropTypes.bool,
  error: PropTypes.string,
}

TokenUsageCard.defaultProps = {
  tokenUsage: null,
  defaultModels: null,
  loading: false,
  error: null,
}
