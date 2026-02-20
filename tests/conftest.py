import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set env BEFORE importing app modules that read settings
os.environ.setdefault("ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.db.base import Base  # noqa: E402
from app.db import session as db_session  # noqa: E402
import app.api.deps as deps_module  # noqa: E402


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        os.environ["DATABASE_URL"],
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # IMPORTANT: one shared in-memory DB
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def _patch_db(engine, monkeypatch):
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )

    # Patch the actual places used by the app
    monkeypatch.setattr(db_session, "engine", engine)
    monkeypatch.setattr(db_session, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(deps_module, "SessionLocal", TestingSessionLocal)

    # Optional: if some module imports SessionLocal directly and caches it,
    # patch it too (safe even if not used yet)
    try:
        import app.workers.tasks as tasks_module
        monkeypatch.setattr(tasks_module, "SessionLocal", TestingSessionLocal)
    except Exception:
        pass

    yield