from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import ConfigDict

from app.schemas.common import SchemaBase


class AlertResponse(SchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    title: str
    message: str
    opportunity_id: UUID | None = None
    is_read: bool
    metadata: dict[str, Any] | None = None
    created_at: datetime


class AlertUpdate(SchemaBase):
    is_read: bool
