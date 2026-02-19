#!/bin/sh
set -e

# apply migrations if alembic is configured, otherwise create tables directly
if [ -s alembic/alembic.ini ]; then
    alembic -c alembic/alembic.ini upgrade head || true
else
    python - <<'PYCODE'
from app.db import init_db
init_db()
PYCODE
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000
