from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.db import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.models.application import Application, ApplicationStatusHistory
from app.models.resume import Resume
from app.models.user import User
from app.schemas.application import (
    ApplicationCreateSchema,
    ApplicationDetailSchema,
    ApplicationFollowUpUpdateSchema,
    ApplicationListResponseSchema,
    ApplicationReadSchema,
    ApplicationStatsOverviewSchema,
    ApplicationStatusHistoryReadSchema,
    ApplicationStatusUpdateSchema,
    ApplicationUpdateSchema,
    compute_application_todo,
)

router = APIRouter(prefix="/applications", tags=["applications"])
logger = get_logger("applications")


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _serialize_application(item: Application, resume_title: str | None = None) -> ApplicationReadSchema:
    todo = compute_application_todo(item.next_follow_up_at)
    return ApplicationReadSchema(
        id=item.id,
        company_name=item.company_name,
        job_title=item.job_title,
        department=item.department,
        city=item.city,
        job_link=item.job_link,
        jd_summary=item.jd_summary,
        salary_range=item.salary_range,
        job_type=item.job_type,
        applied_at=item.applied_at.isoformat(),
        status=item.status,
        status_updated_at=item.status_updated_at.isoformat(),
        last_follow_up_at=_serialize_datetime(item.last_follow_up_at),
        next_follow_up_at=_serialize_datetime(item.next_follow_up_at),
        is_todo=todo,
        final_result=item.final_result,
        channel=item.channel,
        referrer_name=item.referrer_name,
        contact_name=item.contact_name,
        contact_value=item.contact_value,
        resume_id=item.resume_id,
        resume_title=resume_title,
        interview_count=item.interview_count,
        note=item.note,
        risk_note=item.risk_note,
        priority=item.priority,
        next_action=item.next_action,
        deadline_at=_serialize_datetime(item.deadline_at),
        created_at=item.created_at.isoformat(),
        updated_at=item.updated_at.isoformat(),
    )


def _serialize_detail(item: Application, resume_title: str | None = None) -> ApplicationDetailSchema:
    base_payload = _serialize_application(item, resume_title=resume_title).model_dump()
    history_items = [
        ApplicationStatusHistoryReadSchema(
            id=history.id,
            from_status=history.from_status,
            to_status=history.to_status,
            note=history.note,
            changed_at=history.changed_at.isoformat(),
        )
        for history in item.status_histories
    ]
    return ApplicationDetailSchema(**base_payload, status_history=history_items)


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


