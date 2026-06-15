from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import or_, select

from app.core.database import AsyncSession
from app.core.exceptions import AIServiceException
from app.models.opportunity import Opportunity
from app.services.ai_service import get_embedding

logger = logging.getLogger(__name__)


def _serialize_result(opportunity: Opportunity) -> dict[str, Any]:
    return {
        "id": str(opportunity.id),
        "title": opportunity.title,
        "institution": opportunity.institution,
        "country": opportunity.country,
        "region": opportunity.region,
        "category": opportunity.category.value if hasattr(opportunity.category, "value") else str(opportunity.category),
        "score": opportunity.score,
        "status": opportunity.status.value if hasattr(opportunity.status, "value") else str(opportunity.status),
        "ai_summary": opportunity.ai_summary,
        "deadline": opportunity.deadline.isoformat() if opportunity.deadline else None,
        "source_url": opportunity.source_url,
    }


async def keyword_search(db: AsyncSession, query: str, page: int, page_size: int) -> list[dict[str, Any]]:
    """Search opportunities by keyword across core fields."""
    page = max(page, 1)
    page_size = max(page_size, 1)
    offset = (page - 1) * page_size
    search_term = f"%{query.strip()}%"

    result = await db.execute(
        select(Opportunity)
        .where(
            or_(
                Opportunity.title.ilike(search_term),
                Opportunity.institution.ilike(search_term),
                Opportunity.ai_summary.ilike(search_term),
            )
        )
        .order_by(Opportunity.score.desc(), Opportunity.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    return [_serialize_result(item) for item in result.scalars().all()]


async def semantic_search(db: AsyncSession, query: str, page: int, page_size: int) -> list[dict[str, Any]]:
    """Placeholder semantic search that currently falls back to keyword results."""
    try:
        await get_embedding(query)
    except AIServiceException:
        logger.warning("Semantic search fallback triggered for query")
    return await keyword_search(db, query, page, page_size)


async def hybrid_search(db: AsyncSession, query: str, page: int, page_size: int) -> list[dict[str, Any]]:
    """Return hybrid search results by delegating to keyword search for now."""
    return await keyword_search(db, query, page, page_size)
