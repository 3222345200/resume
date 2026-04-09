from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.db import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.models.application import Application
from app.models.interview import Interview, InterviewQuestionNote
from app.models.resume import Resume
from app.models.user import User
from app.schemas.interview import (
    InterviewApplicationSummarySchema,
    InterviewCreateSchema,
    InterviewListItemSchema,
    InterviewListResponseSchema,
    InterviewQuestionCreateSchema,
    InterviewQuestionReadSchema,
    InterviewQuestionUpdateSchema,
    InterviewReadSchema,
    InterviewResultUpdateSchema,
    InterviewStatsOverviewSchema,
    InterviewUpdateSchema,
    compute_this_week_start,
)

router = APIRouter(prefix="/interviews", tags=["interviews"])
logger = get_logger("interviews")

TERMINAL_APPLICATION_STATUSES = {"Offer", "已拒绝", "已结束"}


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _ensure_application_owned_by_user(db: Session, current_user: User, application_id: str) -> Application:
    application = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


def _ensure_resume_owned_by_user(db: Session, current_user: User, resume_id: str | None) -> Resume | None:
    if not resume_id:
        return None
    resume = db.scalar(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
    )
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume


def _get_interview_or_404(db: Session, current_user: User, interview_id: str) -> Interview:
    interview = db.scalar(
        select(Interview)
        .options(selectinload(Interview.question_items))
        .where(
            Interview.id == interview_id,
            Interview.user_id == current_user.id,
        )
    )
    if interview is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")
    return interview


def _sync_application_interview_count(db: Session, application: Application) -> None:
    application.interview_count = db.scalar(
        select(func.count()).select_from(Interview).where(Interview.application_id == application.id)
    ) or 0


def _sync_application_status_from_interview(application: Application, interview_result: str) -> None:
    if interview_result == "rejected":
        application.status = "已拒绝"
    elif interview_result == "offer":
        application.status = "Offer"
    elif application.status not in TERMINAL_APPLICATION_STATUSES:
        application.status = "面试中"
    application.status_updated_at = datetime.now(timezone.utc)


def _serialize_question(question: InterviewQuestionNote) -> InterviewQuestionReadSchema:
    return InterviewQuestionReadSchema(
        id=question.id,
        sort_order=question.sort_order,
        question_text=question.question_text,
        question_category=question.question_category,
        answer_note=question.answer_note,
        follow_up_question=question.follow_up_question,
        self_evaluation=question.self_evaluation,
        need_review=question.need_review,
        created_at=question.created_at.isoformat(),
        updated_at=question.updated_at.isoformat(),
    )


def _build_application_summary(application: Application, resume_title: str | None = None) -> InterviewApplicationSummarySchema:
    return InterviewApplicationSummarySchema(
        id=application.id,
        company_name=application.company_name,
        job_title=application.job_title,
        status=application.status,
        resume_id=application.resume_id,
        resume_title=resume_title,
        interview_count=application.interview_count,
    )


def _serialize_read(
    interview: Interview,
    application: Application,
    resume_title: str | None = None,
) -> InterviewReadSchema:
    return InterviewReadSchema(
        id=interview.id,
        application_id=interview.application_id,
        resume_id=interview.resume_id,
        company_name=application.company_name,
        job_title=application.job_title,
        application_status=application.status,
        resume_title=resume_title,
        round_name=interview.round_name,
        round_index=interview.round_index,
        scheduled_at=_serialize_datetime(interview.scheduled_at),
        interview_type=interview.interview_type,
        duration_minutes=interview.duration_minutes,
        interviewer_name=interview.interviewer_name,
        interviewer_role=interview.interviewer_role,
        result=interview.result,
        is_reviewed=interview.is_reviewed,
        document_title=interview.document_title,
        document_content=interview.document_content,
        preparation_note=interview.preparation_note,
        free_note=interview.free_note,
        strength_note=interview.strength_note,
        weakness_note=interview.weakness_note,
        missing_knowledge_note=interview.missing_knowledge_note,
        next_round_prep_note=interview.next_round_prep_note,
        follow_up_action=interview.follow_up_action,
        follow_up_at=_serialize_datetime(interview.follow_up_at),
        need_thank_you=interview.need_thank_you,
        need_follow_up=interview.need_follow_up,
        question_items=[_serialize_question(item) for item in interview.question_items],
        application_summary=_build_application_summary(application, resume_title=resume_title),
        created_at=interview.created_at.isoformat(),
        updated_at=interview.updated_at.isoformat(),
    )


