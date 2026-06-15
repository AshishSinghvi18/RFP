from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select

from app.core.database import AsyncSession
from app.core.exceptions import NotFoundException
from app.models.opportunity import Opportunity
from app.models.report import Report, ReportStatus

logger = logging.getLogger(__name__)


def _serialize_opportunity(opportunity: Opportunity) -> dict[str, Any]:
    return {
        "id": str(opportunity.id),
        "title": opportunity.title,
        "institution": opportunity.institution,
        "country": opportunity.country,
        "region": opportunity.region,
        "score": opportunity.score,
        "status": opportunity.status.value if hasattr(opportunity.status, "value") else str(opportunity.status),
        "updated_at": opportunity.updated_at.isoformat() if opportunity.updated_at else None,
    }


async def list_reports(db: AsyncSession, page: int, page_size: int) -> tuple[list[Report], int]:
    """Return paginated report records."""
    page = max(page, 1)
    page_size = max(page_size, 1)
    offset = (page - 1) * page_size

    total = await db.scalar(select(func.count()).select_from(Report))
    result = await db.execute(select(Report).order_by(Report.created_at.desc()).offset(offset).limit(page_size))
    return list(result.scalars().all()), int(total or 0)


async def generate_report(
    db: AsyncSession,
    report_type: Any,
    parameters: dict[str, Any],
    user_id: Any,
) -> Report:
    """Create a pending report record for asynchronous generation."""
    title = f"{str(getattr(report_type, 'value', report_type)).replace('_', ' ').title()} Report"
    report = Report(
        title=title,
        report_type=report_type,
        status=ReportStatus.PENDING,
        generated_by_id=user_id,
        parameters=dict(parameters or {}),
        summary="Queued for generation.",
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def get_report(db: AsyncSession, report_id: Any) -> Report:
    """Return a report by identifier."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise NotFoundException("Report not found")
    return report


async def generate_weekly_summary(db: AsyncSession) -> dict[str, Any]:
    """Return weekly summary data for new, updated, and high-priority opportunities."""
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    new_items = (
        await db.execute(
            select(Opportunity)
            .where(Opportunity.created_at >= week_ago)
            .order_by(Opportunity.created_at.desc())
            .limit(25)
        )
    ).scalars().all()

    updated_items = (
        await db.execute(
            select(Opportunity)
            .where(Opportunity.updated_at >= week_ago, Opportunity.created_at < week_ago)
            .order_by(Opportunity.updated_at.desc())
            .limit(25)
        )
    ).scalars().all()

    high_priority_items = (
        await db.execute(
            select(Opportunity)
            .where(Opportunity.score >= 71)
            .order_by(Opportunity.score.desc(), Opportunity.updated_at.desc())
            .limit(25)
        )
    ).scalars().all()

    return {
        "new_opportunities": [_serialize_opportunity(item) for item in new_items],
        "updated_opportunities": [_serialize_opportunity(item) for item in updated_items],
        "high_priority_opportunities": [_serialize_opportunity(item) for item in high_priority_items],
        "counts": {
            "new": len(new_items),
            "updated": len(updated_items),
            "high_priority": len(high_priority_items),
        },
    }
