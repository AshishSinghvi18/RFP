from __future__ import annotations

"""Opportunity endpoints."""

import logging
from datetime import date
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException
from app.core.security import TokenPayload, get_current_user
from app.models.opportunity import OpportunityStatus

try:
    from app.schemas.opportunity import CommentCreateRequest, OpportunitySearchFilters, OpportunityUpdateRequest
except ImportError:
    class OpportunitySearchFilters(BaseModel):
        """Fallback search filter schema until app.schemas.opportunity is available."""

        model_config = ConfigDict(extra="allow", use_enum_values=True)

        region: str | None = None
        country: str | None = None
        min_score: int | None = Field(default=None, ge=0, le=100)
        max_score: int | None = Field(default=None, ge=0, le=100)
        status: OpportunityStatus | list[OpportunityStatus] | None = None
        standards: list[str] | None = None
        start_date: date | None = None
        end_date: date | None = None
        query: str | None = None

    class OpportunityUpdateRequest(BaseModel):
        """Fallback update schema until app.schemas.opportunity is available."""

        model_config = ConfigDict(extra="allow", use_enum_values=True)

        status: OpportunityStatus | None = None
        owner_id: UUID | None = None
        notes: str | None = None

    class CommentCreateRequest(BaseModel):
        """Fallback comment schema until app.schemas.opportunity is available."""

        model_config = ConfigDict(extra="allow")

        content: str = Field(min_length=1)

try:
    from app.services import opportunity_service
except ImportError:
    opportunity_service = None

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/opportunities", tags=["opportunities"])

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]


def _success_response(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the standard API success envelope."""
    return {"success": True, "data": data, "meta": meta or {}}


def _get_service() -> Any:
    """Return the opportunity service or raise a service unavailable error."""
    if opportunity_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Opportunity service is not available",
        )
    return opportunity_service


@router.post("/search", status_code=status.HTTP_200_OK)
async def search_opportunities(
    filters: OpportunitySearchFilters,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, Any]:
    """Search opportunities using region, scoring, status, standards, date, and text filters."""
    try:
        result = await _get_service().search_opportunities(db=db, filters=filters, user_id=current_user.sub)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to search opportunities")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search opportunities",
        ) from exc


@router.get("/{opportunity_id}", status_code=status.HTTP_200_OK)
async def get_opportunity(opportunity_id: UUID, current_user: CurrentUser, db: DBSession) -> dict[str, Any]:
    """Return detailed information for a single opportunity."""
    try:
        result = await _get_service().get_opportunity_by_id(
            db=db,
            opportunity_id=opportunity_id,
            user_id=current_user.sub,
        )
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch opportunity %s", opportunity_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch opportunity",
        ) from exc


@router.patch("/{opportunity_id}", status_code=status.HTTP_200_OK)
async def update_opportunity(
    opportunity_id: UUID,
    payload: OpportunityUpdateRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, Any]:
    """Update an opportunity's status, owner, or notes."""
    try:
        result = await _get_service().update_opportunity(
            db=db,
            opportunity_id=opportunity_id,
            update_data=payload,
            updated_by=current_user.sub,
        )
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update opportunity %s", opportunity_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update opportunity",
        ) from exc


@router.post("/{opportunity_id}/comments", status_code=status.HTTP_201_CREATED)
async def add_comment(
    opportunity_id: UUID,
    payload: CommentCreateRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, Any]:
    """Add a comment to an opportunity."""
    try:
        result = await _get_service().add_comment(
            db=db,
            opportunity_id=opportunity_id,
            user_id=current_user.sub,
            comment_data=payload,
        )
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to add comment to opportunity %s", opportunity_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add comment",
        ) from exc


@router.get("/{opportunity_id}/comments", status_code=status.HTTP_200_OK)
async def list_comments(opportunity_id: UUID, current_user: CurrentUser, db: DBSession) -> dict[str, Any]:
    """List comments associated with an opportunity."""
    try:
        result = await _get_service().list_comments(
            db=db,
            opportunity_id=opportunity_id,
            user_id=current_user.sub,
        )
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to list comments for opportunity %s", opportunity_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list comments",
        ) from exc
