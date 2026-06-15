from __future__ import annotations

from pydantic import Field

from app.schemas.common import SchemaBase


class DashboardSummary(SchemaBase):
    total_opportunities: int = Field(..., ge=0)
    high_priority: int = Field(..., ge=0)
    new_this_week: int = Field(..., ge=0)
    active_rfps: int = Field(..., ge=0)
    regions_covered: int = Field(..., ge=0)
    crawl_success_rate: float = Field(..., ge=0.0, le=100.0)


class TrendData(SchemaBase):
    period: str
    count: int = Field(..., ge=0)


class HeatmapData(SchemaBase):
    region: str
    country: str
    count: int = Field(..., ge=0)
