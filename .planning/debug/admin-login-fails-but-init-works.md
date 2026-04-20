---
status: resolved
trigger: I have just recreate this project. I can loggin using init user but can't login using admin user
created: 2026-04-20T11:19:44+07:00
updated: 2026-04-20T11:20:59+07:00
---

## Symptoms

### Expected Behavior
Both users can login

### Actual Behavior
Login fails with error

### Error Messages
UI error message

### Timeline
Worked before, now broken

### Reproduction Steps
Enter credentials, click login

## Current Focus

**Hypothesis**: User is attempting to login with username "admin" but the admin account was created with username "tam" (from INIT_USER environment variable). The system is working as designed - admin username is configurable via INIT_USER, not hardcoded to "admin".

**Test**: Verify database contains user with username "tam" (role: admin) and no user with username "admin"

**Expecting**: Database will show one admin user with username "tam", confirming the hypothesis

**Next Action**: Verify database state and confirm root cause with user

**Reasoning Checkpoint**:

**TDD Checkpoint**:

## Evidence

- timestamp: 2026-04-20T11:20:59+07:00
  - source: config analysis
  - finding: .env file shows INIT_USER=tam, INIT_PASSWORD=tam123
  - implication: Admin account is created with username "tam", not "admin"

- timestamp: 2026-04-20T11:20:59+07:00
  - source: code review
  - finding: user_service.py create_admin_account() creates admin with username from INIT_USER
  - code: Line 35: `"username": settings.INIT_USER`
  - validation: Lines 16-23 prevent INIT_USER from being "admin"

- timestamp: 2026-04-20T11:20:59+07:00
  - source: database query
  - finding: Database contains exactly one user: username="tam", role="admin"
  - confirmation: No user with username "admin" exists
  - evidence: MongoDB query result from wordpress_writer1.users collection

## Eliminated

## Resolution

**Root Cause**: User is attempting to login with username "admin" but the admin account was created with username "tam" (from INIT_USER environment variable). The system is working as designed - the admin username is configurable via INIT_USER, not hardcoded to "admin".

**Fix**: User should login with username "tam" and password "tam123" (from INIT_USER and INIT_PASSWORD in .env file). Alternatively, if they want to use username "admin", they can either:
1. Change INIT_USER to "admin" in .env and recreate the database, OR
2. Create a new user with username "admin" using the existing admin account

**Verification**: Confirmed by database query showing only user "tam" exists with admin role.

**Files Changed**: None (this is a configuration/usage issue, not a code bug)
