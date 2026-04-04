from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_runtime_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    statements: list[str] = []

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

    if statements:
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))
