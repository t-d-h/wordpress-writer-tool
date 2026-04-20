# Phase 19: Admin Account Creation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-20
**Phase:** 19-admin-account-creation
**Areas discussed:** Username conflict handling, ADMIN_PASSWORD future

---

## Username conflict handling

| Option | Description | Selected |
|--------|-------------|----------|
| Allow 'admin' username | Allow INIT_USER to be 'admin'. Create one admin account with username 'admin' using INIT_PASSWORD. The existing create_admin_account() will be skipped because the account already exists. Simple and predictable. | |
| Prevent 'admin' username | Prevent INIT_USER from being 'admin'. Raise an error on startup if INIT_USER is 'admin'. This prevents confusion between the two admin accounts but adds complexity. | ✓ |
| Skip if 'admin' | Skip creation if INIT_USER is 'admin'. Let the existing create_admin_account() handle it using ADMIN_PASSWORD. INIT_USER/INIT_PASSWORD are ignored in this case. | |

**User's choice:** Prevent 'admin' username
**Notes:** User chose to prevent INIT_USER from being 'admin' and raise an error on startup. This prevents confusion between the two admin accounts (existing 'admin' using ADMIN_PASSWORD, and new initial admin using INIT_USER/INIT_PASSWORD).

---

## ADMIN_PASSWORD future

| Option | Description | Selected |
|--------|-------------|----------|
| Keep both fields | Keep both ADMIN_PASSWORD and INIT_PASSWORD as separate fields. ADMIN_PASSWORD serves the existing 'admin' account, INIT_PASSWORD serves the initial admin account creation. Both coexist for different purposes (per Phase 17 decision D-07, D-08, D-09). | ✓ |
| Deprecate ADMIN_PASSWORD | Deprecate ADMIN_PASSWORD. Remove it from config.py and only use INIT_PASSWORD. The existing create_admin_account() will be updated to use INIT_USER/INIT_PASSWORD instead of hardcoded values. | |
| Make ADMIN_PASSWORD optional | Make ADMIN_PASSWORD optional. Use INIT_PASSWORD if set, fall back to ADMIN_PASSWORD if INIT_PASSWORD is not set. This provides backward compatibility while allowing the new approach. | |

**User's choice:** Keep both fields
**Notes:** User chose to keep both ADMIN_PASSWORD and INIT_PASSWORD as separate fields. This aligns with Phase 17 decisions D-07, D-08, D-09 which said both fields should coexist for different purposes. ADMIN_PASSWORD serves the existing 'admin' account, INIT_PASSWORD serves the initial admin account creation.

---

## the agent's Discretion

None — all decisions were explicitly made by the user.

## Deferred Ideas

None — discussion stayed within phase scope.
