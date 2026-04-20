# WordPress Writer Tool

## What This Is

A full-stack AI content generation tool for WordPress sites. Users configure AI providers and WordPress sites, create projects with AI-assisted content pipelines (outlines, full articles, thumbnails, section images), and publish posts to WordPress. Backend is Python/FastAPI with MongoDB + Redis; frontend is React SPA.

## Core Value

Validate WordPress site connectivity and credentials before saving, so users know immediately if their site is configured correctly — not after wasting time creating content that can't be published.

## Current State

**Version:** v1.4 (in progress)

**Shipped Features (v1.3 Content Quality Improvements):**
- HTML cleaning foundation with 5-stage algorithm
  - Removes markdown code blocks and backticks
  - Sanitizes HTML with allowed tags whitelist
  - Integrated into generate_section_content() and generate_introduction()
- Word count validation service
  - WordCountService.count_words(html_content) for accurate word counting
  - WordCountValidator.validate() for min/max threshold checking
  - Comprehensive unit tests for edge cases
- Comprehensive test coverage
  - 6 test functions for HTML cleaning (HTML-01, HTML-02, HTML-03)
  - Unit tests for word count validation
  - Bug fixed: HTML tag stripping now correctly handles tags with attributes

**Known Limitations:**
- No authentication or user management (current milestone)
- Word count validation not yet integrated into content generation pipeline
- Section count validation not yet implemented
- Validation results display UI not yet implemented
- Validation warnings system not yet implemented
- Research data utilization not yet implemented
- Research context in prompts not yet implemented

**Next Milestone Goals (v1.5):**
- TBD after v1.4 completion

<details>
<summary>v1.3 Development History</summary>

## Requirements

### Validated

- CRUD for WordPress sites (name, URL, username, API key)
- CRUD for AI providers
- Project management linked to WP sites
- AI-assisted content pipeline: outline generation, full content, thumbnails, section images
- Async job processing via Redis pub/sub
- Post publishing to WordPress REST API
- Project statistics display (published, waiting approve, draft, failed posts)
- Token usage tracking per post (research, outline, content, thumbnail)
- Display token usage breakdown in Project general tab (above statistics)
  - Show breakdown by post type: research, outline, content, thumbnail
  - Include deleted posts in calculations
  - Always visible, calculate on-the-fly from posts collection
  - Validated in Phase 01: Token Usage Display
- WordPress REST API integration for fetching, filtering, and searching posts
  - Backend service supports pagination, status filtering, and search by title
  - Rate limiting with exponential backoff for API calls
  - Post origin tracking (tool-created vs existing)
  - Orphan detection for posts that exist locally but not in WordPress
  - API endpoints for WordPress sync functionality
   - Validated in Phase 02: WordPress Integration Backend
- All Posts tab UI for viewing and managing WordPress posts
  - Display all WordPress posts (both tool-created and existing)
  - Visual distinction between post types (origin badges)
  - Edit button opens WordPress admin in new tab
  - Filter by status, sort by date/title/status, search by title
  - Infinite scroll pagination for large post lists
  - Post URL display with security attributes
  - Post categories and tags display as badges
  - Validated in Phase 03: All Posts Tab UI
- Backend API enhancement with caching, pagination, and search/sort — v1.1
- Data transformation for WordPress REST API responses — v1.1
- Frontend UI with table view, search, sort, filter, and pagination — v1.1
- Cleanup of legacy PostCard component and infinite scroll — v1.1

### Active

None — all v1.4 requirements to be defined

## Current Milestone: v1.4 Initial Admin Account on First Startup

**Goal:** Create an initial admin user account automatically on first application startup using environment variables for credentials.

**Target features:**
- Read username from INIT_USER environment variable
- Read password from INIT_PASSWORD environment variable
- Create admin account with these credentials on first startup
- Admin account has full permissions/role
- Prompt for credentials if environment variables not provided (optional)

## Current State

**Version:** v1.3 (shipped 2026-04-17)

**Shipped Features (v1.0 MVP):**
- Token usage display with breakdown by post type
- WordPress REST API integration with search, filtering, and pagination
- All Posts tab UI with filter, sort, search, and infinite scroll
- Post origin tracking (tool-created vs existing)
- Post URL, categories, and tags display

**Shipped Features (v1.1 All Posts Table View):**
- Backend API enhancement with caching, pagination, and search/sort
- Data transformation for WordPress REST API responses
- Frontend UI with table view, search, sort, filter, and pagination
- Cleanup of legacy PostCard component and infinite scroll
- Backend API verification (Phase 8 complete)
- Data transformation documentation (Phase 9 complete)
- Frontend UI verification (Phase 10 complete)
- Cleanup verification (Phase 11 complete)

**Shipped Features (v1.2 Vietnamese Language Support):**
- Backend foundation for language support (Phase 12 complete)
  - Language field added to Post Pydantic models with pattern validation
  - Language field stored in MongoDB
  - API validates language is "vietnamese" or "english"
  - Backward compatibility: existing posts default to "english"
  - Test infrastructure created with pytest and fixtures
- AI service integration for language support (Phase 13 complete)
  - Language parameter added to all 5 AI service functions
  - Language-specific system prompts with Vietnamese cultural context
  - Worker tasks extract and pass language to AI service functions
  - End-to-end language flow from MongoDB to AI providers
