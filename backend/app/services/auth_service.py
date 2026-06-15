from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.core.database import AsyncSession
from app.core.exceptions import NotFoundException, ValidationException
from app.core.security import get_password_hash, verify_password
from app.models.user import User

logger = logging.getLogger(__name__)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Return a user by email address."""
    result = await db.execute(select(User).where(User.email == email.lower().strip()))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: Any) -> User | None:
    """Return a user by identifier."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Authenticate a user with email and password."""
    try:
        user = await get_user_by_email(db, email)
        if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
            return None
        user.last_login = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception:
        await db.rollback()
        logger.exception("Failed to authenticate user", extra={"email": email})
        raise


async def create_user(db: AsyncSession, user_data: dict[str, Any]) -> User:
    """Create a new user record."""
    payload = dict(user_data)
    email = str(payload.get("email", "")).lower().strip()
    password = payload.pop("password", None)
    payload["email"] = email

    if not email:
        raise ValidationException("Email is required")
    if not password:
        raise ValidationException("Password is required")
    if await get_user_by_email(db, email):
        raise ValidationException("A user with this email already exists")

    try:
        user = User(**payload, hashed_password=get_password_hash(password))
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError as exc:
        await db.rollback()
        logger.warning("User creation conflict", extra={"email": email})
        raise ValidationException("Unable to create user", details={"email": email}) from exc
    except Exception:
        await db.rollback()
        logger.exception("Failed to create user", extra={"email": email})
        raise


async def update_user(db: AsyncSession, user_id: Any, update_data: dict[str, Any]) -> User:
    """Update an existing user."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")

    payload = dict(update_data)
    if "email" in payload and payload["email"]:
        normalized_email = str(payload["email"]).lower().strip()
        existing = await get_user_by_email(db, normalized_email)
        if existing and existing.id != user.id:
            raise ValidationException("A user with this email already exists")
        payload["email"] = normalized_email

    password = payload.pop("password", None)
    if password:
        user.hashed_password = get_password_hash(password)

    for field, value in payload.items():
        if hasattr(user, field):
            setattr(user, field, value)

    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError as exc:
        await db.rollback()
        logger.warning("User update conflict", extra={"user_id": str(user_id)})
        raise ValidationException("Unable to update user") from exc
    except Exception:
        await db.rollback()
        logger.exception("Failed to update user", extra={"user_id": str(user_id)})
        raise


async def list_users(db: AsyncSession, page: int, page_size: int) -> tuple[list[User], int]:
    """Return paginated users and total count."""
    page = max(page, 1)
    page_size = max(page_size, 1)
    offset = (page - 1) * page_size

    total = await db.scalar(select(func.count()).select_from(User))
    result = await db.execute(select(User).order_by(User.created_at.desc()).offset(offset).limit(page_size))
    return list(result.scalars().all()), int(total or 0)
