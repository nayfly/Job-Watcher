import time
from typing import Optional

from redis import Redis
from rq import Queue

from app.core.config import settings
from app.workers.tasks import crawl_all_sources


def start_scheduler(interval_seconds: Optional[int] = None) -> None:
    """Simple blocking loop that enqueues a crawl job periodically."""
    interval = interval_seconds or 300  # default 5 minutes
    redis_conn = Redis.from_url(settings.REDIS_URL)
    queue = Queue(settings.RQ_QUEUE, connection=redis_conn)
    while True:
        queue.enqueue(crawl_all_sources)
        time.sleep(interval)
