from __future__ import annotations

"""AI copilot endpoints."""

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException
from app.core.security import TokenPayload, get_current_user

try:
    from app.schemas.ai import ChatRequest, DocumentQnARequest, SummarizeRequest
except ImportError:
    class ChatRequest(BaseModel):
        """Fallback chat schema until app.schemas.ai is available."""

        model_config = ConfigDict(extra="allow")

        message: str = Field(min_length=1)
        session_id: UUID | None = None
        context: dict[str, Any] = Field(default_factory=dict)

    class SummarizeRequest(BaseModel):
        """Fallback summarize schema until app.schemas.ai is available."""

        model_config = ConfigDict(extra="allow")

        document_id: UUID | None = None
        text: str | None = None
        max_length: int | None = Field(default=None, ge=1)

    class DocumentQnARequest(BaseModel):
        """Fallback Q&A schema until app.schemas.ai is available."""

        model_config = ConfigDict(extra="allow")

        question: str = Field(min_length=1)
        document_id: UUID | None = None
        context: dict[str, Any] = Field(default_factory=dict)

try:
    from app.services import copilot_service
except ImportError:
    copilot_service = None

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]


def _success_response(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the standard API success envelope."""
    return {"success": True, "data": data, "meta": meta or {}}


def _get_service() -> Any:
    """Return the copilot service or raise a service unavailable error."""
    if copilot_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI copilot service is not available",
        )
    return copilot_service


@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat(payload: ChatRequest, current_user: CurrentUser, db: DBSession) -> dict[str, Any]:
    """Handle the main AI copilot chat workflow."""
    try:
        result = await _get_service().chat(db=db, user_id=current_user.sub, chat_request=payload)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("AI chat request failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AI chat request failed") from exc


@router.post("/summarize", status_code=status.HTTP_200_OK)
async def summarize(payload: SummarizeRequest, current_user: CurrentUser, db: DBSession) -> dict[str, Any]:
    """Summarize a supplied document or text input."""
    try:
        result = await _get_service().summarize_document(db=db, user_id=current_user.sub, summary_request=payload)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("AI summarize request failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AI summarize request failed") from exc


@router.post("/qna", status_code=status.HTTP_200_OK)
async def question_answering(payload: DocumentQnARequest, current_user: CurrentUser, db: DBSession) -> dict[str, Any]:
    """Answer a question against stored opportunity context or documents."""
    try:
        result = await _get_service().answer_question(db=db, user_id=current_user.sub, qna_request=payload)
        return _success_response(result)
    except AppException:
        raise
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("AI Q&A request failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AI Q&A request failed") from exc
