from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_runtime_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    if "resumes" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("resumes")}
    statements: list[str] = []

    if "user_id" not in existing_columns:
        statements.append('ALTER TABLE resumes ADD COLUMN user_id UUID')
    if "pdf_bucket" not in existing_columns:
        statements.append('ALTER TABLE resumes ADD COLUMN pdf_bucket VARCHAR(120)')
    if "pdf_object_key" not in existing_columns:
        statements.append('ALTER TABLE resumes ADD COLUMN pdf_object_key VARCHAR(500)')
    if "pdf_size" not in existing_columns:
        statements.append('ALTER TABLE resumes ADD COLUMN pdf_size INTEGER')
    if "pdf_updated_at" not in existing_columns:
        statements.append('ALTER TABLE resumes ADD COLUMN pdf_updated_at TIMESTAMPTZ')
    if "rendered_pdf_url" in existing_columns:
        statements.append('ALTER TABLE resumes DROP COLUMN IF EXISTS rendered_pdf_url CASCADE')
    if "slug" in existing_columns:
        statements.append('ALTER TABLE resumes DROP COLUMN IF EXISTS slug CASCADE')
    if "language" in existing_columns:
        statements.append('ALTER TABLE resumes DROP COLUMN IF EXISTS language CASCADE')
    if "status" in existing_columns:
        statements.append('ALTER TABLE resumes DROP COLUMN IF EXISTS status CASCADE')

    if statements:
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))
