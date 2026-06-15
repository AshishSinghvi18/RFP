from __future__ import annotations

"""Search endpoints."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException
from app.core.security import TokenPayload, get_current_user

try:
    from app.schemas.search import HybridSearchRequest, KeywordSearchRequest, SemanticSearchRequest
except ImportError:
    class KeywordSearchRequest(BaseModel):
        """Fallback keyword search schema until app.schemas.search is available."""

        model_config = ConfigDict(extra="allow")

        query: str = Field(min_length=1)
        filters: dict[str, Any] = Field(default_factory=dict)
        page: int = Field(default=1, ge=1)
        page_size: int = Field(default=20, ge=1, le=100)

    class SemanticSearchRequest(BaseModel):
        """Fallback semantic search schema until app.schemas.search is available."""

        model_config = ConfigDict(extra="allow")

        query: str = Field(min_length=1)
        filters: dict[str, Any] = Field(default_factory=dict)
        top_k: int = Field(default=10, ge=1, le=100)

    class HybridSearchRequest(BaseModel):
        """Fallback hybrid search schema until app.schemas.search is available."""

        model_config = ConfigDict(extra="allow")

        query: str = Field(min_length=1)
        filters: dict[str, Any] = Field(default_factory=dict)
        top_k: int = Field(default=10, ge=1, le=100)
        keyword_weight: float = Field(default=0.5, ge=0.0, le=1.0)
        semantic_weight: float = Field(default=0.5, ge=0.0, le=1.0)

try:
    from app.services import search_service
except ImportError:
    search_service = None

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["search"])

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]


def _success_response(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the standard API success envelope."""
    return {"success": True, "data": data, "meta": meta or {}}


def _get_service() -> Any:
    """Return the search service or raise a service unavailable error."""
    if search_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search service is not available",
        )
    return search_service


@router.post("/keyword", status_code=status.HTTP_200_OK)
async def keyword_search(payload: KeywordSearchRequest, current_user: CurrentUser, db: DBSession) -> dict[str, Any]:
    """Run a keyword-based search across indexed opportunities."""
    try:
        result = await _get_service().keyword_search(db=db, search_request=payload, user_id=current_user.sub)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Keyword search failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Keyword search failed") from exc


@router.post("/semantic", status_code=status.HTTP_200_OK)
async def semantic_search(payload: SemanticSearchRequest, current_user: CurrentUser, db: DBSession) -> dict[str, Any]:
    """Run a semantic vector search across indexed opportunities."""
    try:
        result = await _get_service().semantic_search(db=db, search_request=payload, user_id=current_user.sub)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Semantic search failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Semantic search failed") from exc


@router.post("/hybrid", status_code=status.HTTP_200_OK)
async def hybrid_search(payload: HybridSearchRequest, current_user: CurrentUser, db: DBSession) -> dict[str, Any]:
    """Run a hybrid keyword and semantic search."""
    try:
        result = await _get_service().hybrid_search(db=db, search_request=payload, user_id=current_user.sub)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Hybrid search failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Hybrid search failed") from exc
