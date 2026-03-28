from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.resume import UploadResponseSchema

UPLOAD_ROOT = Path('uploads/avatars')
ALLOWED_SUFFIXES = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024

router = APIRouter(prefix='/uploads', tags=['uploads'])


@router.post('/avatar', response_model=UploadResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> UploadResponseSchema:
    suffix = Path(file.filename or '').suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail='仅支持 jpg、jpeg、png、webp 图片')

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail='图片不能超过 5MB')

    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    filename = f'{uuid4()}{suffix}'
    path = UPLOAD_ROOT / filename
    path.write_bytes(content)
    return UploadResponseSchema(url=f'/uploads/avatars/{filename}', filename=filename)
