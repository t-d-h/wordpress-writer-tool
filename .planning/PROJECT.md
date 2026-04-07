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

### Active

- [ ] Backend validates WordPress site URL format (http/https) on creation
- [ ] Backend checks WordPress site is reachable (connectivity test) before saving
- [ ] Backend verifies username + API key credentials against WordPress REST API before saving
- [ ] Backend returns specific error details to frontend on validation failure
- [ ] Save is blocked if any validation step fails

### Out of Scope

- Frontend UI toast styling — backend error details are sufficient for now
- Periodic re-validation of saved sites — validation only runs on site creation

## Context

This is a brownfield project with existing codebase mapped in `.planning/codebase/`. The current `POST /api/wp-sites` endpoint accepts and stores WP site data with zero validation against the actual WordPress instance. Invalid URLs, unreachable sites, and bad credentials are only discovered when the user attempts to publish content. Known concerns include plain-text credential storage (deferred), URL format validation gap, and no pre-save connectivity check.

## Constraints

- **Tech stack**: Python/FastAPI backend, MongoDB, Redis, React frontend — these won't change for this project
- **MVP stage**: This is an early MVP; solutions should be pragmatic, not over-engineered
- **No app-level auth**: Relies on network-level isolation

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Backend-only validation with HTTP error responses | Keep it simple; frontend already handles API errors | — Pending |
| Test connectivity AND credentials on creation | User explicitly wants both checks | — Pending |
| Reject invalid URLs upfront | Catch obviously bad input before making network calls | — Pending |

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
*Last updated: 2026-04-07 after initialization*
