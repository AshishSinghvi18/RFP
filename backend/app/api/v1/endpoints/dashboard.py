from __future__ import annotations

"""Dashboard endpoints."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException
from app.core.security import TokenPayload, get_current_user

try:
    from app.services import dashboard_service
except ImportError:
    dashboard_service = None

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]


def _success_response(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the standard API success envelope."""
    return {"success": True, "data": data, "meta": meta or {}}


def _get_service() -> Any:
    """Return the dashboard service or raise a service unavailable error."""
    if dashboard_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dashboard service is not available",
        )
    return dashboard_service


@router.get("/summary", status_code=status.HTTP_200_OK)
async def get_summary(current_user: CurrentUser, db: DBSession) -> dict[str, Any]:
    """Return KPI counts for the dashboard summary cards."""
    try:
        service = _get_service()
        if hasattr(service, "get_dashboard_summary"):
            result = await service.get_dashboard_summary(db=db, user_id=current_user.sub)
        else:
            result = await service.get_summary(db=db)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch dashboard summary")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard summary",
        ) from exc


@router.get("/trends", status_code=status.HTTP_200_OK)
async def get_trends(current_user: CurrentUser, db: DBSession) -> dict[str, Any]:
    """Return weekly opportunity trend data for dashboard charts."""
    try:
        service = _get_service()
        if hasattr(service, "get_opportunity_trends"):
            result = await service.get_opportunity_trends(db=db, user_id=current_user.sub)
        else:
            result = await service.get_trends(db=db)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch dashboard trends")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard trends",
        ) from exc


@router.get("/heatmap", status_code=status.HTTP_200_OK)
async def get_heatmap(current_user: CurrentUser, db: DBSession) -> dict[str, Any]:
    """Return geographic opportunity distribution for the dashboard heatmap."""
    try:
        service = _get_service()
        if hasattr(service, "get_geographic_heatmap"):
            result = await service.get_geographic_heatmap(db=db, user_id=current_user.sub)
        else:
            result = await service.get_heatmap(db=db)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch dashboard heatmap")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard heatmap",
        ) from exc
