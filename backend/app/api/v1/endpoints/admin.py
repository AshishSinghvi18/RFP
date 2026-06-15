from __future__ import annotations

"""Administrative endpoints."""

import logging
from datetime import date
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException
from app.core.security import TokenPayload, role_required
from app.models.user import UserRole

try:
    from app.schemas.admin import AdminUserCreateRequest, AdminUserUpdateRequest
except ImportError:
    class AdminUserCreateRequest(BaseModel):
        """Fallback admin user creation schema until app.schemas.admin is available."""

        model_config = ConfigDict(extra="allow", use_enum_values=True)

        email: EmailStr
        full_name: str = Field(min_length=1, max_length=255)
        password: str = Field(min_length=8)
        role: UserRole = UserRole.VIEWER
        is_active: bool = True

    class AdminUserUpdateRequest(BaseModel):
        """Fallback admin user update schema until app.schemas.admin is available."""

        model_config = ConfigDict(extra="allow", use_enum_values=True)

        full_name: str | None = Field(default=None, min_length=1, max_length=255)
        role: UserRole | None = None
        is_active: bool | None = None
        password: str | None = Field(default=None, min_length=8)

try:
    from app.services import admin_service
except ImportError:
    admin_service = None

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

DBSession = Annotated[AsyncSession, Depends(get_db)]
AdminUser = Annotated[TokenPayload, Depends(role_required([UserRole.ADMIN.value]))]


def _success_response(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the standard API success envelope."""
    return {"success": True, "data": data, "meta": meta or {}}


def _get_service() -> Any:
    """Return the admin service or raise a service unavailable error."""
    if admin_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service is not available",
        )
    return admin_service


@router.get("/users", status_code=status.HTTP_200_OK)
async def list_users(
    current_user: AdminUser,
    db: DBSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    role: UserRole | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    search: str | None = Query(default=None),
) -> dict[str, Any]:
    """List users with optional filtering and pagination."""
    try:
        result = await _get_service().list_users(
            db=db,
            page=page,
            page_size=page_size,
            role=role,
            is_active=is_active,
            search=search,
            requested_by=current_user.sub,
        )
        return _success_response(
            result,
            meta={"page": page, "page_size": page_size, "role": role, "is_active": is_active},
        )
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to list users")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list users") from exc


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(payload: AdminUserCreateRequest, db: DBSession, current_user: AdminUser) -> dict[str, Any]:
    """Create a new user account from the admin console."""
    try:
        result = await _get_service().create_user(db=db, user_data=payload, created_by=current_user.sub)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to create user")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user") from exc


@router.patch("/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID,
    payload: AdminUserUpdateRequest,
    db: DBSession,
    current_user: AdminUser,
) -> dict[str, Any]:
    """Update a user account from the admin console."""
    try:
        result = await _get_service().update_user(
            db=db,
            user_id=user_id,
            update_data=payload,
            updated_by=current_user.sub,
        )
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update user %s", user_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user") from exc


@router.get("/ai-costs", status_code=status.HTTP_200_OK)
async def get_ai_costs(
    current_user: AdminUser,
    db: DBSession,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
) -> dict[str, Any]:
    """Return aggregated AI usage and cost metrics."""
    try:
        result = await _get_service().get_ai_cost_summary(
            db=db,
            start_date=start_date,
            end_date=end_date,
            requested_by=current_user.sub,
        )
        return _success_response(result, meta={"start_date": start_date, "end_date": end_date})
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch AI cost summary")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch AI cost summary",
        ) from exc


@router.get("/audit-logs", status_code=status.HTTP_200_OK)
async def list_audit_logs(
    current_user: AdminUser,
    db: DBSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    action: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    user_id: UUID | None = Query(default=None),
) -> dict[str, Any]:
    """List audit logs with pagination and optional filters."""
    try:
        result = await _get_service().list_audit_logs(
            db=db,
            page=page,
            page_size=page_size,
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            requested_by=current_user.sub,
        )
        return _success_response(
            result,
            meta={
                "page": page,
                "page_size": page_size,
                "action": action,
                "resource_type": resource_type,
                "user_id": user_id,
            },
        )
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to list audit logs")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list audit logs",
        ) from exc
