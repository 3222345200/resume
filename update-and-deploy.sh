#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ENV_FILE="${1:-.env.docker}"
BRANCH="${2:-main}"

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

echo "[1/4] Fetch latest code..."
git fetch origin

echo "[2/4] Switch to branch: $BRANCH"
git checkout "$BRANCH"

echo "[3/4] Pull latest commit..."
git pull --ff-only origin "$BRANCH"

echo "[4/4] Build and start containers..."
docker compose --env-file "$ENV_FILE" up -d --build

echo "Done."
echo "Check status with:"
echo "  docker compose --env-file $ENV_FILE ps"
