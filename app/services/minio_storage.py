from __future__ import annotations

from datetime import timedelta
from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.core.config import settings


def _build_client(endpoint: str) -> Minio:
    return Minio(
        endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def get_minio_client() -> Minio:
    return _build_client(settings.minio_endpoint)


def get_minio_public_client() -> Minio:
    return _build_client(settings.minio_public_endpoint)


def ensure_bucket_exists() -> None:
    client = get_minio_client()
    if not client.bucket_exists(settings.minio_bucket):
        client.make_bucket(settings.minio_bucket)


def get_user_pdf_object_name(user_id: str, resume_id: str) -> str:
    prefix = settings.minio_pdf_prefix.strip("/ ")
    return f"{prefix}/{user_id}/{resume_id}.pdf"


def upload_user_pdf(user_id: str, resume_id: str, pdf_bytes: bytes) -> dict[str, str | int]:
    ensure_bucket_exists()
    object_name = get_user_pdf_object_name(user_id, resume_id)
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


def get_presigned_pdf_url(
    object_name: str,
    filename: str = "resume.pdf",
    bucket_name: str | None = None,
) -> str | None:
    if not object_name:
        return None
    bucket = bucket_name or settings.minio_bucket
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
    client = get_minio_client()
    try:
        client.remove_object(bucket, object_name)
    except S3Error as exc:
        if exc.code not in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
            raise
