from __future__ import annotations

from datetime import timedelta
from io import BytesIO
from pathlib import Path

from minio import Minio
from minio.error import S3Error
from urllib3 import PoolManager, Retry, Timeout

from app.core.config import settings

UPLOADS_ROOT = Path(__file__).resolve().parent.parent.parent / "uploads"
LOCAL_PDF_ROOT = UPLOADS_ROOT / "generated"
LOCAL_AVATAR_ROOT = UPLOADS_ROOT / "avatars"


def _build_client(endpoint: str) -> Minio:
    return Minio(
        endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
        http_client=PoolManager(
            timeout=Timeout(connect=1.0, read=2.0),
            retries=Retry(total=0, connect=0, read=0, redirect=0),
        ),
    )


def get_minio_client() -> Minio:
    return _build_client(settings.minio_endpoint)


def get_minio_public_client() -> Minio:
    return _build_client(settings.minio_public_endpoint)


def ensure_bucket_exists() -> None:
    LOCAL_PDF_ROOT.mkdir(parents=True, exist_ok=True)
    LOCAL_AVATAR_ROOT.mkdir(parents=True, exist_ok=True)
    try:
        client = get_minio_client()
        if not client.bucket_exists(settings.minio_bucket):
            client.make_bucket(settings.minio_bucket)
    except Exception:
        # Fall back to local filesystem storage when MinIO is unavailable.
        return


def get_user_pdf_object_name(user_id: str, resume_id: str) -> str:
    prefix = settings.minio_pdf_prefix.strip("/ ")
    return f"{prefix}/{user_id}/{resume_id}.pdf"


AVATAR_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")


def get_resume_avatar_object_name(user_id: str, resume_id: str, suffix: str) -> str:
    prefix = settings.minio_avatar_prefix.strip("/ ")
    normalized = suffix.lower()
    return f"{prefix}/{user_id}/{resume_id}/avatar{normalized}"


def _delete_resume_avatar_variants(user_id: str, resume_id: str) -> None:
    prefix = settings.minio_avatar_prefix.strip("/ ")
    object_names = [f"{prefix}/{user_id}/{resume_id}/avatar{suffix}" for suffix in AVATAR_SUFFIXES]
    for object_name in object_names:
        try:
            delete_object(object_name, bucket_name=settings.minio_bucket)
        except Exception:
            pass
        local_path = UPLOADS_ROOT / Path(object_name)
        if local_path.exists():
            local_path.unlink()


def _avatar_content_type(suffix: str) -> str:
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(suffix.lower(), "application/octet-stream")


def _save_local_pdf(user_id: str, resume_id: str, pdf_bytes: bytes) -> dict[str, str | int]:
    relative_path = Path("generated") / user_id / f"{resume_id}.pdf"
    target_path = UPLOADS_ROOT / relative_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(pdf_bytes)
    return {
        "bucket": "local",
        "object_key": relative_path.as_posix(),
        "size": len(pdf_bytes),
        "etag": "",
    }


def upload_user_pdf(user_id: str, resume_id: str, pdf_bytes: bytes) -> dict[str, str | int]:
    ensure_bucket_exists()
    object_name = get_user_pdf_object_name(user_id, resume_id)
    try:
        client = get_minio_client()
        result = client.put_object(
            settings.minio_bucket,
            object_name,
            data=BytesIO(pdf_bytes),
            length=len(pdf_bytes),
            content_type="application/pdf",
        )
        return {
            "bucket": settings.minio_bucket,
            "object_key": object_name,
            "size": len(pdf_bytes),
            "etag": result.etag,
        }
    except Exception:
        return _save_local_pdf(user_id, resume_id, pdf_bytes)


def _save_local_avatar(user_id: str, resume_id: str, suffix: str, content: bytes) -> dict[str, str | int]:
    relative_path = Path(get_resume_avatar_object_name(user_id, resume_id, suffix))
    target_path = UPLOADS_ROOT / relative_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(content)
    return {
        "bucket": "local",
        "object_key": relative_path.as_posix(),
        "size": len(content),
        "etag": "",
    }


def upload_user_avatar(user_id: str, resume_id: str, suffix: str, content: bytes) -> dict[str, str | int]:
    ensure_bucket_exists()
    _delete_resume_avatar_variants(user_id, resume_id)
    object_name = get_resume_avatar_object_name(user_id, resume_id, suffix)
    try:
        client = get_minio_client()
        result = client.put_object(
            settings.minio_bucket,
            object_name,
            data=BytesIO(content),
            length=len(content),
            content_type=_avatar_content_type(suffix),
        )
        return {
            "bucket": settings.minio_bucket,
            "object_key": object_name,
            "size": len(content),
            "etag": result.etag,
        }
    except Exception:
        return _save_local_avatar(user_id, resume_id, suffix, content)


def build_avatar_proxy_url(bucket_name: str, object_name: str) -> str:
    return f"/api/uploads/avatar/{bucket_name}/{object_name.lstrip('/')}"


def get_presigned_avatar_url(
    object_name: str,
    bucket_name: str | None = None,
) -> str | None:
    if not object_name:
        return None
    bucket = bucket_name or settings.minio_bucket
    if bucket == "local":
        local_path = UPLOADS_ROOT / Path(object_name)
        if not local_path.exists():
            return None
        return f"/uploads/{Path(object_name).as_posix()}"

    client = get_minio_client()
    try:
        client.stat_object(bucket, object_name)
    except S3Error as exc:
        if exc.code in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
            return None
        raise

    public_client = get_minio_public_client()
    return public_client.presigned_get_object(
        bucket,
        object_name,
        expires=timedelta(minutes=settings.minio_presigned_expire_minutes),
    )


def load_object_bytes(object_name: str, bucket_name: str | None = None) -> bytes | None:
    if not object_name:
        return None
    bucket = bucket_name or settings.minio_bucket
    if bucket == "local":
        local_path = UPLOADS_ROOT / Path(object_name)
        if not local_path.exists():
            return None
        return local_path.read_bytes()

    client = get_minio_client()
    try:
        response = client.get_object(bucket, object_name)
    except S3Error as exc:
        if exc.code in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
            return None
        raise
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def get_presigned_pdf_url(
    object_name: str,
    filename: str = "resume.pdf",
    bucket_name: str | None = None,
) -> str | None:
    if not object_name:
        return None
    bucket = bucket_name or settings.minio_bucket
    if bucket == "local":
        local_path = UPLOADS_ROOT / Path(object_name)
        if not local_path.exists():
            return None
        return f"/uploads/{Path(object_name).as_posix()}"

    client = get_minio_client()

    try:
        client.stat_object(bucket, object_name)
    except S3Error as exc:
        if exc.code in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
            return None
        raise

    public_client = get_minio_public_client()
    safe_filename = filename.replace('"', "").strip() or "resume.pdf"
    return public_client.presigned_get_object(
        bucket,
        object_name,
        expires=timedelta(minutes=settings.minio_presigned_expire_minutes),
        response_headers={
            "response-content-type": "application/pdf",
            "response-content-disposition": f'inline; filename="{safe_filename}"',
        },
    )


def delete_object(object_name: str | None, bucket_name: str | None = None) -> None:
    if not object_name:
        return
    bucket = bucket_name or settings.minio_bucket
    if bucket == "local":
        local_path = UPLOADS_ROOT / Path(object_name)
        if local_path.exists():
            local_path.unlink()
        return

    client = get_minio_client()
    try:
        client.remove_object(bucket, object_name)
    except S3Error as exc:
        if exc.code not in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
            raise
