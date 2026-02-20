import os
import sys
import pytest

from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture
def client():
    return TestClient(app)


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
    # set up one source
    payload = {"name": "Example", "url": "http://example.com/feed"}
    r = client.post("/sources/", json=payload)
    print(r.status_code, r.json())


    # monkeypatch fetch_feed to return one entry matching keyword
    def fake_fetch(url):
        return [{"title": "Senior Python Developer", "link": "http://job/1", "published": None}]

    monkeypatch.setattr("app.workers.tasks.fetch_feed", fake_fetch)
    # stub out notifier so we don't hit network
    monkeypatch.setattr("app.services.notifier.telegram.send_message", lambda text: None)

    # create a watchlist with keyword 'python'
    wpayload = {"name": "Py", "keywords": "python"}
    r2 = client.post("/watchlists/", json=wpayload)
    assert r2.status_code == 201

    # run crawler directly
    from app.workers.tasks import crawl_all_sources

    crawl_all_sources()

    # verify job_posting inserted and alert created
    from app.db.session import SessionLocal
    from app import models

    db = SessionLocal()
    try:
        jp = db.query(models.job_posting.JobPosting).filter_by(link="http://job/1").one()
        assert jp.fingerprint
        alert = db.query(models.alert.Alert).filter_by(job_posting_id=jp.id).one()
        assert alert.watchlist_id == r2.json()["id"]
    finally:
        db.close()
