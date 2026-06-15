from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import func, select

from app.core.database import AsyncSession
from app.core.exceptions import NotFoundException
from app.models.source import Source

logger = logging.getLogger(__name__)


async def list_sources(db: AsyncSession, page: int, page_size: int) -> tuple[list[Source], int]:
    """Return paginated sources and total count."""
    page = max(page, 1)
    page_size = max(page_size, 1)
    offset = (page - 1) * page_size

    total = await db.scalar(select(func.count()).select_from(Source))
    result = await db.execute(select(Source).order_by(Source.created_at.desc()).offset(offset).limit(page_size))
    return list(result.scalars().all()), int(total or 0)


async def create_source(db: AsyncSession, source_data: dict[str, Any]) -> Source:
    """Create a source record."""
    source = Source(**dict(source_data))
    try:
        db.add(source)
        await db.commit()
        await db.refresh(source)
        return source
    except Exception:
        await db.rollback()
        logger.exception("Failed to create source")
        raise


async def get_source(db: AsyncSession, source_id: Any) -> Source:
    """Return a source by identifier."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise NotFoundException("Source not found")
    return source


async def update_source(db: AsyncSession, source_id: Any, update_data: dict[str, Any]) -> Source:
    """Update a source record."""
    source = await get_source(db, source_id)
    for field, value in dict(update_data).items():
        if hasattr(source, field):
            setattr(source, field, value)

    try:
        await db.commit()
        await db.refresh(source)
        return source
    except Exception:
        await db.rollback()
        logger.exception("Failed to update source", extra={"source_id": str(source_id)})
        raise
