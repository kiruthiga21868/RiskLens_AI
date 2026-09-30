"""
Authentication request/response schemas.

Pydantic v2 automatically validates incoming payloads (rejecting bad ones
with a 422) and serialises outgoing responses. Field validators keep the
contract clean: emails must look like emails, passwords must be strong.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Payload for POST /api/v1/auth/register."""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=120)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if v.isdigit() or v.lower() == v and len(set(v)) < 3:
            raise ValueError("Password is too simple")
        return v


class LoginRequest(BaseModel):
    """Payload for POST /api/v1/auth/login (username OR email accepted)."""

    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    """Tokens returned on login/register/refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    """Public user profile (no password hash ever leaves the API)."""

    id: int
    username: str
    email: EmailStr
    full_name: str | None = None
    role: str
    is_active: bool
    awareness_score: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}