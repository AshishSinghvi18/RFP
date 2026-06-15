from __future__ import annotations

"""Alert endpoints."""

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException
from app.core.security import TokenPayload, get_current_user

try:
    from app.schemas.alert import AlertStatusUpdateRequest
except ImportError:
    class AlertStatusUpdateRequest(BaseModel):
        """Fallback alert status schema until app.schemas.alert is available."""

        model_config = ConfigDict(extra="allow")

        is_read: bool

try:
    from app.services import alert_service
except ImportError:
    alert_service = None

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/alerts", tags=["alerts"])

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]


def _success_response(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the standard API success envelope."""
    return {"success": True, "data": data, "meta": meta or {}}


def _get_service() -> Any:
    """Return the alert service or raise a service unavailable error."""
    if alert_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Alert service is not available",
        )
    return alert_service


@router.get("/", status_code=status.HTTP_200_OK)
async def list_alerts(
    current_user: CurrentUser,
    db: DBSession,
    unread: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    """List alerts for the authenticated user with optional unread filtering."""
    try:
        result = await _get_service().list_user_alerts(
            db=db,
            user_id=current_user.sub,
            unread=unread,
            page=page,
            page_size=page_size,
        )
        return _success_response(result, meta={"page": page, "page_size": page_size, "unread": unread})
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to list alerts")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list alerts") from exc


@router.patch("/{alert_id}", status_code=status.HTTP_200_OK)
async def update_alert(
    alert_id: UUID,
    payload: AlertStatusUpdateRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, Any]:
    """Mark a single alert as read or unread."""
    try:
        result = await _get_service().update_alert_status(
            db=db,
            alert_id=alert_id,
            user_id=current_user.sub,
            is_read=payload.is_read,
        )
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update alert %s", alert_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update alert") from exc


@router.post("/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_read(current_user: CurrentUser, db: DBSession) -> dict[str, Any]:
    """Mark all alerts for the authenticated user as read."""
    try:
        result = await _get_service().mark_all_alerts_read(db=db, user_id=current_user.sub)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to mark all alerts as read")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark all alerts as read",
        ) from exc
