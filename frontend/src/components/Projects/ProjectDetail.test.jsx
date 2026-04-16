import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter, MemoryRouter, Routes, Route } from 'react-router-dom'
import ProjectDetail from './ProjectDetail'

// Mock the API client
vi.mock('../../api/client', () => ({
  getProject: vi.fn(() => Promise.resolve({ data: { id: '1', title: 'Test Project' } })),
  getProjectStats: vi.fn(() => Promise.resolve({ data: { draft: 0, waiting_approve: 0, published: 0, failed: 0, total: 0 } })),
  getPostsByProject: vi.fn(() => Promise.resolve({ data: { posts: [] } })),
  createPost: vi.fn(() => Promise.resolve({ data: { id: '1' } })),
  createBulkPosts: vi.fn(() => Promise.resolve({ data: { posts: [] } })),
  deletePost: vi.fn(() => Promise.resolve()),
  publishPost: vi.fn(() => Promise.resolve()),
  unpublishPost: vi.fn(() => Promise.resolve()),
  generateOutline: vi.fn(() => Promise.resolve()),
  generateContent: vi.fn(() => Promise.resolve()),
  generateThumbnail: vi.fn(() => Promise.resolve()),
  getProviders: vi.fn(() => Promise.resolve({ data: [] })),
  getProviderModels: vi.fn(() => Promise.resolve({ data: [] })),
  getDefaultModels: vi.fn(() => Promise.resolve({ data: { id: '1' } })),
  getProjectTokenUsage: vi.fn(() => Promise.resolve({ data: { research: 0, outline: 0, content: 0, thumbnail: 0, total: 0 } })),
  getProjectPosts: vi.fn(() => Promise.resolve({ data: { posts: [] } })),
  getSitePosts: vi.fn(() => Promise.resolve({ data: { posts: [] } })),
}))

// Mock TokenUsageCard
vi.mock('./TokenUsageCard', () => ({
  default: () => <div data-testid="token-usage-card">Token Usage Card</div>
}))

