# Job Watcher

Minimal job alert service (MVP) with the following features:

- store RSS/JSON sources
- create watchlists with keywords
- RQ worker consumes feeds periodically
- deduplicates postings by fingerprint (sha256 of link)
- generates alerts when posting matches watchlist keywords
- simple HTTP API with FastAPI
- `/metrics` (Prometheus) and `/health` endpoints
- structured logs including request ID
- multi-service Docker Compose for API, worker, Redis, PostgreSQL
- SQLite fallback for development/tests

## Stack

- FastAPI
- SQLAlchemy (PostgreSQL + SQLite)
- Redis + RQ
- httpx, feedparser
- prometheus_client
- pytest / pytest-asyncio

## Project layout

```
app/
  api/routers      # HTTP endpoints
  core/            # config, logging, metrics
  db/              # session & base
  models/          # SQLAlchemy models
  schemas/         # Pydantic schemas
  services/        # scrapers, scheduler, notifier
  workers/         # RQ tasks & worker helper
main.py           # application entrypoint
...
```

## Development

1. create virtualenv and install deps:

```sh
python -m venv .venv
.\.venv\Scripts\activate   # on Windows
pip install -r requirements.txt  # or `pip install -e .[dev]`
```

2. run tests:

```sh
pytest
```

3. start API locally:

```sh
uvicorn app.main:app --reload
```

4. run worker:

```sh
python -m app.workers.worker
# or `rq worker -u redis://localhost:6379/0 default` if you have redis running
```

5. start scheduler (optional for periodic jobs):

```sh
python -m app.services.scheduler  # will enqueue every 5m
```

## Docker

Development compose uses SQLite and Redis:

```sh
docker-compose -f docker-compose.dev.yml up --build
```

Production compose adds PostgreSQL and scheduler:

```sh
docker-compose up --build
```

## Metrics & health

- `GET /health` returns `{"status":"ok"}`
- `GET /metrics` returns Prometheus metrics

## Logging

Structured logs include `request_id`; a middleware injects the header.

## Extensibility

- add new scrapers under `app/services/scrapers`
- implement notifier other than Telegram in `app/services/notifier`
- add database migrations via Alembic (placeholder config exists)
- include authentication on API endpoints

---

This project is focused on minimal functionality, nothing more, nothing less. Follow the architecture laid out in the initial design to maintain separation between HTTP, domain logic, scraping, and workers.