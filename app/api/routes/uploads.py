from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, RedirectResponse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import UploadResponseSchema
from app.services.minio_storage import UPLOADS_ROOT, build_avatar_proxy_url, get_presigned_avatar_url, upload_user_avatar
ALLOWED_SUFFIXES = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024

router = APIRouter(prefix='/uploads', tags=['uploads'])


@router.post('/avatar', response_model=UploadResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_avatar(
    resume_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UploadResponseSchema:
    resume = db.scalar(select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id))
    if resume is None:
        raise HTTPException(status_code=404, detail='简历不存在')

    suffix = Path(file.filename or '').suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail='仅支持 jpg、jpeg、png、webp 图片')

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail='图片不能超过 5MB')

    storage_info = upload_user_avatar(current_user.id, resume_id, suffix, content)
    object_key = str(storage_info["object_key"])
    bucket_name = str(storage_info["bucket"])
    return UploadResponseSchema(
        url=build_avatar_proxy_url(bucket_name, object_key),
        filename=Path(object_key).name,
    )


@router.get('/avatar/{bucket_name}/{object_path:path}', include_in_schema=False)
def get_avatar(bucket_name: str, object_path: str):
    if bucket_name == 'local':
        local_path = UPLOADS_ROOT / Path(object_path)
        if not local_path.exists():
            raise HTTPException(status_code=404, detail='头像不存在')
        return FileResponse(local_path)

    avatar_url = get_presigned_avatar_url(object_path, bucket_name=bucket_name)
    if not avatar_url:
        raise HTTPException(status_code=404, detail='头像不存在')
    return RedirectResponse(url=avatar_url, status_code=307)

