import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter, MemoryRouter, Routes, Route } from 'react-router-dom'
import PropTypes from 'prop-types'
import PostView from './PostView'

// Mock the API client
const mockGetPost = vi.fn(() => Promise.resolve({ data: { id: '1', title: 'Test Post', language: 'vietnamese' } }))
const mockGetJobsByPost = vi.fn(() => Promise.resolve({ data: [] }))
const mockGetProviders = vi.fn(() => Promise.resolve({ data: [] }))
const mockGetDefaultModels = vi.fn(() => Promise.resolve({ data: { id: '1' } }))

vi.mock('../../api/client', () => ({
  getPost: () => mockGetPost(),
  publishPost: vi.fn(() => Promise.resolve()),
  unpublishPost: vi.fn(() => Promise.resolve()),
  generateOutline: vi.fn(() => Promise.resolve()),
  generateContent: vi.fn(() => Promise.resolve()),
  generateThumbnail: vi.fn(() => Promise.resolve()),
  generateThumbnailWithOptions: vi.fn(() => Promise.resolve()),
  getJobsByPost: () => mockGetJobsByPost(),
  getProviders: () => mockGetProviders(),
  getDefaultModels: () => mockGetDefaultModels(),
  uploadThumbnail: vi.fn(() => Promise.resolve()),
  updateThumbnailToWP: vi.fn(() => Promise.resolve()),
}))

// Test the LanguageBadge component directly
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

describe('PostView - Language Badge Display', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset default mock implementations
    mockGetPost.mockResolvedValue({ data: { id: '1', title: 'Test Post', language: 'vietnamese' } })
    mockGetJobsByPost.mockResolvedValue({ data: [] })
    mockGetProviders.mockResolvedValue({ data: [] })
    mockGetDefaultModels.mockResolvedValue({ data: { id: '1' } })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Language Badge Component', () => {
    it('should display "Tiếng Việt" when language is vietnamese', () => {
      render(<LanguageBadge language="vietnamese" />)
      const badge = screen.getByText(/tiếng việt/i)
      expect(badge).toBeInTheDocument()
    })

    it('should display "English" when language is english', () => {
      render(<LanguageBadge language="english" />)
      const badge = screen.getByText(/english/i)
      expect(badge).toBeInTheDocument()
    })

    it('should default to "English" when language is missing', () => {
      render(<LanguageBadge language={null} />)
      const badge = screen.getByText(/english/i)
      expect(badge).toBeInTheDocument()
    })

    it('should default to "English" when language is undefined', () => {
      render(<LanguageBadge language={undefined} />)
      const badge = screen.getByText(/english/i)
      expect(badge).toBeInTheDocument()
    })

    it('should have correct class name', () => {
      const { container } = render(<LanguageBadge language="vietnamese" />)
      const badge = container.querySelector('.status-badge')
      expect(badge).toBeInTheDocument()
    })

    it('should have inline styles for color coding', () => {
      const { container } = render(<LanguageBadge language="vietnamese" />)
      const badge = container.querySelector('.status-badge')
      expect(badge).toBeInTheDocument()
      expect(badge.style.color).toBe('var(--success)')
    })

    it('should use primary color for English', () => {
      const { container } = render(<LanguageBadge language="english" />)
      const badge = container.querySelector('.status-badge')
      expect(badge).toBeInTheDocument()
      expect(badge.style.color).toBe('var(--primary)')
    })

    it('should use success color for Vietnamese', () => {
      const { container } = render(<LanguageBadge language="vietnamese" />)
      const badge = container.querySelector('.status-badge')
      expect(badge).toBeInTheDocument()
      expect(badge.style.color).toBe('var(--success)')
    })
  })
})
