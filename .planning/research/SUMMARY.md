# Project Research Summary

**Project:** WordPress Writer Tool - Token Usage & All Posts Features
**Domain:** AI content generation and WordPress integration
**Researched:** 2026-04-14
**Confidence:** HIGH

## Executive Summary

The WordPress Writer Tool is an AI-powered content generation system that integrates with WordPress sites via REST API. Experts build this type of product using a layered architecture with clear separation between frontend (React SPA), backend (FastAPI), and external integrations (WordPress REST API, AI providers). The recommended approach for the new features leverages existing patterns: MongoDB aggregation for on-demand token usage calculations and a service layer for WordPress API integration, with TanStack Table for the frontend post listing.

The research indicates both features can be built using established patterns in the codebase without requiring architectural changes. Token usage aggregation uses MongoDB's native aggregation framework (no new dependencies), while the All Posts tab extends the existing WordPress REST API integration with a new merge service. Key risks include WordPress API rate limiting, credential exposure in logs, and inconsistent post data between systems—all mitigated by following existing error handling patterns, implementing proper logging hygiene, and using origin tracking for data consistency.

## Key Findings

### Recommended Stack

The research confirms the existing stack is appropriate for both features. No major framework changes are needed—only one new frontend dependency for the All Posts tab.

**Core technologies:**
- **FastAPI 0.115.0**: Backend REST API framework — already in use, async support, Pydantic validation
- **React 18.3.1**: Frontend UI framework — already in use, functional components, hooks
- **MongoDB 7+**: Data store — already in use, aggregation framework for token usage
- **Redis 5.0.0**: Pub/sub messaging — already in use, job processing

**New additions:**
- **TanStack Table 8.20+**: Headless table component — industry standard for React tables in 2025, full control over markup/styles
- **MongoDB Aggregation Framework**: Native token calculation — built-in `$group` and `$sum` operators, no additional libraries needed
- **WordPress REST API**: Post listing — built-in filtering, sorting, searching, pagination

**Optional (defer to v2+):**
- **Recharts 2.12+**: Token usage visualization — only if charts needed later; simple display uses HTML/CSS
- **date-fns 3.6+**: Date formatting — for post date display in All Posts tab

### Expected Features

**Must have (table stakes):**
- **Token usage breakdown by type** — users expect to see research, outline, content, and thumbnail token costs
- **Total token count** — users need to understand overall AI usage costs
- **Post listing with filtering** — users expect to filter by status (publish, draft, pending)
- **Search by title** — users need to find specific posts quickly
- **Sort by date** — users expect chronological ordering

**Should have (competitive):**
- **Visual distinction by origin** — differentiator: clearly mark tool-created vs existing WordPress posts
- **Merged view of tool + WordPress posts** — differentiator: single unified view instead of separate lists
- **Edit button to WordPress admin** — differentiator: seamless workflow for editing published posts

**Defer (v2+):**
- **Input/output token separation** — current model only tracks total per type; requires AI provider API changes
- **Charts/visualizations** — simple HTML/CSS display sufficient for MVP; can add Recharts later
- **Advanced filtering** — date ranges, multiple status filters, category filtering not essential for launch
- **Post origin persistence** — can be computed on-the-fly via wp_post_id matching

### Architecture Approach

The existing layered architecture provides a solid foundation. Both features follow established patterns: MongoDB aggregation for on-demand calculations, service layer for external API integration, and data merging with origin tracking.

**Major components:**
1. **Frontend Layer (React)** — ProjectDetail.jsx with new tabs (General for token usage, All Posts for post listing), TokenUsageDisplay component, AllPostsTab component with TanStack Table
2. **API Client Layer** — client.js with getProjectTokenUsage() and getProjectAllPosts() methods
3. **Backend Router Layer** — projects.py with GET /api/projects/{id}/token-usage and GET /api/projects/{id}/all-posts endpoints
4. **Backend Service Layer** — token_usage_service.py (new) for MongoDB aggregation, post_merge_service.py (new) for merging tool and WordPress posts, wp_service.py (extended) for WordPress REST API calls
5. **Database Layer** — MongoDB posts collection with token_usage field, wp_sites collection for credentials

**Key patterns:**
- MongoDB aggregation pipeline for on-demand token calculations
- Service layer isolation for external API integration
- Data merging with origin tracking (tool/existing/both)
- Client-side filtering/sorting for MVP simplicity

### Critical Pitfalls

**Top 5 pitfalls with prevention strategies:**

1. **WordPress API rate limiting** — implement exponential backoff, respect 429 responses, add rate limiting headers
2. **Credential exposure in logs** — never log WordPress credentials, use redacted logging, audit all print statements
3. **Inconsistent post data between systems** — use origin tracking (wp_post_id matching), handle missing fields gracefully, validate data structure
4. **Token usage calculation errors** — handle missing token_usage fields, default to zero, validate aggregation pipeline
5. **Pagination edge cases** — handle empty results, respect WordPress API limits, implement proper page boundaries

**Moderate risks:**
- Performance at scale (10K+ posts) — add Redis caching later if needed
- Date/time zone issues — use UTC consistently, display in user's timezone
- Empty state handling — show helpful messages when no posts exist

