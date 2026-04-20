# Phase 19: Admin Account Creation - Context

**Gathered:** 2026-04-20
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers admin account creation on first startup using INIT_USER and INIT_PASSWORD environment variables, with idempotent behavior to handle container restarts gracefully. The system checks if the admin account already exists before creating, logs when it already exists, and prevents username conflicts with the existing 'admin' account.

</domain>

<decisions>
## Implementation Decisions

### Username Conflict Handling
- **D-01:** Prevent INIT_USER from being 'admin' — raise an error on startup if INIT_USER is 'admin'
- **D-02:** This prevents confusion between the two admin accounts (existing 'admin' using ADMIN_PASSWORD, and new initial admin using INIT_USER/INIT_PASSWORD)
- **D-03:** Error message should be clear: "INIT_USER cannot be 'admin' — this username is reserved for the existing admin account"

### ADMIN_PASSWORD Future (Carried Forward from Phase 17)
- **D-04:** Keep both ADMIN_PASSWORD and INIT_PASSWORD as separate fields
- **D-05:** ADMIN_PASSWORD serves existing admin user (username 'admin'), INIT_PASSWORD serves initial admin account creation
- **D-06:** No deprecation or replacement — both fields coexist for different purposes (per Phase 17 D-07, D-08, D-09)

### Function Approach
- **D-07:** Update the existing create_admin_account() function to use INIT_USER and INIT_PASSWORD instead of hardcoded 'admin' and ADMIN_PASSWORD
- **D-08:** Keep the function name the same for consistency — it's already called in main.py startup event
- **D-09:** Add validation to prevent INIT_USER from being 'admin' before attempting to create the account

### Idempotent Behavior
- **D-10:** System checks if admin account already exists before creating (query users_col by username)
- **D-11:** System handles container restarts gracefully without duplicate key errors (unique index on username prevents duplicates)
- **D-12:** System logs when admin account already exists (skip creation) — use logger.info() for this scenario

### Logging Behavior
- **D-13:** Log when admin account is created (logger.info())
- **D-14:** Log when admin account already exists and creation is skipped (logger.info())
- **D-15:** Log error when INIT_USER is 'admin' (logger.error() before raising ValueError)

### Password Handling
- **D-16:** Use existing hash_password() function from auth_service to hash INIT_PASSWORD before storing
- **D-17:** Store password_hash in users collection (not plain text password)
- **D-18:** User schema includes: username, password_hash, role, created_at, last_login_at

### Error Handling
- **D-19:** Raise ValueError with clear error message if INIT_USER is 'admin'
- **D-20:** Raise ValueError if username already exists (existing behavior from create_user())
- **D-21:** Log errors before raising exceptions for debugging

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — ADMIN-01, ADMIN-02, ADMIN-03, IDEMP-01, IDEMP-02, IDEMP-03 requirements for admin account creation

### Phase Specification
- `.planning/ROADMAP.md` — Phase 19 success criteria and dependencies

### Prior Phase Context
- `.planning/phases/17-configuration-layer/17-CONTEXT.md` — Phase 17 decisions on configuration layer and ADMIN_PASSWORD relationship
- `.planning/phases/18-environment-variable-validation/18-CONTEXT.md` — Phase 18 decisions on fail-fast validation and error logging

### Existing User System
- `backend/app/models/user.py` — UserCreate, UserUpdate, UserResponse models with validation
- `backend/app/services/user_service.py` — create_admin_account(), create_user(), hash_password() functions
- `backend/app/routers/users.py` — User management endpoints
- `backend/app/database.py` — users_col collection with unique index on username

### Existing Configuration
- `backend/app/config.py` — INIT_USER and INIT_PASSWORD fields with validation
- `backend/app/main.py` — Startup event that calls create_admin_account()

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/services/user_service.py` — create_admin_account() function (currently uses hardcoded 'admin' and ADMIN_PASSWORD)
- `backend/app/services/auth_service.py` — hash_password() function for password hashing
- `backend/app/database.py` — users_col collection with unique index on username (prevents duplicates)
- `backend/app/models/user.py` — UserCreate model with validation (username min 3 chars, password min 8 chars, role validation)

### Established Patterns
- User creation via create_user() function with password hashing
- Idempotent behavior — check if exists before creating
- Error handling via ValueError with clear messages
- Logging via logger.info() for informational messages, logger.error() for errors
- Startup initialization via @app.on_event("startup") in main.py

### Integration Points
- `backend/app/main.py` — Startup event that calls create_admin_account()
- `backend/app/services/user_service.py` — create_admin_account() function to be updated
- `backend/app/config.py` — INIT_USER and INIT_PASSWORD fields to be used
- `backend/app/database.py` — users_col collection for storing admin account

</code_context>

<specifics>
## Specific Ideas

- INIT_USER and INIT_PASSWORD are for initial admin account creation on first startup
- ADMIN_PASSWORD is for the existing 'admin' user (separate account)
- Both fields must be set via environment variables — no defaults allowed
- Prevent INIT_USER from being 'admin' to avoid confusion
- Update existing create_admin_account() function to use INIT_USER/INIT_PASSWORD
- Log when account is created or when it already exists
- Use existing password hashing infrastructure (hash_password from auth_service)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 19-admin-account-creation*
*Context gathered: 2026-04-20*
