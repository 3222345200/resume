from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resume_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    company_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    job_title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    department: Mapped[str] = mapped_column(String(200), nullable=False, default="", server_default="")
    city: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default="")
    job_link: Mapped[str] = mapped_column(String(500), nullable=False, default="", server_default="")
    jd_summary: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    salary_range: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default="")
    job_type: Mapped[str] = mapped_column(String(50), nullable=False, default="", server_default="")
    applied_at: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    is_todo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    final_result: Mapped[str] = mapped_column(String(50), nullable=False, default="", server_default="")
    channel: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default="")
    referrer_name: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default="")
    contact_name: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default="")
    contact_value: Mapped[str] = mapped_column(String(200), nullable=False, default="", server_default="")
    note: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    risk_note: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="中", server_default="中")
    next_action: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    interview_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
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

    status_histories: Mapped[list["ApplicationStatusHistory"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="desc(ApplicationStatusHistory.changed_at)",
    )


class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_histories"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    application_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_status: Mapped[str] = mapped_column(String(50), nullable=False, default="", server_default="")
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    operator_user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    application: Mapped[Application] = relationship(back_populates="status_histories")