def _get_application_or_404(db: Session, current_user: User, application_id: str) -> Application:
    application = db.scalar(
        select(Application)
        .options(joinedload(Application.status_histories))
        .where(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


def _sync_todo_state(application: Application) -> None:
    application.is_todo = compute_application_todo(application.next_follow_up_at)


def _create_status_history(
    application: Application,
    current_user: User,
    from_status: str,
    to_status: str,
    note: str = "",
) -> ApplicationStatusHistory:
    return ApplicationStatusHistory(
        application_id=application.id,
        from_status=from_status,
        to_status=to_status,
        note=note,
        changed_at=datetime.now(timezone.utc),
        operator_user_id=current_user.id,
    )


def _apply_application_payload(application: Application, payload: ApplicationCreateSchema | ApplicationUpdateSchema) -> None:
    application.company_name = payload.company_name
    application.job_title = payload.job_title
    application.department = payload.department
    application.city = payload.city
    application.job_link = payload.job_link
    application.jd_summary = payload.jd_summary
    application.salary_range = payload.salary_range
    application.job_type = payload.job_type
    application.applied_at = payload.applied_at
    application.status = payload.status
    application.channel = payload.channel
    application.referrer_name = payload.referrer_name
    application.contact_name = payload.contact_name
    application.contact_value = payload.contact_value
    application.resume_id = payload.resume_id
    application.note = payload.note
    application.risk_note = payload.risk_note
    application.priority = payload.priority
    application.next_action = payload.next_action
    application.last_follow_up_at = payload.last_follow_up_at
    application.next_follow_up_at = payload.next_follow_up_at
    application.deadline_at = payload.deadline_at
    application.final_result = payload.final_result
    application.interview_count = payload.interview_count
    _sync_todo_state(application)


@router.get("", response_model=ApplicationListResponseSchema)
def list_applications(
    q: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias="status"),
    channel: str | None = Query(default=None),
    city: str | None = Query(default=None),
    follow_up_only: bool = Query(default=False),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    resume_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationListResponseSchema:
    query = (
        select(Application, Resume.title.label("resume_title"))
        .outerjoin(
            Resume,
            and_(
                Resume.id == Application.resume_id,
                Resume.user_id == current_user.id,
            ),
        )
        .where(Application.user_id == current_user.id)
    )

    keyword = (q or "").strip()
    if keyword:
        search_pattern = f"%{keyword}%"
        query = query.where(
            or_(
                Application.company_name.ilike(search_pattern),
                Application.job_title.ilike(search_pattern),
            )
        )

    if status_value:
        query = query.where(Application.status == status_value.strip())
    if channel:
        query = query.where(Application.channel == channel.strip())
    if city:
        query = query.where(Application.city == city.strip())
    if resume_id:
        query = query.where(Application.resume_id == resume_id.strip())
    if date_from:
        query = query.where(Application.applied_at >= date_from)
    if date_to:
        query = query.where(Application.applied_at <= date_to)
    if follow_up_only:
        now = datetime.now(timezone.utc)
        query = query.where(Application.next_follow_up_at.is_not(None), Application.next_follow_up_at <= now)

    rows = db.execute(query.order_by(Application.updated_at.desc(), Application.created_at.desc())).all()
    items = [_serialize_application(application, resume_title=resume_title) for application, resume_title in rows]
    logger.info("applications_listed user_id=%s count=%s", current_user.id, len(items))
    return ApplicationListResponseSchema(items=items)


@router.get("/stats/overview", response_model=ApplicationStatsOverviewSchema)
def get_application_overview_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationStatsOverviewSchema:
    now = datetime.now(timezone.utc)
    week_start = date.today() - timedelta(days=date.today().weekday())
    stale_before = now - timedelta(days=14)

    total_count = db.scalar(select(func.count()).select_from(Application).where(Application.user_id == current_user.id)) or 0
    new_this_week = db.scalar(
        select(func.count()).select_from(Application).where(
            Application.user_id == current_user.id,
            Application.applied_at >= week_start,
        )
    ) or 0
    interviewing_count = db.scalar(
        select(func.count()).select_from(Application).where(
            Application.user_id == current_user.id,
            Application.status.in_(("面试中", "HR 面")),
        )
    ) or 0
    offer_count = db.scalar(
        select(func.count()).select_from(Application).where(
            Application.user_id == current_user.id,
            Application.status == "Offer",
        )
    ) or 0
    rejected_count = db.scalar(
        select(func.count()).select_from(Application).where(
            Application.user_id == current_user.id,
            Application.status == "已拒绝",
        )
    ) or 0
    no_feedback_count = db.scalar(
        select(func.count()).select_from(Application).where(
            Application.user_id == current_user.id,
            Application.status.not_in(("Offer", "已拒绝", "已结束")),
            Application.applied_at <= stale_before.date(),
            or_(Application.last_follow_up_at.is_(None), Application.last_follow_up_at <= stale_before),
        )
    ) or 0
    todo_count = db.scalar(
        select(func.count()).select_from(Application).where(
            Application.user_id == current_user.id,
            Application.next_follow_up_at.is_not(None),
            Application.next_follow_up_at <= now,
        )
    ) or 0

    return ApplicationStatsOverviewSchema(
        total_count=total_count,
        new_this_week=new_this_week,
        interviewing_count=interviewing_count,
        offer_count=offer_count,
        rejected_count=rejected_count,
        no_feedback_count=no_feedback_count,
        todo_count=todo_count,
    )


@router.get("/{application_id}", response_model=ApplicationDetailSchema)
def get_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationDetailSchema:
    application = _get_application_or_404(db, current_user, application_id)
    resume = _ensure_resume_owned_by_user(db, current_user, application.resume_id) if application.resume_id else None
    logger.info("application_loaded user_id=%s application_id=%s", current_user.id, application.id)
    return _serialize_detail(application, resume_title=resume.title if resume else None)


@router.post("", response_model=ApplicationReadSchema, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationReadSchema:
    resume = _ensure_resume_owned_by_user(db, current_user, payload.resume_id)
    status_updated_at = datetime.now(timezone.utc)
    application = Application(
        user_id=current_user.id,
        status_updated_at=status_updated_at,
    )
    _apply_application_payload(application, payload)
    db.add(application)
    db.flush()
    db.add(
        _create_status_history(
            application=application,
            current_user=current_user,
            from_status="",
            to_status=application.status,
            note="创建投递记录",
        )
    )
    db.commit()
    db.refresh(application)
    logger.info("application_created user_id=%s application_id=%s", current_user.id, application.id)
    return _serialize_application(application, resume_title=resume.title if resume else None)


@router.put("/{application_id}", response_model=ApplicationReadSchema)
def update_application(
    application_id: str,
    payload: ApplicationUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationReadSchema:
    application = _get_application_or_404(db, current_user, application_id)
    resume = _ensure_resume_owned_by_user(db, current_user, payload.resume_id)
    previous_status = application.status
    _apply_application_payload(application, payload)
    if previous_status != application.status:
        application.status_updated_at = datetime.now(timezone.utc)
        db.add(
            _create_status_history(
                application=application,
                current_user=current_user,
                from_status=previous_status,
                to_status=application.status,
                note="编辑投递记录并更新状态",
            )
        )
    db.add(application)
    db.commit()
    db.refresh(application)
    logger.info("application_updated user_id=%s application_id=%s", current_user.id, application.id)
    return _serialize_application(application, resume_title=resume.title if resume else None)


@router.patch("/{application_id}/status", response_model=ApplicationReadSchema)
def update_application_status(
    application_id: str,
    payload: ApplicationStatusUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationReadSchema:
    application = _get_application_or_404(db, current_user, application_id)
    previous_status = application.status
    application.status = payload.status
    application.status_updated_at = datetime.now(timezone.utc)
    if payload.status == "Offer":
        application.final_result = "Offer"
    elif payload.status == "已拒绝":
        application.final_result = "已拒绝"
    elif payload.status == "已结束":
        application.final_result = "已结束"
    db.add(application)
    db.add(
        _create_status_history(
            application=application,
            current_user=current_user,
            from_status=previous_status,
            to_status=payload.status,
            note=payload.note,
        )
    )
    db.commit()
    db.refresh(application)
    resume = _ensure_resume_owned_by_user(db, current_user, application.resume_id) if application.resume_id else None
    logger.info("application_status_updated user_id=%s application_id=%s status=%s", current_user.id, application.id, payload.status)
    return _serialize_application(application, resume_title=resume.title if resume else None)


@router.patch("/{application_id}/follow-up", response_model=ApplicationReadSchema)
def update_application_follow_up(
    application_id: str,
    payload: ApplicationFollowUpUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationReadSchema:
    application = _get_application_or_404(db, current_user, application_id)
    application.last_follow_up_at = payload.last_follow_up_at
    application.next_follow_up_at = payload.next_follow_up_at
    application.next_action = payload.next_action
    _sync_todo_state(application)
    db.add(application)
    db.commit()
    db.refresh(application)
    resume = _ensure_resume_owned_by_user(db, current_user, application.resume_id) if application.resume_id else None
    logger.info("application_follow_up_updated user_id=%s application_id=%s", current_user.id, application.id)
    return _serialize_application(application, resume_title=resume.title if resume else None)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    application = _get_application_or_404(db, current_user, application_id)
    db.delete(application)
    db.commit()
    logger.info("application_deleted user_id=%s application_id=%s", current_user.id, application.id)
