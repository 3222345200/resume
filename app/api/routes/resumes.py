from pathlib import Path
import shutil

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.resume import Resume
from app.schemas.resume import (
    RenderResponseSchema,
    ResumeCreateSchema,
    ResumeListResponseSchema,
    ResumeReadSchema,
    ResumeUpdateSchema,
)
from app.services.latex import OUTPUT_ROOT, render_resume_pdf

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _to_read_schema(resume: Resume) -> ResumeReadSchema:
    return ResumeReadSchema(
        id=resume.id,
        title=resume.title,
        template_id=resume.template_id,
        slug=resume.slug,
        language=resume.language,
        status=resume.status,
        content=resume.content,
        rendered_pdf_url=resume.rendered_pdf_url,
        created_at=resume.created_at.isoformat(),
        updated_at=resume.updated_at.isoformat(),
    )


def _get_resume_or_404(resume_id: str, db: Session) -> Resume:
    resume = db.get(Resume, resume_id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume


def _pdf_path_for_resume(resume_id: str) -> Path:
    return OUTPUT_ROOT / resume_id / 'resume.pdf'


@router.get("", response_model=ResumeListResponseSchema)
def list_resumes(db: Session = Depends(get_db)) -> ResumeListResponseSchema:
    resumes = db.scalars(select(Resume).order_by(Resume.updated_at.desc())).all()
    return ResumeListResponseSchema(items=[_to_read_schema(item) for item in resumes])


@router.get("/{resume_id}", response_model=ResumeReadSchema)
def get_resume(resume_id: str, db: Session = Depends(get_db)) -> ResumeReadSchema:
    return _to_read_schema(_get_resume_or_404(resume_id, db))


@router.post("", response_model=ResumeReadSchema, status_code=status.HTTP_201_CREATED)
def create_resume(payload: ResumeCreateSchema, db: Session = Depends(get_db)) -> ResumeReadSchema:
    resume = Resume(
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
) -> ResumeReadSchema:
    resume = _get_resume_or_404(resume_id, db)
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
def render_resume(resume_id: str, db: Session = Depends(get_db)) -> RenderResponseSchema:
    resume = _get_resume_or_404(resume_id, db)
    try:
        render_resume_pdf(resume)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    resume.rendered_pdf_url = f"/api/resumes/{resume.id}/pdf"
    db.add(resume)
    db.commit()
    return RenderResponseSchema(message="PDF generated", pdf_url=resume.rendered_pdf_url)


@router.get("/{resume_id}/pdf")
def download_resume_pdf(resume_id: str, db: Session = Depends(get_db)) -> FileResponse:
    resume = _get_resume_or_404(resume_id, db)
    pdf_path = _pdf_path_for_resume(resume.id)
    if not resume.rendered_pdf_url or not pdf_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not generated")
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{resume.title}.pdf",
        content_disposition_type="inline",
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: str, db: Session = Depends(get_db)) -> None:
    resume = _get_resume_or_404(resume_id, db)
    output_dir = OUTPUT_ROOT / resume.id
    if output_dir.exists():
        shutil.rmtree(output_dir)
    db.delete(resume)
    db.commit()
