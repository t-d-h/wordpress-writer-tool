# Roadmap

**Project:** WordPress Writer Tool
**Last Updated:** 2026-04-20

## Milestones

- ✅ **v1.0 MVP** — Phases 1-3 (shipped 2026-04-14)
- ✅ **v1.1 All Posts Table View** — Phases 4-11 (shipped 2026-04-15)
- ✅ **v1.2 Vietnamese Language Support** — Phases 12-14 (shipped 2026-04-16)
- ✅ **v1.3 Content Quality Improvements** — Phases 15-16 (shipped 2026-04-17)
- 🔄 **v1.4 Initial Admin Account on First Startup** — Phases 17-20 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-3) — SHIPPED 2026-04-14</summary>

- [x] Phase 1: Token Usage Display (4/4 plans) — completed 2026-04-14
- [x] Phase 2: WordPress Integration Backend (3/3 plans) — completed 2026-04-14
- [x] Phase 3: All Posts Tab UI (7/7 plans) — completed 2026-04-14

</details>

<details>
<summary>✅ v1.1 All Posts Table View (Phases 4-11) — SHIPPED 2026-04-15</summary>

- [x] Phase 4: Backend API Enhancement (3/3 plans) — completed 2026-04-15
- [x] Phase 5: Data Transformation (1/1 plan) — completed 2026-04-15
- [x] Phase 6: Frontend UI (3/3 plans) — completed 2026-04-15
- [x] Phase 7: Cleanup (3/3 plans) — completed 2026-04-15
- [x] Phase 8: Backend API Verification (1/1 plan) — completed 2026-04-15
- [x] Phase 9: Data Transformation Documentation (1/1 plan) — completed 2026-04-15
- [x] Phase 10: Frontend UI Verification (1/1 plan) — completed 2026-04-15
- [x] Phase 11: Cleanup Verification (1/1 plan) — completed 2026-04-15

</details>

<details>
<summary>✅ v1.2 Vietnamese Language Support (Phases 12-14) — SHIPPED 2026-04-16</summary>

- [x] Phase 12: Backend Foundation (3/3 plans) — completed 2026-04-15
- [x] Phase 13: AI Service Integration (3/3 plans) — completed 2026-04-15
- [x] Phase 14: Frontend UI (6/6 plans) — completed 2026-04-16

</details>

<details>
<summary>✅ v1.3 Content Quality Improvements (Phases 15-16) — SHIPPED 2026-04-17</summary>

- [x] Phase 15: HTML Cleaning Foundation (2/2 plans) — completed 2026-04-16
- [x] Phase 16: Word Count Validation (1/1 plan) — completed 2026-04-17

</details>

<details>
<summary>🔄 v1.4 Initial Admin Account on First Startup (Phases 17-20) — IN PROGRESS</summary>

  - [x] Phase 17: Configuration Layer (1 plan) — planned (completed 2026-04-20)
  - [x] Phase 18: Environment Variable Validation (1 plan) — planned (completed 2026-04-20)
  - [x] Phase 19: Admin Account Creation (1 plan) — planned (completed 2026-04-20)
  - [ ] Phase 20: MongoDB Storage Integration (TBD plans) — not started

</details>

## Phase Details

### Phase 17: Configuration Layer
**Goal**: Update config.py to include INIT_USER and INIT_PASSWORD fields with default values
**Depends on**: Nothing (first phase of v1.4)
**Requirements**: CONFIG-01, CONFIG-02, CONFIG-03
**Success Criteria** (what must be TRUE):
  1. config.py includes INIT_USER field with default value
  2. config.py includes INIT_PASSWORD field with default value
  3. config.py validates INIT_USER and INIT_PASSWORD on startup
  4. System loads INIT_USER from environment variable or uses default
  5. System loads INIT_PASSWORD from environment variable or uses default
**Plans**: 1 plan
- [x] 17-01-PLAN.md — Add INIT_USER and INIT_PASSWORD fields to config.py with validation on startup