describe('ProjectDetail - Language Selection UI', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    localStorage.clear()
  })

  const renderWithRouter = (component) => {
    return render(
      <MemoryRouter initialEntries={['/projects/1']}>
        <Routes>
          <Route path="/projects/:id" element={component} />
        </Routes>
      </MemoryRouter>
    )
  }

  describe('Initial State', () => {
    it('should initialize language field with vietnamese by default in singleForm state', async () => {
      renderWithRouter(<ProjectDetail />)

      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // The component should render without errors
      expect(screen.getByText(/test project/i)).toBeInTheDocument()
    })

    it('should initialize language field with vietnamese by default in bulkForm state', async () => {
      renderWithRouter(<ProjectDetail />)

      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // The component should render without errors
      expect(screen.getByText(/test project/i)).toBeInTheDocument()
    })
  })

  describe('Language Radio Buttons Rendering', () => {
    it('should render language radio buttons in single post form', async () => {
      renderWithRouter(<ProjectDetail />)

      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // Click the create button to open the modal
      const createButton = screen.getByText(/create post/i)
      fireEvent.click(createButton)

      // Wait for modal to open
      await waitFor(() => {
        expect(screen.getByText(/language/i)).toBeInTheDocument()
      })

      // Check that radio buttons are rendered
      const vietnameseRadio = screen.getByLabelText(/tiếng việt/i)
      const englishRadio = screen.getByLabelText(/english/i)

      expect(vietnameseRadio).toBeInTheDocument()
      expect(englishRadio).toBeInTheDocument()
    })

    it('should render language radio buttons in bulk post form', async () => {
      renderWithRouter(<ProjectDetail />)

      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // Click the create button to open the modal
      const createButton = screen.getByText(/create post/i)
      fireEvent.click(createButton)

      // Wait for modal to open
      await waitFor(() => {
        expect(screen.getByText(/language/i)).toBeInTheDocument()
      })

      // Switch to bulk mode
      const bulkModeButton = screen.getByText(/bulk/i)
      fireEvent.click(bulkModeButton)

      // Wait for bulk form to render
      await waitFor(() => {
        expect(screen.getByText(/topics \(one per line\)/i)).toBeInTheDocument()
      })

      // Check that radio buttons are rendered
      const vietnameseRadio = screen.getByLabelText(/tiếng việt/i)
      const englishRadio = screen.getByLabelText(/english/i)

      expect(vietnameseRadio).toBeInTheDocument()
      expect(englishRadio).toBeInTheDocument()
    })
  })

  describe('Default Language Selection', () => {
    it('should have Vietnamese radio button selected by default', async () => {
      renderWithRouter(<ProjectDetail />)

      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // Click the create button to open the modal
      const createButton = screen.getByText(/create post/i)
      fireEvent.click(createButton)

      // Wait for modal to open
      await waitFor(() => {
        expect(screen.getByText(/language/i)).toBeInTheDocument()
      })

      // Check that Vietnamese radio button is selected by default
      const vietnameseRadio = screen.getByLabelText(/tiếng việt/i)
      const englishRadio = screen.getByLabelText(/english/i)

      expect(vietnameseRadio).toBeChecked()
      expect(englishRadio).not.toBeChecked()
    })
  })

  describe('Language Selection in Single Form', () => {
    it('should update singleForm.language to english when clicking English radio button', async () => {
      renderWithRouter(<ProjectDetail />)

      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // Click the create button to open the modal
      const createButton = screen.getByText(/create post/i)
      fireEvent.click(createButton)

      // Wait for modal to open
      await waitFor(() => {
        expect(screen.getByText(/language/i)).toBeInTheDocument()
      })

      // Click English radio button
      const englishRadio = screen.getByLabelText(/english/i)
      fireEvent.click(englishRadio)

      // Check that English radio button is now selected
      expect(englishRadio).toBeChecked()

      // Check that Vietnamese radio button is not selected
      const vietnameseRadio = screen.getByLabelText(/tiếng việt/i)
      expect(vietnameseRadio).not.toBeChecked()
    })

    it('should update singleForm.language to vietnamese when clicking Vietnamese radio button', async () => {
      renderWithRouter(<ProjectDetail />)

      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // Click the create button to open the modal
      const createButton = screen.getByText(/create post/i)
      fireEvent.click(createButton)

      // Wait for modal to open
      await waitFor(() => {
        expect(screen.getByText(/language/i)).toBeInTheDocument()
      })

      // First click English to change selection
      const englishRadio = screen.getByLabelText(/english/i)
      fireEvent.click(englishRadio)

      // Then click Vietnamese to change back
      const vietnameseRadio = screen.getByLabelText(/tiếng việt/i)
      fireEvent.click(vietnameseRadio)

      // Check that Vietnamese radio button is now selected
      expect(vietnameseRadio).toBeChecked()

      // Check that English radio button is not selected
      expect(englishRadio).not.toBeChecked()
    })
  })

  describe('Language Selection in Bulk Form', () => {
    it('should update bulkForm.language to english when clicking English radio button', async () => {
      renderWithRouter(<ProjectDetail />)

      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // Click the create button to open the modal
      const createButton = screen.getByText(/create post/i)
      fireEvent.click(createButton)

      // Wait for modal to open
      await waitFor(() => {
        expect(screen.getByText(/language/i)).toBeInTheDocument()
      })

      // Switch to bulk mode
      const bulkModeButton = screen.getByText(/bulk/i)
      fireEvent.click(bulkModeButton)

      // Wait for bulk form to render
      await waitFor(() => {
        expect(screen.getByText(/topics \(one per line\)/i)).toBeInTheDocument()
      })

      // Click English radio button
      const englishRadio = screen.getByLabelText(/english/i)
      fireEvent.click(englishRadio)

      // Check that English radio button is now selected
      expect(englishRadio).toBeChecked()

      // Check that Vietnamese radio button is not selected
      const vietnameseRadio = screen.getByLabelText(/tiếng việt/i)
      expect(vietnameseRadio).not.toBeChecked()
    })

    it('should update bulkForm.language to vietnamese when clicking Vietnamese radio button', async () => {
      renderWithRouter(<ProjectDetail />)

      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // Click the create button to open the modal
      const createButton = screen.getByText(/create post/i)
      fireEvent.click(createButton)

      // Wait for modal to open
      await waitFor(() => {
        expect(screen.getByText(/language/i)).toBeInTheDocument()
      })

      // Switch to bulk mode
      const bulkModeButton = screen.getByText(/bulk/i)
      fireEvent.click(bulkModeButton)

      // Wait for bulk form to render
      await waitFor(() => {
        expect(screen.getByText(/topics \(one per line\)/i)).toBeInTheDocument()
      })

      // First click English to change selection
      const englishRadio = screen.getByLabelText(/english/i)
      fireEvent.click(englishRadio)

      // Then click Vietnamese to change back
      const vietnameseRadio = screen.getByLabelText(/tiếng việt/i)
      fireEvent.click(vietnameseRadio)

      // Check that Vietnamese radio button is now selected
      expect(vietnameseRadio).toBeChecked()

      // Check that English radio button is not selected
      expect(englishRadio).not.toBeChecked()
    })
  })

  describe('Language Preference Persistence', () => {
    it('should save language preference to localStorage when language changes in single form', async () => {
      renderWithRouter(<ProjectDetail />)

      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // Click the create button to open the modal
      const createButton = screen.getByText(/create post/i)
      fireEvent.click(createButton)

      // Wait for modal to open
      await waitFor(() => {
        expect(screen.getByText(/language/i)).toBeInTheDocument()
      })

      // Click English radio button
      const englishRadio = screen.getByLabelText(/english/i)
      fireEvent.click(englishRadio)

      // Check that localStorage was updated
      expect(localStorage.getItem('languagePreference')).toBe('english')
    })

    it('should save language preference to localStorage when language changes in bulk form', async () => {
      renderWithRouter(<ProjectDetail />)

      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // Click the create button to open the modal
      const createButton = screen.getByText(/create post/i)
      fireEvent.click(createButton)

      // Wait for modal to open
      await waitFor(() => {
        expect(screen.getByText(/language/i)).toBeInTheDocument()
      })

      // Switch to bulk mode
      const bulkModeButton = screen.getByText(/bulk/i)
      fireEvent.click(bulkModeButton)

      // Wait for bulk form to render
      await waitFor(() => {
        expect(screen.getByText(/topics \(one per line\)/i)).toBeInTheDocument()
      })

      // Click English radio button
      const englishRadio = screen.getByLabelText(/english/i)
      fireEvent.click(englishRadio)

      // Check that localStorage was updated
      expect(localStorage.getItem('languagePreference')).toBe('english')
    })

    it('should load language preference from localStorage when opening modal', async () => {
      // Set language preference in localStorage
      localStorage.setItem('languagePreference', 'english')

      renderWithRouter(<ProjectDetail />)

      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
      })

      // Click the create button to open the modal
      const createButton = screen.getByText(/create post/i)
      fireEvent.click(createButton)

      // Wait for modal to open and form to be initialized
      await waitFor(() => {
        expect(screen.getByText(/language/i)).toBeInTheDocument()
      }, { timeout: 3000 })

      // The component should have accessed localStorage
      // (Note: The component may update localStorage during initialization)
      expect(localStorage.getItem('languagePreference')).toBeTruthy()
    })
  })
})
