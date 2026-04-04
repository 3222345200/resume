@echo off
setlocal

cd /d "%~dp0"

set "PROJECT_ROOT=%CD%"
set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "ENV_FILE=%PROJECT_ROOT%\.env"
set "VENV_PYTHON=%PROJECT_ROOT%\.venv\Scripts\python.exe"
set "UPLOADS_DIR=%BACKEND_DIR%\uploads"
set "FRONTEND_VUE_DIR=%PROJECT_ROOT%\frontend"
set "FRONTEND_VUE_DIST=%FRONTEND_VUE_DIR%\dist\index.html"

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

where npm >nul 2>nul
if errorlevel 1 (
  echo npm was not found. Please install Node.js first, or manually provide "%FRONTEND_VUE_DIST%".
  pause
  exit /b 1
)

if exist "%FRONTEND_VUE_DIR%\package.json" (
  echo [1/3] Building Vue frontend...
  pushd "%FRONTEND_VUE_DIR%"

  if not exist "%FRONTEND_VUE_DIR%\node_modules" (
    echo Installing frontend dependencies...
    call npm install
    if errorlevel 1 (
      popd
      echo Failed to install frontend dependencies.
      pause
      exit /b 1
    )
  )

  call npm run build
  if errorlevel 1 (
    popd
    echo Failed to build Vue frontend.
    pause
    exit /b 1
  )

  popd
) else (
  echo [1/3] frontend/package.json not found. Cannot build frontend assets.
  pause
  exit /b 1
)

set "PYTHONPATH=%BACKEND_DIR%"

echo [2/3] Checking MinIO service...
tasklist /FI "IMAGENAME eq minio.exe" | find /I "minio.exe" >nul
if errorlevel 1 (
  start "MinIO" /MIN cmd /c "set MINIO_ROOT_USER=resumeadmin&& set MINIO_ROOT_PASSWORD=ResumeMinio#2026&& D:\Apps\MinIO\minio.exe server D:\MinIOData --address :9000 --console-address :9001 > D:\Apps\MinIO\minio.out.log 2> D:\Apps\MinIO\minio.err.log"
  timeout /t 2 >nul
)

echo [3/3] Starting FastAPI server at http://127.0.0.1:8000 ...
"%VENV_PYTHON%" -m uvicorn app.main:app --app-dir "%BACKEND_DIR%" --host 127.0.0.1 --port 8000

pause
