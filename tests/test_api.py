import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health/")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_list_source(client):
    payload = {"name": "Example", "url": "http://example.com/feed"}
    r = client.post("/sources/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Example"

    r2 = client.get("/sources/")
    assert r2.status_code == 200
    assert len(r2.json()) >= 1


def test_worker_processing(monkeypatch, client):
    payload = {"name": "Example", "url": "http://example.com/feed"}
    r = client.post("/sources/", json=payload)
    assert r.status_code == 201

    def fake_fetch(url):
        return [{"title": "Senior Python Developer", "link": "http://job/1", "published": None}]

    monkeypatch.setattr("app.workers.tasks.fetch_feed", fake_fetch)
    monkeypatch.setattr("app.services.notifier.telegram.send_message", lambda text: None)

    wpayload = {"name": "Py", "keywords": "python"}
    r2 = client.post("/watchlists/", json=wpayload)
    assert r2.status_code == 201

    from app.workers.tasks import crawl_all_sources
    crawl_all_sources()

    from app.db.session import SessionLocal
    from app import models

    db = SessionLocal()
    try:
        jp = db.query(models.job_posting.JobPosting).filter_by(link="http://job/1").one()
        alert = db.query(models.alert.Alert).filter_by(job_posting_id=jp.id).one()
        assert alert.watchlist_id == r2.json()["id"]
    finally:
        db.close()