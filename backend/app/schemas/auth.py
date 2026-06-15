from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, EmailStr

from app.schemas.common import SchemaBase


class LoginRequest(SchemaBase):
    email: EmailStr
    password: str


class UserResponse(SchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    last_login: datetime | None = None
    created_at: datetime


class TokenResponse(SchemaBase):
    token: str
    user: UserResponse


class UserCreate(SchemaBase):
    email: EmailStr
    password: str
    full_name: str
    role: str


class UserUpdate(SchemaBase):
    full_name: str | None = None
    role: str | None = None
    is_active: bool | None = None
