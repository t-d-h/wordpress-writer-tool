---
phase: 17
slug: backend-authentication-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-18
---

# Phase 17 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | backend/pytest.ini (existing) |
| **Quick run command** | `pytest backend/tests/test_auth.py -v` |
| **Full suite command** | `pytest backend/tests/ -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest backend/tests/test_auth.py -v`
- **After every plan wave:** Run `pytest backend/tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 17-01-01 | 01 | 1 | AUTH-01 | T-17-01 | Login returns valid JWT token | integration | `pytest backend/tests/test_auth.py::test_login_success -v` | ❌ W0 | ⬜ pending |
| 17-01-02 | 01 | 1 | AUTH-02 | T-17-02 | JWT token contains required claims | unit | `pytest backend/tests/test_auth.py::test_jwt_claims -v` | ❌ W0 | ⬜ pending |
| 17-01-03 | 01 | 1 | AUTH-03 | T-17-03 | Token validation rejects invalid tokens | integration | `pytest backend/tests/test_auth.py::test_token_validation_invalid -v` | ❌ W0 | ⬜ pending |
| 17-01-04 | 01 | 1 | AUTH-04 | T-17-04 | Token validation rejects expired tokens | integration | `pytest backend/tests/test_auth.py::test_token_validation_expired -v` | ❌ W0 | ⬜ pending |
| 17-01-05 | 01 | 1 | AUTH-06 | T-17-05 | Passwords hashed with Argon2id | unit | `pytest backend/tests/test_auth.py::test_password_hashing -v` | ❌ W0 | ⬜ pending |
| 17-01-06 | 01 | 1 | SEC-05 | T-17-06 | JWT signed with SECRET_KEY env var | unit | `pytest backend/tests/test_auth.py::test_jwt_signing -v` | ❌ W0 | ⬜ pending |
| 17-01-07 | 01 | 1 | SEC-06 | T-17-07 | Token expiration uses ACCESS_TOKEN_EXPIRE_MINUTES | unit | `pytest backend/tests/test_auth.py::test_token_expiration -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_auth.py` — stubs for AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-06, SEC-05, SEC-06
- [ ] `backend/tests/conftest.py` — shared fixtures (existing)
- [ ] `pytest` — framework already installed

*Existing infrastructure covers all phase requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SECRET_KEY environment variable validation | SEC-05 | Requires environment setup | Set SECRET_KEY in .env, verify JWT signing works |
| ACCESS_TOKEN_EXPIRE_MINUTES configuration | SEC-06 | Requires environment setup | Set ACCESS_TOKEN_EXPIRE_MINUTES in .env, verify token expiration |

*All phase behaviors have automated verification except environment configuration.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
