"""API request/response DTOs for auth endpoints.

These are plain Pydantic models, not the frozen event/state contracts in
app/contracts — they describe HTTP wire shapes for this one router and are
free to change as the API evolves.
"""

from __future__ import annotations

import re
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# Deliberately small and boring: a real deployment should back this with a
# proper breached-password list (e.g. Have I Been Pwned's k-anonymity API).
# This hardcoded set exists to catch the most obvious throwaway passwords.
_COMMON_PASSWORDS = {
    "password123",
    "password1234",
    "letmein1234",
    "qwerty123456",
    "iloveyou1234",
    "admin1234567",
    "welcome12345",
    "123456789012",
    "changeme1234",
}


def _validate_password_policy(value: str) -> str:
    if len(value) < 10:
        raise ValueError("password must be at least 10 characters long")
    if not re.search(r"[A-Za-z]", value):
        raise ValueError("password must contain at least one letter")
    if not re.search(r"\d", value):
        raise ValueError("password must contain at least one digit")
    if value.lower() in _COMMON_PASSWORDS:
        raise ValueError("password is too common; choose something less guessable")
    return value


RiskTolerance = Literal["conservative", "balanced", "aggressive"]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10)
    display_name: str | None = None
    phone: str | None = None
    risk_tolerance: RiskTolerance = "balanced"

    @field_validator("password")
    @classmethod
    def _check_password_policy(cls, v: str) -> str:
        return _validate_password_policy(v)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    display_name: str | None
    phone: str | None
    account_type: str
    is_active: bool
    is_verified: bool
    risk_tolerance: str
    onboarding_stage: str


class OrgMembershipResponse(BaseModel):
    org_id: UUID
    org_name: str
    org_slug: str
    role: str


class UpdateProfileRequest(BaseModel):
    risk_tolerance: RiskTolerance | None = None
    display_name: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=10)

    @field_validator("new_password")
    @classmethod
    def _check_password_policy(cls, v: str) -> str:
        return _validate_password_policy(v)
