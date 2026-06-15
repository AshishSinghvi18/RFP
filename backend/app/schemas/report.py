from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import ConfigDict

from app.schemas.common import SchemaBase


class ReportGenerateRequest(SchemaBase):
    type: Literal["weekly", "monthly", "custom"]
    parameters: dict[str, Any] | None = None


class ReportResponse(SchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    status: str
    parameters: dict[str, Any] | None = None
    file_url: str | None = None
    generated_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
