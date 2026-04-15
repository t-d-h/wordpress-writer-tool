# WordPress Writer Tool

## What This Is

A full-stack AI content generation tool for WordPress sites. Users configure AI providers and WordPress sites, create projects with AI-assisted content pipelines (outlines, full articles, thumbnails, section images), and publish posts to WordPress. Backend is Python/FastAPI with MongoDB + Redis; frontend is React SPA.

## Core Value

Validate WordPress site connectivity and credentials before saving, so users know immediately if their site is configured correctly — not after wasting time creating content that can't be published.

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

### Active

- All Posts table view in ProjectDetail
- Table layout with columns: Title, URL, Categories, Tags, Date, Status, Actions
- Search by title functionality
- Sort by date/title/status functionality
- Status filter functionality
- Manual pagination (100 posts per page)
- Project-scoped WordPress site posts (no site selection)

## Current Milestone: v1.1 All Posts Table View

**Goal:** Replace the "All Posts" tab in ProjectDetail with a table view similar to /all-posts, keeping search/sort/filter functionality while using manual pagination.

**Target features:**
- Replace PostCard grid layout with table layout
- Use /all-posts columns: Title, URL, Categories, Tags, Date, Status, Actions
- Keep search by title functionality
- Keep sort by date/title/status functionality
- Keep status filter functionality
- Switch from infinite scroll to manual pagination (100 posts per page)
- Scope to project's WordPress site only (no site selection dropdown)
- Discard PostCard component usage in this tab
- Discard origin badges (not needed in table view)

## Current State

**Version:** v1.1 (in progress)

**Shipped Features (v1.0 MVP):**
- Token usage display with breakdown by post type
- WordPress REST API integration with search, filtering, and pagination
- All Posts tab UI with filter, sort, search, and infinite scroll
- Post origin tracking (tool-created vs existing)
- Post URL, categories, and tags display

**Completed in v1.1:**
- Backend API enhancement with caching, pagination, and search/sort
- Data transformation for WordPress REST API responses
- Frontend UI with table view, search, sort, filter, and pagination
- Cleanup of legacy PostCard component and infinite scroll
- Backend API verification (Phase 8 complete)
- Data transformation documentation (Phase 9 complete)
- Frontend UI verification (Phase 10 complete)
- Cleanup verification (Phase 11 complete)

**Next Milestone Goals:**
- All Posts table view with enhanced filtering
- Security improvements (credential encryption, input validation)
- Performance optimizations (caching, database indexes)
- Additional features (bulk operations, advanced filtering)

**Technical Debt:**
- 10 code review findings documented (2 critical, 5 warnings, 3 info)
- Plain-text credential storage (deferred)
- URL format validation gap (minor)

### Out of Scope

- Frontend UI toast styling — backend error details are sufficient for now
- Periodic re-validation of saved sites — validation only runs on site creation
- Token usage pagination — show all at once, note performance concern for later

## Context

This is a brownfield project with existing codebase mapped in `.planning/codebase/`. The system has a working AI content generation pipeline with job processing, WordPress integration, and project management. All three planned phases (Token Usage Display, WordPress Integration Backend, All Posts Tab UI) are now complete and shipped as v1.0 MVP.

**Current State:**
- 3 phases completed, 14 plans executed, 38 tasks delivered
- 16,329 lines of code added (Python + JavaScript/JSX)
- 8 days of development (2026-04-06 → 2026-04-14)
- UAT completed: 18/20 tests passed, 2 skipped (external dependencies)
- Code review: 10 findings (2 critical, 5 warnings, 3 info) — documented in 03-REVIEW.md

**Known Issues:**
- Plain-text credential storage (deferred for security milestone)
- URL format validation gap (minor, not blocking)
- No pre-save connectivity check (feature for future milestone)
- Code review findings documented but not yet fixed (can be addressed in v1.1)

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
*Last updated: 2026-04-15 after Phase 11 (Cleanup Verification) complete*
