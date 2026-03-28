@echo off
cd /d "%~dp0"
tasklist /FI "IMAGENAME eq minio.exe" | find /I "minio.exe" >nul
if errorlevel 1 (
  start "MinIO" /MIN cmd /c "set MINIO_ROOT_USER=resumeadmin&& set MINIO_ROOT_PASSWORD=ResumeMinio#2026&& D:\Apps\MinIO\minio.exe server D:\MinIOData --address :9000 --console-address :9001 > D:\Apps\MinIO\minio.out.log 2> D:\Apps\MinIO\minio.err.log"
  timeout /t 2 >nul
)
call .venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
