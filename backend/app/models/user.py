from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.audit_log import AuditLog
    from app.models.chat_session import ChatSession
    from app.models.comment import Comment
    from app.models.opportunity import Opportunity
    from app.models.report import Report


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    SALES_USER = "sales_user"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, name="user_role"), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    comments: Mapped[list[Comment]] = relationship(back_populates="user")
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="user")
    owned_opportunities: Mapped[list[Opportunity]] = relationship(back_populates="owner")
    alerts: Mapped[list[Alert]] = relationship(back_populates="user")
    reports: Mapped[list[Report]] = relationship(back_populates="generated_by")
    chat_sessions: Mapped[list[ChatSession]] = relationship(back_populates="user")
