from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    application_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resume_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    round_name: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default="")
    round_index: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    interview_type: Mapped[str] = mapped_column(String(50), nullable=False, default="online", server_default="online")
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60, server_default="60")
    interviewer_name: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default="")
    interviewer_role: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default="")
    result: Mapped[str] = mapped_column(
        String(50), nullable=False, default="scheduled", server_default="scheduled", index=True
    )
    is_reviewed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false", index=True
    )
    document_title: Mapped[str] = mapped_column(String(200), nullable=False, default="", server_default="")
    document_content: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    preparation_note: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    free_note: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    strength_note: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    weakness_note: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    missing_knowledge_note: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    next_round_prep_note: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    follow_up_action: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    need_thank_you: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    need_follow_up: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    question_items: Mapped[list["InterviewQuestionNote"]] = relationship(
        back_populates="interview",
        cascade="all, delete-orphan",
        order_by="InterviewQuestionNote.sort_order.asc(), InterviewQuestionNote.created_at.asc()",
    )


class InterviewQuestionNote(Base):
    __tablename__ = "interview_question_notes"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    interview_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    question_text: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    question_category: Mapped[str] = mapped_column(String(50), nullable=False, default="other", server_default="other")
    answer_note: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    follow_up_question: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    self_evaluation: Mapped[str] = mapped_column(String(50), nullable=False, default="normal", server_default="normal")
    need_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    interview: Mapped[Interview] = relationship(back_populates="question_items")
