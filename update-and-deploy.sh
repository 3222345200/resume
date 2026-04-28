#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ENV_FILE="${1:-.env.docker}"
BRANCH="${2:-main}"
NODE_IMAGE="${NODE_IMAGE:-node:20-alpine}"
NPM_CACHE_VOLUME="${NPM_CACHE_VOLUME:-resume-frontend-npm-cache}"
NODE_BUILD_MEMORY_MB="${NODE_BUILD_MEMORY_MB:-1024}"

cd "$ROOT_DIR"

if [ ! -f "$ENV_FILE" ]; then
  echo "Environment file not found: $ENV_FILE"
  echo "Example: cp .env.docker.example .env.docker"
  exit 1
fi

if [ ! -d .git ]; then
  echo "This script must be run inside the git project directory."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required on this server."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose plugin is required on this server."
  exit 1
fi

mkdir -p "$ROOT_DIR/backend/uploads"

echo "[1/5] Fetch latest code..."
git fetch origin

echo "[2/5] Switch to branch: $BRANCH"
git checkout "$BRANCH"

echo "[3/5] Pull latest commit..."
git pull --ff-only origin "$BRANCH"

echo "[4/5] Build Vue frontend in a temporary Node container..."
docker volume create "$NPM_CACHE_VOLUME" >/dev/null
docker run --rm \
  -v "$ROOT_DIR/frontend:/app" \
  -v "$NPM_CACHE_VOLUME:/root/.npm" \
  -w /app \
  "$NODE_IMAGE" \
  sh -lc "npm ci --prefer-offline --no-audit && NODE_OPTIONS=--max-old-space-size=$NODE_BUILD_MEMORY_MB npm run build"

echo "[5/5] Build and start containers..."
docker compose --env-file "$ENV_FILE" up -d --build

echo "Done."
echo "Check status with:"
echo "  docker compose --env-file $ENV_FILE ps"
