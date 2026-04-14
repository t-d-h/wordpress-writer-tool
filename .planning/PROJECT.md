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

### Active

- [ ] Display token usage breakdown in Project general tab (above statistics)
  - Show breakdown by post type: research, outline, content, thumbnail
  - Show total input tokens and total output tokens
  - Include deleted posts in calculations
  - Always visible, calculate on-the-fly from posts collection
- [ ] Add "All Posts" tab to each project
  - Show all WordPress posts (both tool-created and existing)
  - Visual distinction between post types
  - Edit button opens WordPress admin in new tab
  - Filter by status, sort by date, search by title
  - Add WordPress API method to fetch all posts
  - Track post origin in database

### Out of Scope

- Frontend UI toast styling — backend error details are sufficient for now
- Periodic re-validation of saved sites — validation only runs on site creation
- Token usage pagination — show all at once, note performance concern for later

## Context

This is a brownfield project with existing codebase mapped in `.planning/codebase/`. The system has a working AI content generation pipeline with job processing, WordPress integration, and project management. Current concerns include plain-text credential storage (deferred), URL format validation gap, no pre-save connectivity check, and missing token usage aggregation display.

## Constraints

- **Tech stack**: Python/FastAPI backend, MongoDB, Redis, React frontend — these won't change for this project
- **MVP stage**: This is an early MVP; solutions should be pragmatic, not over-engineered
- **No app-level auth**: Relies on network-level isolation

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Token usage calculated on-the-fly | No caching needed for MVP, simpler implementation | — Pending |
| Include deleted posts in token totals | Users want complete cost visibility | — Pending |
| Build features sequentially | Token usage first, then All Posts tab | — Pending |
| Track post origin in database | Distinguish tool-created vs existing posts | — Pending |

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
*Last updated: 2026-04-14 after initialization*
