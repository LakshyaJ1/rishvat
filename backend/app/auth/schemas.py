"""
AI CFO — Auth Schemas

Pydantic v2 models for auth request/response validation.
These are the contracts Person 3 (frontend) builds against.
"""

import uuid
from pydantic import BaseModel, EmailStr, Field


# ── Request Schemas ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """Registration request — creates both a tenant and a user."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    company_name: str = Field(min_length=1, max_length=255)
    jurisdiction: str = Field(default="US", max_length=10)


class LoginRequest(BaseModel):
    """Login request."""
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


# ── Response Schemas ─────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    """User information included in auth responses."""
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    tenant_id: uuid.UUID

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Response returned on successful register or login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenResponse(BaseModel):
    """Response returned on token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
