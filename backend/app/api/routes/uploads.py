from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import UploadResponseSchema
from app.services.minio_storage import UPLOADS_ROOT, build_avatar_proxy_url, load_object_bytes, upload_user_avatar

ALLOWED_SUFFIXES = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024

router = APIRouter(prefix='/uploads', tags=['uploads'])
logger = get_logger('uploads')


def _avatar_media_type(path: str) -> str:
    suffix = Path(path).suffix.lower()
    return {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
    }.get(suffix, 'application/octet-stream')


@router.post('/avatar', response_model=UploadResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_avatar(
    resume_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UploadResponseSchema:
    resume = db.scalar(select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id))
    if resume is None:
        logger.warning('avatar_upload_resume_missing user_id=%s resume_id=%s', current_user.id, resume_id)
        raise HTTPException(status_code=404, detail='简历不存在')

    suffix = Path(file.filename or '').suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        logger.warning('avatar_upload_invalid_suffix user_id=%s resume_id=%s suffix=%s', current_user.id, resume_id, suffix)
        raise HTTPException(status_code=400, detail='仅支持 jpg、jpeg、png、webp 图片')

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        logger.warning('avatar_upload_too_large user_id=%s resume_id=%s size=%s', current_user.id, resume_id, len(content))
        raise HTTPException(status_code=400, detail='图片不能超过 5MB')

    storage_info = upload_user_avatar(current_user.id, resume_id, suffix, content)
    object_key = str(storage_info['object_key'])
    bucket_name = str(storage_info['bucket'])
    logger.info('avatar_upload_succeeded user_id=%s resume_id=%s bucket=%s object_key=%s size=%s', current_user.id, resume_id, bucket_name, object_key, len(content))
    return UploadResponseSchema(
        url=build_avatar_proxy_url(bucket_name, object_key),
        filename=Path(object_key).name,
    )


@router.get('/avatar/{bucket_name}/{object_path:path}', include_in_schema=False)
def get_avatar(bucket_name: str, object_path: str):
    if bucket_name == 'local':
        local_path = UPLOADS_ROOT / Path(object_path)
        if not local_path.exists():
            logger.warning('avatar_local_missing bucket=%s object_path=%s', bucket_name, object_path)
            raise HTTPException(status_code=404, detail='头像不存在')
        logger.info('avatar_local_served bucket=%s object_path=%s', bucket_name, object_path)
        return FileResponse(local_path)

    avatar_bytes = load_object_bytes(object_path, bucket_name=bucket_name)
    if not avatar_bytes:
        logger.warning('avatar_storage_missing bucket=%s object_path=%s', bucket_name, object_path)
        raise HTTPException(status_code=404, detail='头像不存在')
    logger.info('avatar_storage_served bucket=%s object_path=%s', bucket_name, object_path)
    return Response(
        content=avatar_bytes,
        media_type=_avatar_media_type(object_path),
        headers={
            'Cache-Control': 'private, max-age=300',
        },
    )