def _serialize_list_item(interview: Interview, application: Application) -> InterviewListItemSchema:
    return InterviewListItemSchema(
        id=interview.id,
        application_id=interview.application_id,
        company_name=application.company_name,
        job_title=application.job_title,
        round_name=interview.round_name,
        round_index=interview.round_index,
        scheduled_at=_serialize_datetime(interview.scheduled_at),
        interview_type=interview.interview_type,
        result=interview.result,
        is_reviewed=interview.is_reviewed,
        interview_count=application.interview_count,
        application_status=application.status,
        updated_at=interview.updated_at.isoformat(),
    )


def _apply_interview_payload(
    interview: Interview,
    payload: InterviewCreateSchema | InterviewUpdateSchema,
    fallback_resume_id: str | None = None,
) -> None:
    interview.application_id = payload.application_id
    interview.resume_id = payload.resume_id or fallback_resume_id
    interview.round_name = payload.round_name
    interview.round_index = payload.round_index
    interview.scheduled_at = payload.scheduled_at
    interview.interview_type = payload.interview_type
    interview.duration_minutes = payload.duration_minutes
    interview.interviewer_name = payload.interviewer_name
    interview.interviewer_role = payload.interviewer_role
    interview.result = payload.result
    interview.is_reviewed = payload.is_reviewed
    interview.document_title = payload.document_title
    interview.document_content = payload.document_content
    interview.preparation_note = payload.preparation_note
    interview.free_note = payload.free_note
    interview.strength_note = payload.strength_note
    interview.weakness_note = payload.weakness_note
    interview.missing_knowledge_note = payload.missing_knowledge_note
    interview.next_round_prep_note = payload.next_round_prep_note
    interview.follow_up_action = payload.follow_up_action
    interview.follow_up_at = payload.follow_up_at
    interview.need_thank_you = payload.need_thank_you
    interview.need_follow_up = payload.need_follow_up


