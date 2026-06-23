#!/usr/bin/env bash
# Backend entrypoint: runs Alembic migrations, then execs the main command.
# Usage:
#   ./docker/entrypoint.sh uvicorn app.main:app --host 0.0.0.0 --port 8000
#   ./docker/entrypoint.sh celery -A app.workers.celery_app worker -l info
set -euo pipefail

# Only run migrations when the API server starts (skip for the worker / tests).
if [[ "${RUN_MIGRATIONS:-1}" == "1" && "${1:-}" == "uvicorn" ]]; then
    echo ">> Running Alembic migrations..."
    alembic upgrade head
fi

echo ">> Starting: $*"
exec "$@"
