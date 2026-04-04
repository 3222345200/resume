FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CHROME_BIN=/usr/bin/chromium

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        chromium \
        fontconfig \
        fonts-noto-cjk \
        fonts-dejavu-core \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/backend

COPY backend/pyproject.toml README.md ./
COPY backend/app ./app
COPY frontend/src/assets /workspace/frontend/src/assets
COPY frontend/dist /workspace/frontend/dist
COPY backend/server-fonts /usr/local/share/fonts/resume

RUN pip install --upgrade pip \
    && pip install . \
    && mkdir -p ./uploads \
    && fc-cache -f -v

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
