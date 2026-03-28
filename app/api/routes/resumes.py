from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import (
    RenderResponseSchema,
    ResumeCreateSchema,
    ResumeListResponseSchema,
    ResumeReadSchema,
    ResumeUpdateSchema,
)
from app.services.latex import render_resume_pdf
from app.services.minio_storage import delete_object, get_presigned_pdf_url, upload_user_pdf

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _resume_pdf_url(resume: Resume) -> str | None:
    if not resume.pdf_object_key:
        return None
    return get_presigned_pdf_url(
        resume.pdf_object_key,
        f"{resume.title}.pdf",
        bucket_name=resume.pdf_bucket,
    )


def _to_read_schema(resume: Resume) -> ResumeReadSchema:
    return ResumeReadSchema(
        id=resume.id,
        title=resume.title,
        template_id=resume.template_id,
        slug=resume.slug,
        language=resume.language,
        status=resume.status,
        content=resume.content,
        rendered_pdf_url=_resume_pdf_url(resume),
        created_at=resume.created_at.isoformat(),
        updated_at=resume.updated_at.isoformat(),
    )


def _get_resume_or_404(resume_id: str, db: Session, current_user: User) -> Resume:
    resume = db.scalar(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
    )
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume


@router.get("", response_model=ResumeListResponseSchema)
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeListResponseSchema:
    resumes = db.scalars(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(Resume.updated_at.desc())
    ).all()
    return ResumeListResponseSchema(items=[_to_read_schema(item) for item in resumes])


@router.get("/{resume_id}", response_model=ResumeReadSchema)
def get_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeReadSchema:
    return _to_read_schema(_get_resume_or_404(resume_id, db, current_user))


@router.post("", response_model=ResumeReadSchema, status_code=status.HTTP_201_CREATED)
def create_resume(
    payload: ResumeCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeReadSchema:
    resume = Resume(
        user_id=current_user.id,
        title=payload.title,
        template_id=payload.template_id,
        slug=payload.slug,
        language=payload.language,
        status=payload.status,
        content=payload.content.model_dump(),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return _to_read_schema(resume)


@router.put("/{resume_id}", response_model=ResumeReadSchema)
def update_resume(
    resume_id: str,
    payload: ResumeUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeReadSchema:
    resume = _get_resume_or_404(resume_id, db, current_user)
    resume.title = payload.title
    resume.template_id = payload.template_id
    resume.slug = payload.slug
    resume.language = payload.language
    resume.status = payload.status
    resume.content = payload.content.model_dump()
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return _to_read_schema(resume)


@router.post("/{resume_id}/render", response_model=RenderResponseSchema)
def render_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RenderResponseSchema:
    resume = _get_resume_or_404(resume_id, db, current_user)
    try:
        pdf_bytes = render_resume_pdf(resume)
        storage_info = upload_user_pdf(current_user.id, resume.id, pdf_bytes)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    resume.pdf_bucket = str(storage_info["bucket"])
    resume.pdf_object_key = str(storage_info["object_key"])
    resume.pdf_size = int(storage_info["size"])
    resume.pdf_updated_at = datetime.now(timezone.utc)
    db.add(resume)
    db.commit()
    db.refresh(resume)

    pdf_url = _resume_pdf_url(resume)
    if not pdf_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="PDF upload failed")
    return RenderResponseSchema(message="PDF generated", pdf_url=pdf_url)


@router.get("/{resume_id}/pdf", response_model=RenderResponseSchema)
def get_resume_pdf(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RenderResponseSchema:
    resume = _get_resume_or_404(resume_id, db, current_user)
    pdf_url = _resume_pdf_url(resume)
    if not pdf_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not generated")
    return RenderResponseSchema(message="PDF ready", pdf_url=pdf_url)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    resume = _get_resume_or_404(resume_id, db, current_user)
    object_name = resume.pdf_object_key
    bucket_name = resume.pdf_bucket
    db.delete(resume)
    db.commit()
    delete_object(object_name, bucket_name=bucket_name)
