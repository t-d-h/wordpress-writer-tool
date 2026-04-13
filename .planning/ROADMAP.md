# WordPress Writer Tool - Roadmap

**Milestone:** WP Site Validation + Auto-Pipeline
**Granularity:** standard
**Phases:** 2

## Goal

1. Validate WordPress site connectivity and credentials before saving, so users know immediately if their site is configured correctly -- not after wasting time creating content that can't be published.
2. Automate the content generation pipeline so users don't need to manually trigger each step after research completes.

## Phases

- [ ] **Phase 1: Site Validation Pipeline** - Validate URL format, connectivity, and API credentials before saving WordPress sites to MongoDB
- [ ] **Phase 2: Auto-Pipeline** - Automatically queue the entire content generation pipeline (outline, content, thumbnail, section images, publish) after research completes

## Phase Details

### Phase 1: Site Validation Pipeline
**Goal**: When a user submits a new WordPress site, the backend validates URL format, tests connectivity, and verifies API credentials -- only saving to MongoDB if all checks pass, otherwise returning specific error details
**Depends on**: Nothing (existing codebase is the foundation)
**Requirements**: VALID-01, VALID-02, VALID-03, VALID-04, VALID-05
**Success Criteria** (what must be TRUE):
  1. Submitting an invalid URL (missing http/https, malformed) returns an error and saves nothing to MongoDB
  2. Submitting a valid URL pointing to an unreachable WordPress site returns a connectivity error and saves nothing to MongoDB
  3. Submitting a reachable site with invalid username or API key returns a credential verification error and saves nothing to MongoDB
  4. Submitting a fully valid site (correct URL, reachable, valid credentials) saves successfully to MongoDB
  5. Every validation failure returns a specific error message identifying which check failed (URL, connectivity, or credentials)

**Plans**: 1 plan
**UI hint**: no (backend-only change)

Plan list:
- [ ] 02-01-PLAN.md — Implement automatic pipeline progression in task handlers

### Phase 2: Auto-Pipeline
**Goal**: After research completes, automatically run the entire content generation pipeline (outline, content, thumbnail, section images, publish) without manual user intervention
**Depends on**: Phase 1 (existing job system is the foundation)
**Requirements**: AUTO-01, AUTO-02, AUTO-03, AUTO-04, AUTO-05, AUTO-06, AUTO-07
**Success Criteria** (what must be TRUE):
  1. When a research job completes successfully, an outline job is automatically queued
  2. When an outline job completes successfully, a content job is automatically queued
  3. When a content job completes successfully, a thumbnail job is automatically queued
  4. When a thumbnail job completes successfully, a section images job is automatically queued
  5. When a section images job completes successfully, a publish job is automatically queued (if auto_publish is True)
  6. If any job fails, the pipeline stops and no subsequent jobs are queued
  7. If auto_publish is False, the pipeline stops after section images (no publish job queued)

**Plans**: TBD
**UI hint**: no (backend-only change)

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Site Validation Pipeline | 0/0 | Not started | - |
| 2. Auto-Pipeline | 0/1 | Not started | - |
