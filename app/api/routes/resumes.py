import hashlib
import json
from datetime import datetime, timezone
from urllib.parse import unquote, urlparse

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.logging import get_logger
from app.core.security import decode_access_token, get_current_user, get_optional_current_user
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import (
    RenderResponseSchema,
    ResumeCreateSchema,
    ResumeListResponseSchema,
    ResumeReadSchema,
    ResumeUpdateSchema,
)
from app.services.html_pdf import render_resume_pdf
from app.services.minio_storage import delete_object, get_presigned_pdf_url, load_object_bytes, upload_user_pdf
from app.services.templates import normalize_template_id

router = APIRouter(prefix='/resumes', tags=['resumes'])
logger = get_logger('resumes')


def _resume_render_hash(resume: Resume) -> str:
    payload = {
        'title': resume.title,
        'template_id': normalize_template_id(resume.template_id),
        'content': resume.content or {},
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()


def _resume_download_name(resume: Resume) -> str:
    content = resume.content if isinstance(resume.content, dict) else {}
    basics = content.get('basics') if isinstance(content.get('basics'), dict) else {}
    name = str(basics.get('name') or '').strip()
    title = str(resume.title or '').strip()
    base = '_'.join(part for part in (name, title) if part) or 'resume'
    return f'{base}.pdf'


def _resume_avatar_storage_ref(resume: Resume) -> tuple[str, str] | None:
    content = resume.content if isinstance(resume.content, dict) else {}
    basics = content.get('basics') if isinstance(content.get('basics'), dict) else {}
    avatar_url = str(basics.get('avatar_url') or '').strip()
    if not avatar_url:
        return None
    path = urlparse(avatar_url).path or avatar_url
    marker = '/api/uploads/avatar/'
    if marker not in path:
        return None
    storage_path = path.split(marker, 1)[1].lstrip('/')
    if '/' not in storage_path:
        return None
    bucket_name, object_name = storage_path.split('/', 1)
    return unquote(object_name), unquote(bucket_name)


def _resume_pdf_url(resume: Resume) -> str | None:
    if not resume.pdf_object_key:
        return None
    if resume.pdf_source_hash != _resume_render_hash(resume):
        return None
    return get_presigned_pdf_url(
        resume.pdf_object_key,
        _resume_download_name(resume),
        bucket_name=resume.pdf_bucket,
    )


def _to_read_schema(resume: Resume) -> ResumeReadSchema:
    return ResumeReadSchema(
        id=resume.id,
        title=resume.title,
        template_id=normalize_template_id(resume.template_id),
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resume not found')
    return resume


@router.get('', response_model=ResumeListResponseSchema)
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeListResponseSchema:
    resumes = db.scalars(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(Resume.updated_at.desc())
    ).all()
    logger.info('resumes_listed user_id=%s count=%s', current_user.id, len(resumes))
    return ResumeListResponseSchema(items=[_to_read_schema(item) for item in resumes])


@router.get('/{resume_id}', response_model=ResumeReadSchema)
def get_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeReadSchema:
    resume = _get_resume_or_404(resume_id, db, current_user)
    logger.info('resume_loaded user_id=%s resume_id=%s', current_user.id, resume.id)
    return _to_read_schema(resume)


@router.post('', response_model=ResumeReadSchema, status_code=status.HTTP_201_CREATED)
def create_resume(
    payload: ResumeCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeReadSchema:
    resume = Resume(
        user_id=current_user.id,
        title=payload.title,
        template_id=normalize_template_id(payload.template_id),
        content=payload.content.model_dump(),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    logger.info('resume_created user_id=%s resume_id=%s template_id=%s title=%s', current_user.id, resume.id, resume.template_id, resume.title)
    return _to_read_schema(resume)


@router.put('/{resume_id}', response_model=ResumeReadSchema)
def update_resume(
    resume_id: str,
    payload: ResumeUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeReadSchema:
    resume = _get_resume_or_404(resume_id, db, current_user)
    resume.title = payload.title
    resume.template_id = normalize_template_id(payload.template_id)
    resume.content = payload.content.model_dump()
    db.add(resume)
    db.commit()
    db.refresh(resume)
    logger.info('resume_updated user_id=%s resume_id=%s template_id=%s title=%s', current_user.id, resume.id, resume.template_id, resume.title)
    return _to_read_schema(resume)


@router.post('/{resume_id}/render', response_model=RenderResponseSchema)
def render_resume(
    resume_id: str,
    payload: ResumeUpdateSchema | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RenderResponseSchema:
    resume = _get_resume_or_404(resume_id, db, current_user)
    logger.info('resume_render_requested user_id=%s resume_id=%s', current_user.id, resume.id)
    if payload is not None:
        resume.title = payload.title
        resume.template_id = normalize_template_id(payload.template_id)
        resume.content = payload.content.model_dump()
        db.add(resume)
        db.commit()
        db.refresh(resume)
        logger.info('resume_render_payload_applied user_id=%s resume_id=%s', current_user.id, resume.id)

    current_hash = _resume_render_hash(resume)
    cached_pdf_url = _resume_pdf_url(resume)
    if cached_pdf_url and resume.pdf_source_hash == current_hash:
        logger.info('resume_render_cache_hit user_id=%s resume_id=%s', current_user.id, resume.id)
        return RenderResponseSchema(
            message='PDF ready',
            pdf_url=cached_pdf_url,
            resume=_to_read_schema(resume),
        )
    try:
        pdf_bytes = render_resume_pdf(resume)
        storage_info = upload_user_pdf(current_user.id, resume.id, pdf_bytes)
    except RuntimeError as exc:
        logger.exception('resume_render_failed user_id=%s resume_id=%s', current_user.id, resume.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    resume.pdf_bucket = str(storage_info['bucket'])
    resume.pdf_object_key = str(storage_info['object_key'])
    resume.pdf_size = int(storage_info['size'])
    resume.pdf_source_hash = current_hash
    resume.pdf_updated_at = datetime.now(timezone.utc)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    logger.info('resume_render_succeeded user_id=%s resume_id=%s bucket=%s object_key=%s size=%s', current_user.id, resume.id, resume.pdf_bucket, resume.pdf_object_key, resume.pdf_size)

    pdf_url = _resume_pdf_url(resume)
    if not pdf_url:
        logger.error('resume_render_uploaded_but_url_missing user_id=%s resume_id=%s', current_user.id, resume.id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='PDF upload failed')
    return RenderResponseSchema(
        message='PDF generated',
        pdf_url=pdf_url,
        resume=_to_read_schema(resume),
    )


@router.get('/{resume_id}/pdf', response_model=RenderResponseSchema)
def get_resume_pdf(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RenderResponseSchema:
    resume = _get_resume_or_404(resume_id, db, current_user)
    pdf_url = _resume_pdf_url(resume)
    if not pdf_url:
        logger.warning('resume_pdf_missing user_id=%s resume_id=%s', current_user.id, resume.id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='PDF not generated')
    logger.info('resume_pdf_ready user_id=%s resume_id=%s', current_user.id, resume.id)
    return RenderResponseSchema(message='PDF ready', pdf_url=pdf_url)


@router.get('/{resume_id}/pdf/inline', include_in_schema=False)
def preview_resume_pdf(
    resume_id: str,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> Response:
    if current_user is None:
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='请先登录')
        payload = decode_access_token(token)
        username = str(payload.get('sub') or '').strip()
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='请先登录')
        current_user = db.query(User).filter(User.username == username).first()
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='请先登录')

    resume = _get_resume_or_404(resume_id, db, current_user)
    if not resume.pdf_object_key or resume.pdf_source_hash != _resume_render_hash(resume):
        logger.warning('resume_pdf_inline_missing user_id=%s resume_id=%s', current_user.id, resume.id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='PDF not generated')

    pdf_bytes = load_object_bytes(resume.pdf_object_key, bucket_name=resume.pdf_bucket)
    if not pdf_bytes:
        logger.warning('resume_pdf_inline_storage_missing user_id=%s resume_id=%s object_key=%s', current_user.id, resume.id, resume.pdf_object_key)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='PDF not found')

    logger.info('resume_pdf_inline_served user_id=%s resume_id=%s', current_user.id, resume.id)
    safe_name = 'resume.pdf'
    return Response(
        content=pdf_bytes,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'inline; filename="{safe_name}"',
            'Cache-Control': 'private, max-age=300',
        },
    )


@router.delete('/{resume_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    resume = _get_resume_or_404(resume_id, db, current_user)
    pdf_object_name = resume.pdf_object_key
    pdf_bucket_name = resume.pdf_bucket
    avatar_ref = _resume_avatar_storage_ref(resume)
    db.delete(resume)
    db.commit()
    delete_object(pdf_object_name, bucket_name=pdf_bucket_name)
    if avatar_ref:
        avatar_object_name, avatar_bucket_name = avatar_ref
        delete_object(avatar_object_name, bucket_name=avatar_bucket_name)
    logger.info('resume_deleted user_id=%s resume_id=%s', current_user.id, resume.id)
