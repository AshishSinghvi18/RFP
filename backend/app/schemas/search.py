from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase


class KeywordSearchRequest(SchemaBase):
    query: str
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1)


class SemanticSearchRequest(SchemaBase):
    query: str
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1)


class HybridSearchRequest(SchemaBase):
    query: str
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1)


class SearchResult(SchemaBase):
    opportunity_id: UUID
    title: str
    score: int | None = None
    relevance_score: float
    snippet: str | None = None
    country: str | None = None
    region: str | None = None
    category: str | None = None