@router.get("", response_model=InterviewListResponseSchema)
def list_interviews(
    q: str | None = Query(default=None),
    result: str | None = Query(default=None),
    interview_type: str | None = Query(default=None),
    reviewed: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    application_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewListResponseSchema:
    query = (
        select(Interview, Application)
        .join(
            Application,
            and_(
                Application.id == Interview.application_id,
                Application.user_id == current_user.id,
            ),
        )
        .where(Interview.user_id == current_user.id)
    )

    keyword = (q or "").strip()
    if keyword:
        search_pattern = f"%{keyword}%"
        query = query.where(
            or_(
                Application.company_name.ilike(search_pattern),
                Application.job_title.ilike(search_pattern),
                Interview.round_name.ilike(search_pattern),
                Interview.interviewer_name.ilike(search_pattern),
            )
        )
    if result:
        query = query.where(Interview.result == result.strip())
    if interview_type:
        query = query.where(Interview.interview_type == interview_type.strip())
    if reviewed is not None:
        query = query.where(Interview.is_reviewed == reviewed)
    if application_id:
        query = query.where(Interview.application_id == application_id.strip())
    if date_from:
        query = query.where(Interview.scheduled_at >= datetime.combine(date_from, time.min, tzinfo=timezone.utc))
    if date_to:
        query = query.where(Interview.scheduled_at <= datetime.combine(date_to, time.max, tzinfo=timezone.utc))

    rows = db.execute(query.order_by(Interview.scheduled_at.desc().nullslast(), Interview.updated_at.desc())).all()
    items = [_serialize_list_item(interview, application) for interview, application in rows]
    logger.info("interviews_listed user_id=%s count=%s", current_user.id, len(items))
    return InterviewListResponseSchema(items=items)


@router.get("/stats/overview", response_model=InterviewStatsOverviewSchema)
def get_interview_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewStatsOverviewSchema:
    now = datetime.now(timezone.utc)
    week_start = datetime.combine(compute_this_week_start(), time.min, tzinfo=timezone.utc)

    total_count = db.scalar(select(func.count()).select_from(Interview).where(Interview.user_id == current_user.id)) or 0
    this_week_count = db.scalar(
        select(func.count()).select_from(Interview).where(
            Interview.user_id == current_user.id,
            Interview.scheduled_at.is_not(None),
            Interview.scheduled_at >= week_start,
        )
    ) or 0
    upcoming_count = db.scalar(
        select(func.count()).select_from(Interview).where(
            Interview.user_id == current_user.id,
            Interview.scheduled_at.is_not(None),
            Interview.scheduled_at >= now,
            Interview.result == "scheduled",
        )
    ) or 0
    completed_count = db.scalar(
        select(func.count()).select_from(Interview).where(
            Interview.user_id == current_user.id,
            Interview.result.in_(("completed", "passed", "rejected", "offer")),
        )
    ) or 0
    pending_review_count = db.scalar(
        select(func.count()).select_from(Interview).where(
            Interview.user_id == current_user.id,
            Interview.result.in_(("completed", "passed", "rejected", "offer")),
            Interview.is_reviewed.is_(False),
        )
    ) or 0
    passed_count = db.scalar(
        select(func.count()).select_from(Interview).where(
            Interview.user_id == current_user.id,
            Interview.result.in_(("passed", "offer")),
        )
    ) or 0
    rejected_count = db.scalar(
        select(func.count()).select_from(Interview).where(
            Interview.user_id == current_user.id,
            Interview.result == "rejected",
        )
    ) or 0

    return InterviewStatsOverviewSchema(
        total_count=total_count,
        this_week_count=this_week_count,
        upcoming_count=upcoming_count,
        completed_count=completed_count,
        pending_review_count=pending_review_count,
        passed_count=passed_count,
        rejected_count=rejected_count,
    )


@router.get("/{interview_id}", response_model=InterviewReadSchema)
def get_interview(
    interview_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewReadSchema:
    interview = _get_interview_or_404(db, current_user, interview_id)
    application = _ensure_application_owned_by_user(db, current_user, interview.application_id)
    resume = _ensure_resume_owned_by_user(db, current_user, interview.resume_id or application.resume_id)
    return _serialize_read(interview, application, resume_title=resume.title if resume else None)


@router.post("", response_model=InterviewReadSchema, status_code=status.HTTP_201_CREATED)
def create_interview(
    payload: InterviewCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewReadSchema:
    application = _ensure_application_owned_by_user(db, current_user, payload.application_id)
    resume = _ensure_resume_owned_by_user(db, current_user, payload.resume_id or application.resume_id)

    interview = Interview(user_id=current_user.id)
    _apply_interview_payload(interview, payload, fallback_resume_id=application.resume_id)
    db.add(interview)
    db.flush()

    _sync_application_interview_count(db, application)
    _sync_application_status_from_interview(application, interview.result)
    db.add(application)
    db.commit()
    db.refresh(interview)
    logger.info("interview_created user_id=%s interview_id=%s", current_user.id, interview.id)
    return _serialize_read(interview, application, resume_title=resume.title if resume else None)


@router.put("/{interview_id}", response_model=InterviewReadSchema)
def update_interview(
    interview_id: str,
    payload: InterviewUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewReadSchema:
    interview = _get_interview_or_404(db, current_user, interview_id)
    previous_application = _ensure_application_owned_by_user(db, current_user, interview.application_id)
    next_application = _ensure_application_owned_by_user(db, current_user, payload.application_id)
    resume = _ensure_resume_owned_by_user(db, current_user, payload.resume_id or next_application.resume_id)

    _apply_interview_payload(interview, payload, fallback_resume_id=next_application.resume_id)
    db.add(interview)
    db.flush()

    _sync_application_interview_count(db, previous_application)
    db.add(previous_application)
    if previous_application.id != next_application.id:
        _sync_application_interview_count(db, next_application)
    _sync_application_status_from_interview(next_application, interview.result)
    db.add(next_application)

    db.commit()
    db.refresh(interview)
    logger.info("interview_updated user_id=%s interview_id=%s", current_user.id, interview.id)
    return _serialize_read(interview, next_application, resume_title=resume.title if resume else None)


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(
    interview_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    interview = _get_interview_or_404(db, current_user, interview_id)
    application = _ensure_application_owned_by_user(db, current_user, interview.application_id)
    db.delete(interview)
    db.flush()
    _sync_application_interview_count(db, application)
    db.add(application)
    db.commit()
    logger.info("interview_deleted user_id=%s interview_id=%s", current_user.id, interview.id)


@router.patch("/{interview_id}/result", response_model=InterviewReadSchema)
def update_interview_result(
    interview_id: str,
    payload: InterviewResultUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewReadSchema:
    interview = _get_interview_or_404(db, current_user, interview_id)
    application = _ensure_application_owned_by_user(db, current_user, interview.application_id)
    resume = _ensure_resume_owned_by_user(db, current_user, interview.resume_id or application.resume_id)

    interview.result = payload.result
    if payload.result in {"completed", "passed", "rejected", "offer"} and not interview.is_reviewed:
        interview.is_reviewed = payload.result in {"passed", "rejected", "offer"}
    db.add(interview)
    if payload.sync_application_status:
        _sync_application_status_from_interview(application, payload.result)
        db.add(application)
    db.commit()
    db.refresh(interview)
    logger.info("interview_result_updated user_id=%s interview_id=%s result=%s", current_user.id, interview.id, payload.result)
    return _serialize_read(interview, application, resume_title=resume.title if resume else None)


@router.post("/{interview_id}/questions", response_model=InterviewQuestionReadSchema, status_code=status.HTTP_201_CREATED)
def create_interview_question(
    interview_id: str,
    payload: InterviewQuestionCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewQuestionReadSchema:
    interview = _get_interview_or_404(db, current_user, interview_id)
    max_order = db.scalar(
        select(func.max(InterviewQuestionNote.sort_order)).where(InterviewQuestionNote.interview_id == interview.id)
    ) or 0
    question = InterviewQuestionNote(
        user_id=current_user.id,
        interview_id=interview.id,
        sort_order=payload.sort_order or max_order + 1,
        question_text=payload.question_text,
        question_category=payload.question_category,
        answer_note=payload.answer_note,
        follow_up_question=payload.follow_up_question,
        self_evaluation=payload.self_evaluation,
        need_review=payload.need_review,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    logger.info("interview_question_created user_id=%s interview_id=%s question_id=%s", current_user.id, interview.id, question.id)
    return _serialize_question(question)


@router.put("/{interview_id}/questions/{question_id}", response_model=InterviewQuestionReadSchema)
def update_interview_question(
    interview_id: str,
    question_id: str,
    payload: InterviewQuestionUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewQuestionReadSchema:
    _get_interview_or_404(db, current_user, interview_id)
    question = db.scalar(
        select(InterviewQuestionNote).where(
            InterviewQuestionNote.id == question_id,
            InterviewQuestionNote.interview_id == interview_id,
            InterviewQuestionNote.user_id == current_user.id,
        )
    )
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question note not found")

    question.sort_order = payload.sort_order
    question.question_text = payload.question_text
    question.question_category = payload.question_category
    question.answer_note = payload.answer_note
    question.follow_up_question = payload.follow_up_question
    question.self_evaluation = payload.self_evaluation
    question.need_review = payload.need_review
    db.add(question)
    db.commit()
    db.refresh(question)
    logger.info("interview_question_updated user_id=%s interview_id=%s question_id=%s", current_user.id, interview_id, question.id)
    return _serialize_question(question)


@router.delete("/{interview_id}/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview_question(
    interview_id: str,
    question_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _get_interview_or_404(db, current_user, interview_id)
    question = db.scalar(
        select(InterviewQuestionNote).where(
            InterviewQuestionNote.id == question_id,
            InterviewQuestionNote.interview_id == interview_id,
            InterviewQuestionNote.user_id == current_user.id,
        )
    )
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question note not found")
    db.delete(question)
    db.commit()
    logger.info("interview_question_deleted user_id=%s interview_id=%s question_id=%s", current_user.id, interview_id, question.id)
