# Requirements

## Source

Active requirements from PROJECT.md (validated section), extracted on 2026-04-07.

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

- Frontend UI toast styling -- backend error details are sufficient for now
- Periodic re-validation of saved sites -- validation only runs on site creation

## Traceability

| Requirement ID | Description | Phase | Status |
|----------------|-------------|-------|--------|
| VALID-01 | Backend validates WordPress site URL format (http/https) on creation | Phase 1 | Pending |
| VALID-02 | Backend checks WordPress site is reachable (connectivity test) before saving | Phase 1 | Pending |
| VALID-03 | Backend verifies username + API key credentials against WordPress REST API before saving | Phase 1 | Pending |
| VALID-04 | Backend returns specific error details to frontend on validation failure | Phase 1 | Pending |
| VALID-05 | Save is blocked if any validation step fails | Phase 1 | Pending |

## Coverage

**Mapped**: 5/5 (100%)
**Orphaned**: 0
**Duplicated**: 0