- Frontend UI for language selection (Phase 14 complete)
  - Language selection checkbox in Create Post form
  - Language badge in post list table
  - Language badge in post detail view
  - localStorage persistence for language selection
  - Frontend testing infrastructure
  - Language parameter to worker AI service

**Next Milestone Goals (v1.4):**
- Implement section count validation (Phase 17)
- Implement validation results display UI (Phase 18)
- Implement validation warnings system (Phase 19)
- Implement research data utilization (Phase 20)
- Implement research context in prompts (Phase 21)
- Integrate word count validation into content generation pipeline

**Technical Debt:**
- 10 code review findings documented (2 critical, 5 warnings, 3 info)
- Plain-text credential storage (deferred)
- URL format validation gap (minor)

### Out of Scope

- Frontend UI toast styling — backend error details are sufficient for now
- Periodic re-validation of saved sites — validation only runs on site creation
- Token usage pagination — show all at once, note performance concern for later

## Context

This is a brownfield project with existing codebase mapped in `.planning/codebase/`. The system has a working AI content generation pipeline with job processing, WordPress integration, and project management.

**v1.0 MVP State:**
- 3 phases completed, 14 plans executed, 38 tasks delivered
- 16,329 lines of code added (Python + JavaScript/JSX)
- 8 days of development (2026-04-06 → 2026-04-14)
- UAT completed: 18/20 tests passed, 2 skipped (external dependencies)
- Code review: 10 findings (2 critical, 5 warnings, 3 info) — documented in 03-REVIEW.md

**v1.1 All Posts Table View State:**
- 8 phases completed, 14 plans executed, 43 tasks delivered
- 5,305 lines of code added, 445 lines removed (Python + JavaScript/JSX)
- 8 days of development (2026-04-06 → 2026-04-15)
- All 18 v1.1 requirements verified and documented
- Backend API with caching, pagination, and search/sort
- Frontend table view with search, sort, filter, and pagination
- Comprehensive verification documentation for all phases

**v1.2 Vietnamese Language Support State:**
- 3 phases completed, 12 plans executed, 36 tasks delivered
- Backend foundation for language support
- AI service integration for language support
- Frontend UI for language selection
- End-to-end language flow from MongoDB to AI providers

**v1.3 Content Quality Improvements State:**
- 2 phases completed, 3 plans executed
- HTML cleaning foundation with 5-stage algorithm
- Word count validation service
- Comprehensive test coverage for HTML cleaning and validation
- Phases 17-21 deferred to v1.4

**v1.4 Initial Admin Account on First Startup State:**
- 2 phases completed, 2 plans executed
- Configuration layer with INIT_USER and INIT_PASSWORD fields
- Fail-fast validation on startup for required environment variables
- Error logging for missing environment variables
- Phase 17 complete — configuration infrastructure ready for admin account creation
- Phase 18 complete — environment variable validation with error logging

**Known Issues:**
- Plain-text credential storage (deferred for security milestone)
- URL format validation gap (minor, not blocking)
- No pre-save connectivity check (feature for future milestone)
- Code review findings documented but not yet fixed (can be addressed in future milestones)

## Constraints

- **Tech stack**: Python/FastAPI backend, MongoDB, Redis, React frontend — these won't change for this project
- **MVP stage**: This is an early MVP; solutions should be pragmatic, not over-engineered
- **No app-level auth**: Relies on network-level isolation

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Token usage calculated on-the-fly | No caching needed for MVP, simpler implementation | ✓ Good — Implemented in Phase 01, performs well for <100 posts |
| Include deleted posts in token totals | Users want complete cost visibility | ✓ Good — Implemented in Phase 01, aggregation pipeline works correctly |
| Build features sequentially | Token usage first, then All Posts tab | ✓ Good — Phases 01, 02, 03 completed in order, no dependencies broken |
| Track post origin in database | Distinguish tool-created vs existing posts | ✓ Good — Implemented in Phase 02, origin field added to Post model |
| Client-side filtering for MVP | Simpler implementation, move to backend later | ⚠️ Revisit — Moved to server-side in Phase 03 for better performance |
| Infinite scroll for pagination | Better UX than manual page controls | ✓ Good — Implemented in Phase 03, 20 posts per page with loading indicator |
| WordPress REST API with rate limiting | Prevent API abuse and handle errors gracefully | ✓ Good — Implemented in Phase 02, exponential backoff works well |
| Cache WordPress posts in MongoDB with TTL | Reduce API calls and improve performance | ✓ Good — Implemented in Phase 04, 3-hour TTL with automatic expiration |
| Hybrid pagination (cache first, WordPress API fallback) | Balance performance with data freshness | ✓ Good — Implemented in Phase 04, search bypasses cache |
| Transform WordPress REST API responses in backend | Simplify frontend, provide table-ready data | ✓ Good — Implemented in Phase 05, categories, tags, formatted dates, edit URLs |
| Replace PostCard grid with table view | Better data density, standard UI pattern | ✓ Good — Implemented in Phase 06, table layout with search/sort/filter/pagination |
| Remove PostCard component and infinite scroll | Eliminate legacy code, simplify codebase | ✓ Good — Implemented in Phase 07, cleaner codebase with table view |
| Create verification documentation for all phases | Formal verification of requirements with evidence | ✓ Good — Implemented in Phases 8, 9, 10, 11, all requirements verified |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---

**Last updated:** 2026-04-20 (v1.4 milestone - Phase 18 complete)

</details>