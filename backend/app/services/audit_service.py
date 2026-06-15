from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import func, select

from app.core.database import AsyncSession
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


async def log_action(
    db: AsyncSession,
    user_id: Any,
    action: str,
    resource_type: str,
    resource_id: str | None,
    details: dict[str, Any] | None,
    ip_address: str | None,
) -> AuditLog:
    """Create an audit log entry."""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address,
    )
    try:
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        return audit_log
    except Exception:
        await db.rollback()
        logger.exception("Failed to write audit log", extra={"action": action, "resource_type": resource_type})
        raise


async def list_audit_logs(
    db: AsyncSession,
    page: int,
    page_size: int,
    user_id: Any | None = None,
    action: str | None = None,
) -> tuple[list[AuditLog], int]:
    """Return paginated audit logs with optional filters."""
    page = max(page, 1)
    page_size = max(page_size, 1)
    offset = (page - 1) * page_size

    stmt = select(AuditLog)
    if user_id is not None:
        stmt = stmt.where(AuditLog.user_id == user_id)
    if action:
        stmt = stmt.where(AuditLog.action == action)

    total = await db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    result = await db.execute(stmt.order_by(AuditLog.created_at.desc()).offset(offset).limit(page_size))
    return list(result.scalars().all()), int(total or 0)
