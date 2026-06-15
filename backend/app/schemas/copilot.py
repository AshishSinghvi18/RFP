from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase


class ChatRequest(SchemaBase):
    session_id: UUID | None = None
    message: str


class ChatResponse(SchemaBase):
    answer: str
    citations: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float
    session_id: UUID


class SummarizeRequest(SchemaBase):
    document_id: UUID


class QnARequest(SchemaBase):
    question: str
    context_ids: list[UUID] | None = None
