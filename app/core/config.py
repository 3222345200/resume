from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Resume Backend"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_debug: bool = True
    database_url: str = "postgresql+psycopg://postgres:ResumeTemp%232026%21@127.0.0.1:5432/resume_app"
    auth_secret_key: str = "change-me-before-production"
    auth_token_expire_minutes: int = 60 * 24 * 7
    minio_endpoint: str = "127.0.0.1:9000"
    minio_public_endpoint: str = "127.0.0.1:9000"
    minio_access_key: str = "resumeadmin"
    minio_secret_key: str = "ResumeMinio#2026"
    minio_bucket: str = "resume-pdfs"
    minio_secure: bool = False
    minio_pdf_prefix: str = "resumes"
    minio_presigned_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
