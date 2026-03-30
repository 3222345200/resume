from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuthVerificationChallenge(Base):
    __tablename__ = "auth_verification_challenges"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    purpose: Mapped[str] = mapped_column(String(32), nullable=False, index=True, default="register")
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    captcha_code: Mapped[str] = mapped_column(String(12), nullable=False)
    captcha_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    email_code: Mapped[str | None] = mapped_column(String(12), nullable=True)
    email_code_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    email_code_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
