# Milestones

## v1.3 Content Quality Improvements (Shipped: 2026-04-17)

**Phases completed:** 2 phases, 3 plans

**Key accomplishments:**

- Implemented HTML cleaning foundation with 5-stage algorithm to sanitize AI-generated content
- Added beautifulsoup4>=4.12.0 and lxml>=5.0.0 dependencies for robust HTML sanitization
- Integrated HTML cleaning into generate_section_content() and generate_introduction()
- Created comprehensive test suite with 6 test functions covering HTML-01, HTML-02, HTML-03 requirements
- Ensured only safe HTML tags (h1-h6, p, strong, em, ul, ol, li, a, img) and attributes (href, src, alt, title) are preserved
- Removed markdown artifacts (backticks, code blocks) from AI-generated content
- Implemented WordCountService to accurately count words in HTML content
- Created WordCountValidator to check content against minimum and maximum word counts
- Added comprehensive unit tests for word count validation logic
- Fixed bug in HTML stripping logic to correctly handle tags with attributes

**Known gaps:**
- Phases 17-21 (Section Count Validation, Validation Results Display, Validation Warnings, Research Data Utilization, Research Context in Prompts) deferred to v1.4
- Word count validation service not yet integrated into content generation pipeline

---

## v1.1 All Posts Table View (Shipped: 2026-04-15)

**Phases completed:** 8 phases, 14 plans, 43 tasks

**Key accomplishments:**

- Status:
- Status:
- Status:
- API client updated with search/sort parameters and AllPosts component with state management for filtering and ordering posts
- Search input and sort dropdown UI controls added to AllPosts toolbar with consistent styling and event handling
- All 7 frontend requirements verified through comprehensive testing with 22 test scenarios, all passing
- PostCard component and all references removed from codebase after being replaced by table view in Phase 6
- Infinite scroll logic and all related state variables, functions, and event listeners removed from ProjectDetail.jsx after being replaced by manual pagination in Phase 6
- All unused CSS classes for PostCard component removed from index.css after component deletion in Plan 07-01
- Status:
- Formal verification report for Phase 6 frontend UI requirements with comprehensive evidence for pagination controls and loading states
- Formal verification documentation for Phase 7 cleanup with CLEANUP-02 (origin badges removal) verified and passed

---

## v1.0 MVP (Shipped: 2026-04-14)

**Phases completed:** 3 phases, 14 plans, 38 tasks

**Key accomplishments:**

- Found during:
- Frontend API client and state management for token usage data with loading/error states
- One-liner:
- Token usage display validated via comprehensive code review - 6/7 requirements met, 1 deviation identified (missing input/output token separation)
- WordPress REST API integration with search, filtering, sorting, and exponential backoff rate limiting
- Post origin tracking with origin field in Post model and sync service for WordPress post synchronization with duplicate prevention
- Orphan detection for posts that exist locally but not in WordPress, with three API endpoints for WordPress sync operations
- Filter, sort, and search controls for All Posts tab with status filtering, date/title/status sorting, and case-insensitive title search
- Infinite scroll pagination with loading indicator and automatic reset on filter/sort/search changes
- Backend API endpoint for fetching all posts with filter, sort, and search parameters, moving filtering logic from client-side to server-side for better performance
- Post URL display in PostCard component with clickable links, truncation for long URLs, and security attributes for external links
- Categories and tags support added to post system with WordPress REST API integration, backend API response, and frontend badge display

---