**Minor risks:**
- Accessibility concerns — follow ARIA patterns for table, keyboard navigation
- Bundle size — TanStack Table is lightweight, defer Recharts to v2+

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Token Usage Display
**Rationale:** Independent feature with no dependencies, builds on existing MongoDB aggregation patterns, quick win for users
**Delivers:** Token usage breakdown by type (research, outline, content, thumbnail), total token count, per-project aggregation
**Addresses:** Token usage breakdown (table stakes), total token count (table stakes)
**Avoids:** Token usage calculation errors (pitfall #4)
**Uses:** MongoDB Aggregation Framework, Motor 3.6.0, Pydantic 2.9.0
**Implements:** token_usage_service.py, TokenUsageDisplay.jsx component

### Phase 2: All Posts Tab
**Rationale:** Depends on existing wp_service.py integration, builds on WordPress REST API patterns, provides core post management functionality
**Delivers:** Post listing with filtering, search by title, sort by date, visual distinction by origin, edit button to WordPress admin
**Addresses:** Post listing with filtering (table stakes), search by title (table stakes), sort by date (table stakes), visual distinction by origin (differentiator), merged view (differentiator)
**Avoids:** WordPress API rate limiting (pitfall #1), credential exposure in logs (pitfall #2), inconsistent post data (pitfall #3)
**Uses:** TanStack Table 8.20+, httpx >=0.28.1, WordPress REST API
**Implements:** post_merge_service.py, AllPostsTab.jsx component with TanStack Table

### Phase 3: Post Origin Tracking (Optional)
**Rationale:** Enhances data consistency, optional for MVP since origin can be computed on-the-fly
**Delivers:** Persisted origin field in posts collection, improved merge accuracy, origin-based filtering
**Addresses:** Inconsistent post data between systems (pitfall #3)
**Uses:** MongoDB schema update, post_merge_service.py extension
**Implements:** Database migration, origin persistence on post creation

### Phase Ordering Rationale

- **Why this order based on dependencies:** Phase 1 is independent and can be built in parallel. Phase 2 depends on existing wp_service.py but not on Phase 1. Phase 3 depends on Phase 2's merge logic.
- **Why this grouping based on architecture patterns:** Phase 1 follows MongoDB aggregation pattern (backend-heavy). Phase 2 follows service layer + external API pattern (full-stack). Phase 3 is an optional enhancement to data consistency.
- **How this avoids pitfalls from research:** Phase 1 avoids calculation errors by using proven aggregation patterns. Phase 2 avoids rate limiting and credential exposure by extending existing wp_service.py with proper error handling. Phase 3 addresses data consistency issues by persisting origin.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** WordPress API rate limiting behavior varies by hosting provider; may need to test with real WordPress sites during implementation
- **Phase 2:** WordPress REST API response structure can vary by plugin/theme; need to handle edge cases in merge logic

Phases with standard patterns (skip research-phase):
- **Phase 1:** MongoDB aggregation is well-documented with established patterns; no additional research needed
- **Phase 3:** Database schema updates are straightforward; origin tracking logic is clearly defined

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified with official MongoDB, TanStack Table, and WordPress REST API documentation |
| Features | HIGH | Based on existing codebase patterns and user expectations for content management tools |
| Architecture | HIGH | Analyzed existing codebase; patterns are well-established and documented |
| Pitfalls | HIGH | Identified from WordPress REST API documentation and common integration issues |

**Overall confidence:** HIGH

### Gaps to Address

- **WordPress API rate limiting specifics:** Different hosting providers have different rate limits; implement exponential backoff and test with real sites during Phase 2
- **WordPress REST API response variability:** Plugins and themes can modify post structure; add defensive coding and field validation in merge logic
- **Token usage input/output separation:** Current model only tracks total per type; requires AI provider API changes for input/output breakdown (defer to v2+)

## Sources

### Primary (HIGH confidence)
- MongoDB Aggregation Pipeline Documentation — https://www.mongodb.com/docs/manual/core/aggregation-pipeline/
- MongoDB $group Operator Documentation — https://www.mongodb.com/docs/manual/reference/operator/aggregation/group/
- MongoDB $sum Operator Documentation — https://www.mongodb.com/docs/manual/reference/operator/aggregation/sum/
- TanStack Table Official Documentation — https://tanstack.com/table/latest/docs/introduction
- TanStack Table Quick Start Guide — https://tanstack.com/table/latest/docs/guide/quick-start
- WordPress REST API Posts Reference — https://developer.wordpress.org/rest-api/reference/posts/
- WordPress REST API Authentication — https://developer.wordpress.org/rest-api/using-the-rest-api/authentication/
- WordPress REST API Global Parameters — https://developer.wordpress.org/rest-api/using-the-rest-api/global-parameters/

### Secondary (MEDIUM confidence)
- Recharts Official Documentation — https://recharts.org/ (for future consideration)
- Existing codebase analysis — backend/requirements.txt, frontend/package.json, backend/app/services/wp_service.py, backend/app/models/post.py, frontend/src/components/Projects/ProjectDetail.jsx

### Tertiary (LOW confidence)
- None — all findings verified with primary sources

---
*Research completed: 2026-04-14*
*Ready for roadmap: yes*
