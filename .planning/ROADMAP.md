# WordPress Writer Tool - Roadmap

**Milestone:** WP Site Validation
**Granularity:** standard
**Phases:** 1

## Goal

Validate WordPress site connectivity and credentials before saving, so users know immediately if their site is configured correctly -- not after wasting time creating content that can't be published.

## Phases

- [ ] **Phase 1: Site Validation Pipeline** - Validate URL format, connectivity, and API credentials before saving WordPress sites to MongoDB

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

**Plans**: TBD
**UI hint**: yes

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Site Validation Pipeline | 0/0 | Not started | - |
