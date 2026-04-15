---
phase: 12
slug: backend-foundation
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-15
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | backend/pytest.ini (Wave 0 installs) |
| **Quick run command** | `pytest backend/tests/test_post_models.py -v` |
| **Full suite command** | `pytest backend/tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest backend/tests/test_post_models.py -v`
- **After every plan wave:** Run `pytest backend/tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | LANG-03 | — | N/A | unit | `pytest backend/tests/test_post_models.py::test_language_field_validation -v` | ✅ W0 | ⬜ pending |
| 12-01-02 | 01 | 1 | LANG-03 | — | N/A | unit | `pytest backend/tests/test_post_models.py::test_language_field_default -v` | ✅ W0 | ⬜ pending |
| 12-01-03 | 01 | 1 | LANG-08 | — | Rejects invalid language values | unit | `pytest backend/tests/test_post_models.py::test_invalid_language_rejected -v` | ✅ W0 | ⬜ pending |
| 12-01-04 | 01 | 1 | LANG-09 | — | Defaults to "english" for missing field | unit | `pytest backend/tests/test_post_models.py::test_backward_compatibility_default -v` | ✅ W0 | ⬜ pending |
| 12-01-05 | 01 | 1 | LANG-09 | — | No errors when querying posts without language | integration | `pytest backend/tests/test_posts_router.py::test_query_posts_without_language -v` | ✅ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `backend/tests/test_post_models.py` — stubs for LANG-03, LANG-08, LANG-09 (created in Plan 01)
- [x] `backend/tests/conftest.py` — shared fixtures for MongoDB and test data (created in Plan 01)
- [x] `pytest` installation — if no framework detected (added in Plan 01)
- [x] `pytest-asyncio` installation — for async test support (added in Plan 01)

*Wave 0 complete: Plan 01 creates all test infrastructure before dependent tasks execute.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| API returns 400 error with clear message for invalid language | LANG-08 | Requires HTTP client to test error response | 1. Start backend server 2. Send POST /posts with invalid language 3. Verify 400 status and error message |
| API responses default to "english" for posts without language field | LANG-09 | Requires existing post data without language field | 1. Query existing posts from MongoDB 2. Verify language field defaults to "english" in response |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-15
