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
- [ ] Research job automatically queues outline job on successful completion
- [ ] Outline job automatically queues content job on successful completion
- [ ] Content job automatically queues thumbnail job on successful completion
- [ ] Thumbnail job automatically queues section images job on successful completion
- [ ] Section images job automatically queues publish job on successful completion (if auto_publish is enabled)
- [ ] Pipeline stops if any job fails (does not queue next job)
- [ ] Pipeline respects auto_publish flag (stops before publish if False)

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
| AUTO-01 | Research job automatically queues outline job on successful completion | Phase 2 | Pending |
| AUTO-02 | Outline job automatically queues content job on successful completion | Phase 2 | Pending |
| AUTO-03 | Content job automatically queues thumbnail job on successful completion | Phase 2 | Pending |
| AUTO-04 | Thumbnail job automatically queues section images job on successful completion | Phase 2 | Pending |
| AUTO-05 | Section images job automatically queues publish job on successful completion (if auto_publish is enabled) | Phase 2 | Pending |
| AUTO-06 | Pipeline stops if any job fails (does not queue next job) | Phase 2 | Pending |
| AUTO-07 | Pipeline respects auto_publish flag (stops before publish if False) | Phase 2 | Pending |

## Coverage

**Mapped**: 12/12 (100%)
**Orphaned**: 0
**Duplicated**: 0
