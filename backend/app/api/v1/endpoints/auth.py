from __future__ import annotations

"""Authentication endpoints."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException
from app.core.security import TokenPayload, get_current_user, role_required
from app.models.user import UserRole

try:
    from app.schemas.auth import LoginRequest, UserCreateRequest
except ImportError:
    class LoginRequest(BaseModel):
        """Fallback login schema until app.schemas.auth is available."""

        model_config = ConfigDict(extra="allow")

        email: EmailStr
        password: str = Field(min_length=8)

    class UserCreateRequest(BaseModel):
        """Fallback user creation schema until app.schemas.auth is available."""

        model_config = ConfigDict(extra="allow", use_enum_values=True)

        email: EmailStr
        full_name: str = Field(min_length=1, max_length=255)
        password: str = Field(min_length=8)
        role: UserRole = UserRole.VIEWER
        is_active: bool = True

try:
    from app.services import auth_service
except ImportError:
    auth_service = None

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]
AdminUser = Annotated[TokenPayload, Depends(role_required([UserRole.ADMIN.value]))]


def _success_response(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the standard API success envelope."""
    return {"success": True, "data": data, "meta": meta or {}}


def _get_service() -> Any:
    """Return the auth service or raise a service unavailable error."""
    if auth_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is not available",
        )
    return auth_service


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest, db: DBSession) -> dict[str, Any]:
    """Authenticate a user with email and password and return a JWT."""
    try:
        result = await _get_service().login_user(db=db, login_data=payload)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to login user")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to login user") from exc


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(current_user: CurrentUser, db: DBSession) -> dict[str, Any]:
    """Return the current authenticated user's profile."""
    try:
        result = await _get_service().get_current_user_profile(db=db, user_id=current_user.sub)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to load current user profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load current user profile",
        ) from exc


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreateRequest, db: DBSession, current_user: AdminUser) -> dict[str, Any]:
    """Create a new user account as an administrator."""
    try:
        result = await _get_service().create_user(db=db, user_data=payload, created_by=current_user.sub)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to register user")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register user") from exc
