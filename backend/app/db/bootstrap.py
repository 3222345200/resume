from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def _should_recreate_interview_tables(inspector) -> bool:
    table_names = set(inspector.get_table_names())
    if "interviews" not in table_names:
        return False
    interview_columns = {column["name"] for column in inspector.get_columns("interviews")}
    # Legacy versions used different required columns such as interview_at.
    return "interview_at" in interview_columns


def ensure_runtime_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    statements: list[str] = []

    if _should_recreate_interview_tables(inspector):
        with engine.begin() as connection:
            if "interview_question_notes" in table_names:
                connection.execute(text("DROP TABLE IF EXISTS interview_question_notes CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS interviews CASCADE"))
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())

    if "users" in table_names:
        existing_user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "email" not in existing_user_columns:
            statements.append('ALTER TABLE users ADD COLUMN email VARCHAR(255)')
        if "email_verified" not in existing_user_columns:
            statements.append('ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE')
        statements.append('CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email) WHERE email IS NOT NULL')

    if "resumes" in table_names:
        existing_resume_columns = {column["name"] for column in inspector.get_columns("resumes")}
        if "user_id" not in existing_resume_columns:
            statements.append('ALTER TABLE resumes ADD COLUMN user_id UUID')
        if "pdf_bucket" not in existing_resume_columns:
            statements.append('ALTER TABLE resumes ADD COLUMN pdf_bucket VARCHAR(120)')
        if "pdf_object_key" not in existing_resume_columns:
            statements.append('ALTER TABLE resumes ADD COLUMN pdf_object_key VARCHAR(500)')
        if "pdf_size" not in existing_resume_columns:
            statements.append('ALTER TABLE resumes ADD COLUMN pdf_size INTEGER')
        if "pdf_source_hash" not in existing_resume_columns:
            statements.append('ALTER TABLE resumes ADD COLUMN pdf_source_hash VARCHAR(64)')
        if "pdf_updated_at" not in existing_resume_columns:
            statements.append('ALTER TABLE resumes ADD COLUMN pdf_updated_at TIMESTAMPTZ')
        if "rendered_pdf_url" in existing_resume_columns:
            statements.append('ALTER TABLE resumes DROP COLUMN IF EXISTS rendered_pdf_url CASCADE')
        if "slug" in existing_resume_columns:
            statements.append('ALTER TABLE resumes DROP COLUMN IF EXISTS slug CASCADE')
        if "language" in existing_resume_columns:
            statements.append('ALTER TABLE resumes DROP COLUMN IF EXISTS language CASCADE')
        if "status" in existing_resume_columns:
            statements.append('ALTER TABLE resumes DROP COLUMN IF EXISTS status CASCADE')

    if "applications" in table_names:
        existing_application_columns = {column["name"] for column in inspector.get_columns("applications")}
        if "interview_count" not in existing_application_columns:
            statements.append('ALTER TABLE applications ADD COLUMN interview_count INTEGER NOT NULL DEFAULT 0')

    if "interviews" in table_names:
        existing_interview_columns = {column["name"] for column in inspector.get_columns("interviews")}
        if "document_title" not in existing_interview_columns:
            statements.append("ALTER TABLE interviews ADD COLUMN document_title VARCHAR(200) NOT NULL DEFAULT ''")
        if "document_content" not in existing_interview_columns:
            statements.append("ALTER TABLE interviews ADD COLUMN document_content TEXT NOT NULL DEFAULT ''")

    if statements:
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))
