@echo off
setlocal

cd /d "%~dp0"

set "PROJECT_ROOT=%CD%"
set "ENV_FILE=%PROJECT_ROOT%\.env"
set "VENV_PYTHON=%PROJECT_ROOT%\.venv\Scripts\python.exe"
set "UPLOADS_DIR=%PROJECT_ROOT%\uploads"

if not exist "%ENV_FILE%" (
  echo Missing .env. Please create "%PROJECT_ROOT%\.env" first.
  pause
  exit /b 1
)

if not exist "%VENV_PYTHON%" (
  echo Missing virtual environment. Please restore or create "%PROJECT_ROOT%\.venv".
  pause
  exit /b 1
)

if not exist "%UPLOADS_DIR%" (
  mkdir "%UPLOADS_DIR%"
)

set "PYTHONPATH=%PROJECT_ROOT%"

tasklist /FI "IMAGENAME eq minio.exe" | find /I "minio.exe" >nul
if errorlevel 1 (
  start "MinIO" /MIN cmd /c "set MINIO_ROOT_USER=resumeadmin&& set MINIO_ROOT_PASSWORD=ResumeMinio#2026&& D:\Apps\MinIO\minio.exe server D:\MinIOData --address :9000 --console-address :9001 > D:\Apps\MinIO\minio.out.log 2> D:\Apps\MinIO\minio.err.log"
  timeout /t 2 >nul
)

"%VENV_PYTHON%" -m uvicorn app.main:app --app-dir "%PROJECT_ROOT%" --host 127.0.0.1 --port 8000 --reload --reload-dir "%PROJECT_ROOT%\app"

pause
