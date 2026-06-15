from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import func, select, update

from app.core.database import AsyncSession
from app.core.exceptions import NotFoundException
from app.models.alert import Alert

logger = logging.getLogger(__name__)


async def list_alerts(
    db: AsyncSession,
    user_id: Any,
    unread_only: bool,
    page: int,
    page_size: int,
) -> tuple[list[Alert], int]:
    """Return paginated alerts for a user."""
    page = max(page, 1)
    page_size = max(page_size, 1)
    offset = (page - 1) * page_size

    stmt = select(Alert).where(Alert.user_id == user_id)
    if unread_only:
        stmt = stmt.where(Alert.is_read.is_(False))

    total = await db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    result = await db.execute(stmt.order_by(Alert.created_at.desc()).offset(offset).limit(page_size))
    return list(result.scalars().all()), int(total or 0)


async def mark_alert_read(db: AsyncSession, alert_id: Any, is_read: bool) -> Alert:
    """Mark a single alert read or unread."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise NotFoundException("Alert not found")

    alert.is_read = is_read
    await db.commit()
    await db.refresh(alert)
    return alert


async def mark_all_read(db: AsyncSession, user_id: Any) -> int:
    """Mark all unread alerts as read for a user."""
    result = await db.execute(
        update(Alert).where(Alert.user_id == user_id, Alert.is_read.is_(False)).values(is_read=True)
    )
    await db.commit()
    return int(result.rowcount or 0)


async def create_alert(db: AsyncSession, alert_data: dict[str, Any]) -> Alert:
    """Create a new alert record."""
    alert = Alert(**dict(alert_data))
    try:
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert
    except Exception:
        await db.rollback()
        logger.exception("Failed to create alert")
        raise
