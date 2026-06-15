from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Enum as SAEnum, Float, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.document import Document


class SourceType(str, Enum):
    REGULATOR_WEBSITE = "regulator_website"
    TENDER_PORTAL = "tender_portal"
    PROCUREMENT_SYSTEM = "procurement_system"
    GOVERNMENT_WEBSITE = "government_website"
    PRESS_RELEASE = "press_release"
    RSS_FEED = "rss_feed"
    PDF = "pdf"
    ANNUAL_REPORT = "annual_report"
    NEWS_FEED = "news_feed"
    FUNDING_PORTAL = "funding_portal"
    OTHER = "other"


class CrawlFrequency(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class CrawlStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(SAEnum(SourceType, name="source_type"), nullable=False)
    frequency: Mapped[CrawlFrequency] = mapped_column(SAEnum(CrawlFrequency, name="crawl_frequency"), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_crawl_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_crawl_status: Mapped[CrawlStatus] = mapped_column(
        SAEnum(CrawlStatus, name="crawl_status"), default=CrawlStatus.PENDING, nullable=False
    )
    success_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    documents: Mapped[list[Document]] = relationship(back_populates="source")
