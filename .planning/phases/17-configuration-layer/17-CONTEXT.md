# Phase 17: Configuration Layer - Context

**Gathered:** 2026-04-20
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers configuration infrastructure for initial admin account setup — adding INIT_USER and INIT_PASSWORD fields to config.py with validation on startup. These fields are separate from the existing ADMIN_PASSWORD field, which serves a different admin user.

</domain>

<decisions>
## Implementation Decisions

### Default Values
- **D-01:** INIT_USER and INIT_PASSWORD are separate users from ADMIN_PASSWORD — both required for first startup
- **D-02:** No default values for INIT_USER or INIT_PASSWORD — both must be set via environment variables
- **D-03:** System fails startup if INIT_USER or INIT_PASSWORD are missing or empty

### Validation Approach
- **D-04:** Validation happens in config.py (Settings class or validate() method)
- **D-05:** Validation raises ValueError with clear error messages if INIT_USER or INIT_PASSWORD are missing/empty
- **D-06:** Fails fast — validation runs immediately on Settings instantiation

### ADMIN_PASSWORD Relationship
- **D-07:** Keep both ADMIN_PASSWORD and INIT_PASSWORD as separate fields
- **D-08:** ADMIN_PASSWORD serves existing admin user, INIT_PASSWORD serves initial admin account creation
- **D-09:** No deprecation or replacement — both fields coexist for different purposes

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — CONFIG-01, CONFIG-02, CONFIG-03 requirements for configuration layer

### Phase Specification
- `.planning/ROADMAP.md` — Phase 17 success criteria and dependencies

### Existing Configuration
- `backend/app/config.py` — Current Settings class with ADMIN_PASSWORD field and os.getenv() pattern

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/config.py` — Settings class with type annotations and os.getenv() pattern
- Existing pattern: `FIELD_NAME: str = os.getenv("ENV_VAR", "default_value")`

### Established Patterns
- Environment variable loading via `os.getenv()` with default values
- Settings class with type annotations for all configuration fields
- No validation currently happens on startup — this is new behavior

### Integration Points
- `backend/app/main.py` — Application entry point that instantiates Settings
- Future phases will use INIT_USER and INIT_PASSWORD for admin account creation (Phase 19)

</code_context>

<specifics>
## Specific Ideas

- INIT_USER and INIT_PASSWORD are for initial admin account creation on first startup
- ADMIN_PASSWORD is for a different admin user (existing field)
- Both fields must be set via environment variables — no defaults allowed
- Validation should fail fast with clear error messages

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 17-configuration-layer*
*Context gathered: 2026-04-20*
