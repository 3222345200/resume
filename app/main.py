from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

import app.models  # noqa: F401
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.resumes import router as resumes_router
from app.api.routes.templates import router as templates_router
from app.api.routes.uploads import router as uploads_router
from app.core.config import settings
from app.core.db import engine
from app.db.base import Base
from app.db.bootstrap import ensure_runtime_schema
from app.services.minio_storage import ensure_bucket_exists

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / 'frontend'
UPLOADS_DIR = BASE_DIR / 'uploads'
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
)

app.mount('/assets', StaticFiles(directory=str(FRONTEND_DIR)), name='assets')
app.mount('/uploads', StaticFiles(directory=str(UPLOADS_DIR)), name='uploads')
app.include_router(health_router, prefix='/api')
app.include_router(auth_router, prefix='/api')
app.include_router(templates_router, prefix='/api')
app.include_router(resumes_router, prefix='/api')
app.include_router(uploads_router, prefix='/api')


@app.on_event('startup')
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_runtime_schema(engine)
    ensure_bucket_exists()


@app.get('/', include_in_schema=False)
def index() -> RedirectResponse:
    return RedirectResponse(url='/login', status_code=302)


@app.get('/login', include_in_schema=False)
def login_page() -> HTMLResponse:
    html = (FRONTEND_DIR / 'login.html').read_text(encoding='utf-8')
    return HTMLResponse(content=html)


@app.get('/register', include_in_schema=False)
def register_page() -> HTMLResponse:
    html = (FRONTEND_DIR / 'login.html').read_text(encoding='utf-8')
    return HTMLResponse(content=html)


@app.get('/editor', include_in_schema=False)
def editor_page() -> HTMLResponse:
    html = (FRONTEND_DIR / 'editor.html').read_text(encoding='utf-8')
    return HTMLResponse(content=html)