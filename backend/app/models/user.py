from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8)
    role: str = Field(default="user")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username must contain only alphanumeric characters and underscores"
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in ["admin", "editor", "user"]:
            raise ValueError("Role must be one of: admin, editor, user")
        return v


class UserUpdate(BaseModel):
    role: Optional[str] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v is not None and v not in ["admin", "editor", "user"]:
            raise ValueError("Role must be one of: admin, editor, user")
        return v


class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    created_at: str
    last_login_at: Optional[str] = None

    class Config:
        from_attributes = True
