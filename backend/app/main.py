from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

import app.models  # noqa: F401
from app.api.routes.auth import router as auth_router
from app.api.routes.applications import router as applications_router
from app.api.routes.health import router as health_router
from app.api.routes.resumes import router as resumes_router
from app.api.routes.templates import router as templates_router
from app.api.routes.uploads import router as uploads_router
from app.core.config import settings
from app.core.db import engine
from app.core.logging import configure_logging, get_logger, log_requests
from app.db.base import Base
from app.db.bootstrap import ensure_runtime_schema
from app.services.minio_storage import ensure_bucket_exists

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
FRONTEND_VUE_DIST_DIR = PROJECT_ROOT / 'frontend' / 'dist'
FRONTEND_VUE_INDEX_FILE = FRONTEND_VUE_DIST_DIR / 'index.html'
FRONTEND_VUE_ASSETS_DIR = FRONTEND_VUE_DIST_DIR / 'assets'
UPLOADS_DIR = BASE_DIR / 'uploads'
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

configure_logging()
logger = get_logger('main')

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
)
app.middleware('http')(log_requests)

app.mount('/assets', StaticFiles(directory=str(FRONTEND_VUE_ASSETS_DIR), check_dir=False), name='assets')
app.mount('/uploads', StaticFiles(directory=str(UPLOADS_DIR)), name='uploads')
app.include_router(health_router, prefix='/api')
app.include_router(auth_router, prefix='/api')
app.include_router(applications_router, prefix='/api')
app.include_router(templates_router, prefix='/api')
app.include_router(resumes_router, prefix='/api')
app.include_router(uploads_router, prefix='/api')


@app.on_event('startup')
def on_startup() -> None:
    logger.info('startup_begin app_env=%s debug=%s', settings.app_env, settings.app_debug)
    Base.metadata.create_all(bind=engine)
    ensure_runtime_schema(engine)
    ensure_bucket_exists()
    logger.info('startup_complete')


@app.get('/', include_in_schema=False)
def index() -> RedirectResponse:
    return RedirectResponse(url='/dashboard', status_code=302)


def _read_frontend_html() -> str:
    if not FRONTEND_VUE_INDEX_FILE.exists():
        raise RuntimeError('frontend/dist/index.html not found, please build frontend first')
    return FRONTEND_VUE_INDEX_FILE.read_text(encoding='utf-8')


@app.get('/login', include_in_schema=False)
def login_page() -> HTMLResponse:
    return HTMLResponse(content=_read_frontend_html())


@app.get('/register', include_in_schema=False)
def register_page() -> HTMLResponse:
    return HTMLResponse(content=_read_frontend_html())


@app.get('/dashboard', include_in_schema=False)
def dashboard_page() -> HTMLResponse:
    return HTMLResponse(content=_read_frontend_html())


@app.get('/applications', include_in_schema=False)
def applications_page() -> HTMLResponse:
    return HTMLResponse(content=_read_frontend_html())


@app.get('/interviews', include_in_schema=False)
def interviews_page() -> HTMLResponse:
    return HTMLResponse(content=_read_frontend_html())


@app.get('/editor', include_in_schema=False)
def editor_page() -> HTMLResponse:
    return HTMLResponse(content=_read_frontend_html())
