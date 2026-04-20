from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId
from app.config import settings
from app.database import users_col
from app.services.auth_service import hash_password, verify_password
from app.redis_client import redis_client
import json
import logging

logger = logging.getLogger(__name__)


async def create_admin_account():
    """Create admin account on first startup if it doesn't exist."""
    # Prevent INIT_USER from being 'admin' to avoid username conflict
    if settings.INIT_USER == "admin":
        logger.error(
            "INIT_USER cannot be 'admin' — this username is reserved for the existing admin account"
        )
        raise ValueError(
            "INIT_USER cannot be 'admin' — this username is reserved for the existing admin account"
        )

    # Check if admin account already exists
    existing_admin = await users_col.find_one({"username": settings.INIT_USER})
    if existing_admin:
        logger.info(
            f"Admin account '{settings.INIT_USER}' already exists, skipping creation"
        )
        return

    # Create admin account with INIT_USER and hashed INIT_PASSWORD
    admin_data = {
        "username": settings.INIT_USER,
        "password_hash": hash_password(settings.INIT_PASSWORD),
        "role": "admin",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login_at": None,
    }
    await users_col.insert_one(admin_data)
    logger.info(f"Admin account '{settings.INIT_USER}' created successfully")


async def create_user(username: str, password: str, role: str = "user") -> dict:
    """Create a new user account."""
    # Check if username already exists
    existing = await users_col.find_one({"username": username})
    if existing:
        raise ValueError("Username already exists")

    user_data = {
        "username": username,
        "password_hash": hash_password(password),
        "role": role,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login_at": None,
    }
    result = await users_col.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return user_data


async def list_users() -> List[dict]:
    """List all user accounts."""
    users = await users_col.find().to_list(length=None)
    for user in users:
        user["id"] = str(user["_id"])
        # Exclude password_hash from response
        if "password_hash" in user:
            del user["password_hash"]
    return users


async def get_user(user_id: str) -> Optional[dict]:
    """Get user by ID."""
    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if user:
        user["id"] = str(user["_id"])
        # Exclude password_hash from response
        if "password_hash" in user:
            del user["password_hash"]
    return user


async def delete_user(user_id: str) -> bool:
    """Delete a user account (prevents deletion of admin)."""
    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        return False

    # Prevent deletion of admin account
    if user.get("role") == "admin":
        raise ValueError("Cannot delete admin account")

    # Delete user
    await users_col.delete_one({"_id": ObjectId(user_id)})

    # Invalidate Redis cache
    cache_key = f"auth:user:{user_id}"
    await redis_client.delete(cache_key)

    return True


async def reset_password(user_id: str, new_password: str) -> bool:
    """Reset user password."""
    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        return False

    # Update password
    await users_col.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password_hash": hash_password(new_password)}},
    )

    # Invalidate Redis cache
    cache_key = f"auth:user:{user_id}"
    await redis_client.delete(cache_key)

    return True


async def update_role(user_id: str, new_role: str) -> bool:
    """Update user role."""
    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        return False

    # Prevent changing admin role
    if user.get("role") == "admin":
        raise ValueError("Cannot change admin role")

    # Update role
    await users_col.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": new_role}})

    # Invalidate Redis cache
    cache_key = f"auth:user:{user_id}"
    await redis_client.delete(cache_key)

    return True
