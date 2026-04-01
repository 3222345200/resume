#!/usr/bin/env sh
set -eu

ENV_FILE="${1:-.env.docker}"

if [ ! -f "$ENV_FILE" ]; then
  echo "Environment file not found: $ENV_FILE"
  echo "Example: cp .env.docker.example .env.docker"
  exit 1
fi

docker compose --env-file "$ENV_FILE" up -d --build
