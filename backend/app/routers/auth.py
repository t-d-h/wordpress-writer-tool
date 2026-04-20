from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated
from datetime import datetime, timezone
from bson import ObjectId
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.database import users_col
from app.dependencies.auth import get_current_user
from app.models.user import UserCreate, UserResponse
from app.redis_client import redis_client

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenResponse:
    """Authenticate user and return JWT tokens."""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token = create_access_token(
        user_id=user["id"], username=user["username"], role=user["role"]
    )

    # Generate refresh token
    refresh_token = create_refresh_token(user_id=user["id"], username=user["username"])

    # Update last_login_at and store refresh token
    await users_col.update_one(
        {"_id": ObjectId(user["id"])},
        {
            "$set": {
                "last_login_at": datetime.now(timezone.utc).isoformat(),
                "refresh_token": refresh_token,
            }
        },
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh(refresh_token: str) -> TokenResponse:
    """Refresh access token using refresh token."""
    try:
        payload = decode_token(refresh_token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Verify refresh token exists in database
        user = await users_col.find_one({"_id": ObjectId(user_id)})
        if not user or user.get("refresh_token") != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Generate new access token
        access_token = create_access_token(
            user_id=user_id, username=user["username"], role=user["role"]
        )

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.get("/me")
async def get_me(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> UserResponse:
    """Get current user information."""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        role=current_user["role"],
        created_at=current_user["created_at"],
        last_login_at=current_user.get("last_login_at"),
    )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Change current user's password."""
    # Get user from database with password hash
    user = await users_col.find_one({"_id": ObjectId(current_user["id"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify current password
    if not verify_password(request.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Update password
    await users_col.update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$set": {"password_hash": hash_password(request.new_password)}},
    )

    # Invalidate Redis cache for both username and user_id
    cache_key_username = f"auth:user:{current_user['username']}"
    cache_key_user_id = f"auth:user:{current_user['id']}"
    await redis_client.delete(cache_key_username)
    await redis_client.delete(cache_key_user_id)

    return {"message": "Password changed successfully"}
