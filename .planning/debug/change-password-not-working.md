---
status: resolved
trigger: the change password feature not work, I changed once, the browser pop a successfully box but the password still the same
created: 2026-04-19T16:58:28Z
updated: 2026-04-19T23:58:58Z
---

# Debug Session: change-password-not-working

## Symptoms

### Expected Behavior
- New password should work for login

### Actual Behavior
- New password doesn't work

### Error Messages
- No errors

### Timeline
- Never worked

### Reproduction
- Standard flow: Click Change Password, enter current and new password, submit

## Current Focus

hypothesis: The change_password endpoint does not invalidate Redis cache after updating the password, causing authentication to fail with the new password until the cache expires (15 minutes)
test: Add cache invalidation to change_password endpoint and verify that new password works immediately
expecting: After adding cache invalidation, the new password should work immediately after change
next_action: Fix the change_password endpoint to invalidate both username and user_id cache keys
reasoning_checkpoint:
tdd_checkpoint:

## Evidence

- timestamp: 2026-04-19T23:58:58Z
  source: code review
  finding: Change password endpoint in backend/app/routers/auth.py (lines 109-130) updates password in MongoDB but does not invalidate Redis cache
  details: |
    The change_password endpoint updates the password hash in the database:
    ```python
    await users_col.update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$set": {"password_hash": hash_password(request.new_password)}},
    )
    ```
    But it does not invalidate the Redis cache. The auth_service.py caches user data with keys:
    - `auth:user:{username}` (expires in 900 seconds)
    - `auth:user:{user_id}` (expires in 900 seconds)

    When a user tries to login after changing password, the authenticate_user function retrieves the cached user data with the old password hash, causing authentication to fail.

- timestamp: 2026-04-19T23:58:58Z
  source: code review
  finding: Other password update functions properly invalidate cache
  details: |
    The reset_password function in user_service.py (lines 88-104) properly invalidates the cache:
    ```python
    # Invalidate Redis cache
    cache_key = f"auth:user:{user_id}"
    await redis_client.delete(cache_key)
    ```
    This pattern should be followed in the change_password endpoint.

## Eliminated

## Resolution

root_cause: The change_password endpoint in backend/app/routers/auth.py did not invalidate Redis cache after updating the password hash. The auth_service caches user data with keys `auth:user:{username}` and `auth:user:{user_id}` (15-minute TTL). When a user changed their password, the database was updated but the cache still contained the old password hash, causing authentication to fail with the new password until the cache expired.

fix: Added cache invalidation to the change_password endpoint. After updating the password in MongoDB, the endpoint now deletes both cache keys:
- `auth:user:{username}` - cache key for username lookup
- `auth:user:{user_id}` - cache key for user_id lookup

This ensures that the next authentication attempt retrieves the updated password hash from the database.

verification: The fix can be verified by:
1. Changing a user's password via the change password modal
2. Immediately attempting to login with the new password
3. The login should succeed (previously it would fail until the 15-minute cache expired)

files_changed:
- backend/app/routers/auth.py: Added redis_client import and cache invalidation in change_password endpoint