### Phase 18: Environment Variable Validation
**Goal**: Validate environment variables with error logging and fail-fast behavior
**Depends on**: Phase 17
**Requirements**: CONF-01, CONF-02, CONF-03, CONF-04, CONF-05
**Success Criteria** (what must be TRUE):
  1. System reads INIT_USER environment variable for admin username
  2. System reads INIT_PASSWORD environment variable for admin password
  3. System validates that INIT_USER is provided (non-empty string)
  4. System validates that INIT_PASSWORD is provided (non-empty string)
  5. System fails fast if INIT_USER or INIT_PASSWORD are missing or empty (no default values)
  6. System logs error when INIT_USER or INIT_PASSWORD are missing
  7. System does not log when environment variables are successfully loaded
**Plans**: 1 plan
- [x] 18-01-PLAN.md — Add error logging to validate() method and update CONF-05 requirement

### Phase 19: Admin Account Creation
**Goal**: Create admin account on first startup with idempotent behavior
**Depends on**: Phase 18
**Requirements**: ADMIN-01, ADMIN-02, ADMIN-03, IDEMP-01, IDEMP-02, IDEMP-03
**Success Criteria** (what must be TRUE):
  1. System creates admin account on first application startup
  2. Admin account uses username from INIT_USER environment variable
  3. Admin account uses password from INIT_PASSWORD environment variable
  4. System checks if admin account already exists before creating
  5. System handles container restarts gracefully without duplicate key errors
  6. System logs when admin account already exists (skip creation)
**Plans**: 1 plan
- [x] 19-01-PLAN.md — Update create_admin_account() to use INIT_USER and INIT_PASSWORD with idempotent behavior

### Phase 20: MongoDB Storage Integration
**Goal**: Store admin account in MongoDB with proper schema and uniqueness constraints
**Depends on**: Phase 19
**Requirements**: MONGO-01, MONGO-02, MONGO-03
**Success Criteria** (what must be TRUE):
  1. System stores admin account in MongoDB users collection
  2. System uses existing users collection schema for admin account
  3. System ensures username uniqueness in users collection
  4. Admin account persists across application restarts
  5. MongoDB unique index prevents duplicate usernames
**Plans**: 1 plan
- [ ] 20-01-PLAN.md — Create automated test suite to verify MongoDB storage integration (MONGO-01, MONGO-02, MONGO-03)

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Token Usage Display | v1.0 | 4/4 | Complete | 2026-04-14 |
| 2. WordPress Integration Backend | v1.0 | 3/3 | Complete | 2026-04-14 |
| 3. All Posts Tab UI | v1.0 | 7/7 | Complete | 2026-04-14 |
| 4. Backend API Enhancement | v1.1 | 3/3 | Complete | 2026-04-15 |
| 5. Data Transformation | v1.1 | 1/1 | Complete | 2026-04-15 |
| 6. Frontend UI | v1.1 | 3/3 | Complete | 2026-04-15 |
| 7. Cleanup | v1.1 | 3/3 | Complete | 2026-04-15 |
| 8. Backend API Verification | v1.1 | 1/1 | Complete | 2026-04-15 |
| 9. Data Transformation Documentation | v1.1 | 1/1 | Complete | 2026-04-15 |
| 10. Frontend UI Verification | v1.1 | 1/1 | Complete | 2026-04-15 |
| 11. Cleanup Verification | v1.1 | 1/1 | Complete | 2026-04-15 |
| 12. Backend Foundation | v1.2 | 3/3 | Complete | 2026-04-15 |
| 13. AI Service Integration | v1.2 | 3/3 | Complete | 2026-04-15 |
| 14. Frontend UI | v1.2 | 6/6 | Complete | 2026-04-16 |
 | 15. HTML Cleaning Foundation | v1.3 | 2/2 | Complete | 2026-04-16 |
 | 16. Word Count Validation | v1.3 | 1/1 | Complete | 2026-04-17 |
   | 17. Configuration Layer | v1.4 | 1/1 | Complete | 2026-04-20 |
   | 18. Environment Variable Validation | v1.4 | 1/1 | Planned | — |
   | 19. Admin Account Creation | v1.4 | 0/1 | Planned | — |
   | 20. MongoDB Storage Integration | v1.4 | 0/1 | Planned | — |

---

**See `.planning/milestones/v1.0-ROADMAP.md` for full v1.0 milestone details.**
**See `.planning/milestones/v1.1-ROADMAP.md` for full v1.1 milestone details.**
**See `.planning/milestones/v1.2-ROADMAP.md` for full v1.2 milestone details.**
**See `.planning/milestones/v1.3-ROADMAP.md` for full v1.3 milestone details.**
