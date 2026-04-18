from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Annotated, List
from bson import ObjectId
from app.services.user_service import (
    create_user,
    list_users,
    get_user,
    delete_user,
    reset_password,
    update_role,
)
from app.dependencies.auth import get_current_admin
from app.models.user import UserCreate, UserResponse

router = APIRouter(prefix="/api/users", tags=["User Management"])


class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: str = "user"


class UserListResponse(BaseModel):
    users: List[UserResponse]


class PasswordResetRequest(BaseModel):
    new_password: str


class RoleUpdateRequest(BaseModel):
    role: str


@router.post("", response_model=UserResponse)
async def create_user_endpoint(
    user_data: UserCreateRequest,
    current_admin: Annotated[dict, Depends(get_current_admin)],
) -> UserResponse:
    """Create a new user account (admin-only)."""
    try:
        user = await create_user(user_data.username, user_data.password, user_data.role)
        return UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            role=user["role"],
            created_at=user["created_at"],
            last_login_at=user.get("last_login_at"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=UserListResponse)
async def list_users_endpoint(
    current_admin: Annotated[dict, Depends(get_current_admin)],
) -> UserListResponse:
    """List all user accounts (admin-only)."""
    users = await list_users()
    return UserListResponse(
        users=[
            UserResponse(
                id=user["id"],
                username=user["username"],
                role=user["role"],
                created_at=user["created_at"],
                last_login_at=user.get("last_login_at"),
            )
            for user in users
        ]
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(
    user_id: str, current_admin: Annotated[dict, Depends(get_current_admin)]
) -> UserResponse:
    """Get user by ID (admin-only)."""
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user["id"],
        username=user["username"],
        role=user["role"],
        created_at=user["created_at"],
        last_login_at=user.get("last_login_at"),
    )


@router.delete("/{user_id}")
async def delete_user_endpoint(
    user_id: str, current_admin: Annotated[dict, Depends(get_current_admin)]
):
    """Delete a user account (admin-only)."""
    try:
        success = await delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{user_id}/reset-password")
async def reset_password_endpoint(
    user_id: str,
    request: PasswordResetRequest,
    current_admin: Annotated[dict, Depends(get_current_admin)],
):
    """Reset user password (admin-only)."""
    success = await reset_password(user_id, request.new_password)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password reset successfully"}


@router.put("/{user_id}/role")
async def update_role_endpoint(
    user_id: str,
    request: RoleUpdateRequest,
    current_admin: Annotated[dict, Depends(get_current_admin)],
):
    """Update user role (admin-only)."""
    try:
        success = await update_role(user_id, request.role)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "Role updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
