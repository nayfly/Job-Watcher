import hashlib
import json
import logging
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app import models
from app.services.scrapers.rss import fetch_feed

logger = logging.getLogger(__name__)


def crawl_all_sources() -> None:
    """Entry point for the RQ worker.  Fetches each active source and processes items."""
    db = SessionLocal()
    try:
        sources = db.query(models.source.Source).filter(models.source.Source.is_active.is_(True)).all()
        for src in sources:
            try:
                _process_source(db, src)
            except Exception:  # pylint: disable=broad-except
                logger.exception("failed to process source %s", src.id)
    finally:
        db.close()


def _process_source(db: Session, source: models.source.Source) -> None:
    items = fetch_feed(source.url)
    for entry in items:
        _process_entry(db, source, entry)


def _process_entry(db: Session, source: models.source.Source, entry: Dict[str, Any]) -> None:
    link = entry.get("link") or entry.get("id") or ""
    if not link:
        return
    fp = hashlib.sha256(link.encode("utf-8")).hexdigest()

    # deduplicate
    existing = db.query(models.job_posting.JobPosting).filter_by(fingerprint=fp).first()
    if existing:
        return

    jp = models.job_posting.JobPosting(
        source_id=source.id,
        title=entry.get("title", ""),
        link=link,
        published_at=_parse_datetime(entry.get("published")),
        fingerprint=fp,
        raw_json=json.dumps(entry, default=str),
    )
    db.add(jp)
    db.commit()
    db.refresh(jp)

    _match_watchlists(db, jp)


def _parse_datetime(val: Any) -> Any:
    # feedparser returns a struct_time for published_parsed; keep naive
    try:
        import time
        from datetime import datetime

        if isinstance(val, time.struct_time):
            return datetime.fromtimestamp(time.mktime(val))
        return val
    except Exception:
        return None


def _match_watchlists(db: Session, posting: models.job_posting.JobPosting) -> None:
    watchlists = db.query(models.watchlist.Watchlist).filter(models.watchlist.Watchlist.is_active.is_(True)).all()
    text = posting.title.lower()
    from app.services.notifier import telegram

    for wl in watchlists:
        for kw in wl.keywords.split():
            if kw.lower() in text:
                alert = models.alert.Alert(watchlist_id=wl.id, job_posting_id=posting.id)
                db.add(alert)
                # attempt to send notification
                try:
                    telegram.send_message(
                        f"Alert: '{posting.title}' matches watchlist '{wl.name}'"
                    )
                except Exception:
                    logger.exception("failed to send telegram alert")
    db.commit()
