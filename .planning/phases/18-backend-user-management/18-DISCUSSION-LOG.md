# Phase 18: Backend User Management - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-18
**Phase:** 18-Backend User Management
**Areas discussed:** Admin account creation mechanism, User creation endpoint path, User listing endpoint path, User deletion behavior, Password reset functionality, User role update functionality

---

## Admin Account Creation Mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Check and create if missing | Check if admin exists on startup, create if missing. Simple and safe. | ✓ |
| Always create on startup | Always create admin on startup. Simpler but may overwrite existing. | |
| Create only if empty | Create only if users collection is empty. First-time setup only. | |

**User's choice:** Check and create if missing
**Notes:** User selected safe idempotent approach that checks before creating.

---

## User Creation Endpoint Path

| Option | Description | Selected |
|--------|-------------|----------|
| /api/users | RESTful resource-based path. Consistent with CRUD pattern. | ✓ |
| /api/admin/users | Admin-specific path. Clear but less RESTful. | |
| /api/admin/create-admin | Explicit admin creation. More specific but less flexible. | |

**User's choice:** /api/users
**Notes:** User chose RESTful resource-based path for consistency with CRUD pattern.

---

## User Listing Endpoint Path

| Option | Description | Selected |
|--------|-------------|----------|
| /api/users | RESTful resource-based path. Consistent with CRUD pattern. | ✓ |
| /api/admin/users | Admin-specific path. Clear but less RESTful. | |

**User's choice:** /api/users
**Notes:** User chose RESTful resource-based path for consistency with CRUD pattern.

---

## User Deletion Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Cascade delete | Delete user and all associated data. Simple but destructive. | |
| Soft delete | Mark user as deleted but keep data. More complex, requires filtering. | |
| Delete and reassign posts | Delete user, reassign posts to admin. Preserves content. | ✓ |

**User's choice:** Delete and reassign posts
**Notes:** User chose to preserve content by reassigning posts to admin.

---

## Password Reset Functionality

| Option | Description | Selected |
|--------|-------------|----------|
| Self-service | Users can reset their own passwords via email. More complex. | |
| Admin-only | Only admin can reset passwords. Simpler for MVP. | ✓ |

**User's choice:** Admin-only
**Notes:** User chose admin-only approach for MVP simplicity.

---

## User Role Update Functionality

| Option | Description | Selected |
|--------|-------------|----------|
| Self-service | Users can update their own roles. More complex. | |
| Admin-only | Only admin can update user roles. Simpler for MVP. | ✓ |

**User's choice:** Admin-only
**Notes:** User chose admin-only approach for MVP simplicity.

---

## Follow-up Questions

### User Deletion Behavior
**Question:** For user deletion with post reassignment, what if the deleted user has no posts?
**User's choice:** Always succeed
**Notes:** User chose to always succeed even if no posts to reassign.

### Password Reset Endpoint
**Question:** Should password reset be a separate endpoint or part of user update?
**User's choice:** Separate endpoint for reset
**Notes:** User chose separate endpoint POST /api/users/{id}/reset-password for clarity.

### Role Update Endpoint
**Question:** Should role update be a separate endpoint or part of user update?
**User's choice:** Separate endpoint for role
**Notes:** User chose separate endpoint PUT /api/users/{id}/role for clarity.

---

## the agent's Discretion

Areas where user said "you decide" or deferred to the agent:
- ADMIN_PASSWORD environment variable default value
- Admin account username (default: "admin")
- Admin account role (default: "admin")
- User update endpoint structure (PUT /api/users/{id} with optional fields)
- Response format for user listing (pagination, sorting, filtering)
- Error messages for user management operations
- Whether to include password_hash in user response (should be excluded for security)

## Deferred Ideas

None — discussion stayed within phase scope
