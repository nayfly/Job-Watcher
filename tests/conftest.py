import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# force test environment
os.environ["ENV"] = "test"

from app.db.base import Base  # noqa: E402
from app.db import session as db_session  # noqa: E402


@pytest.fixture(autouse=True)
def override_db(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    monkeypatch.setattr(db_session, "engine", engine)
    monkeypatch.setattr(db_session, "SessionLocal", TestingSessionLocal)

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)