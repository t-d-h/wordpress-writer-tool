# Requirements

**Project:** WordPress Writer Tool
**Milestone:** v1.4 Initial Admin Account on First Startup
**Last Updated:** 2026-04-20

## Milestone v1.4 Requirements

### Configuration (CONF)

- [ ] **CONF-01**: System reads INIT_USER environment variable for admin username
- [ ] **CONF-02**: System reads INIT_PASSWORD environment variable for admin password
- [ ] **CONF-03**: System validates that INIT_USER is provided (non-empty string)
- [ ] **CONF-04**: System validates that INIT_PASSWORD is provided (non-empty string)
- [ ] **CONF-05**: System provides sensible default values if environment variables are missing

### Admin Account Creation (ADMIN)

- [ ] **ADMIN-01**: System creates admin account on first application startup
- [ ] **ADMIN-02**: Admin account uses username from INIT_USER environment variable
- [ ] **ADMIN-03**: Admin account uses password from INIT_PASSWORD environment variable

### Idempotent Initialization (IDEMP)

- [ ] **IDEMP-01**: System checks if admin account already exists before creating
- [ ] **IDEMP-02**: System handles container restarts gracefully without duplicate key errors
- [ ] **IDEMP-03**: System logs when admin account already exists (skip creation)

### MongoDB Storage (MONGO)

- [ ] **MONGO-01**: System stores admin account in MongoDB users collection
- [ ] **MONGO-02**: System uses existing users collection schema for admin account
- [ ] **MONGO-03**: System ensures username uniqueness in users collection

### Configuration File Updates (CONFIG)

- [ ] **CONFIG-01**: config.py includes INIT_USER field with default value
- [ ] **CONFIG-02**: config.py includes INIT_PASSWORD field with default value
- [ ] **CONFIG-03**: config.py validates INIT_USER and INIT_PASSWORD on startup

## Future Requirements

Deferred to future milestones:

- Admin role assignment and permissions
- Interactive credential prompt when environment variables not provided
- Password hashing integration with existing Argon2id infrastructure
- JWT token integration with existing authentication system
- Service layer updates to use environment variables
- Testing and validation of admin account creation
- Documentation of required environment variables

## Out of Scope

Explicitly excluded from this milestone:

- User authentication and login functionality (already implemented in previous v1.4 work)
- Multi-tenant data isolation (deferred to future milestone)
- User management UI (deferred to future milestone)
- Password reset functionality (deferred to future milestone)
- User account CRUD operations (deferred to future milestone)

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CONF-01 | Phase 18 | Pending |
| CONF-02 | Phase 18 | Pending |
| CONF-03 | Phase 18 | Pending |
| CONF-04 | Phase 18 | Pending |
| CONF-05 | Phase 18 | Pending |
| ADMIN-01 | Phase 19 | Pending |
| ADMIN-02 | Phase 19 | Pending |
| ADMIN-03 | Phase 19 | Pending |
| IDEMP-01 | Phase 19 | Pending |
| IDEMP-02 | Phase 19 | Pending |
| IDEMP-03 | Phase 19 | Pending |
| MONGO-01 | Phase 20 | Pending |
| MONGO-02 | Phase 20 | Pending |
| MONGO-03 | Phase 20 | Pending |
| CONFIG-01 | Phase 17 | Pending |
| CONFIG-02 | Phase 17 | Pending |
| CONFIG-03 | Phase 17 | Pending |

---

**Total Requirements:** 15
**In Scope:** 15
**Future:** 7
**Out of Scope:** 5
