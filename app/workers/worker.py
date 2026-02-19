from redis import Redis
from rq import Worker, Queue, Connection

from app.core.config import settings


def run_worker():
    """Start an RQ worker listening to the configured queue."""

    listen = [settings.RQ_QUEUE]
    redis_conn = Redis.from_url(settings.REDIS_URL)
    with Connection(redis_conn):
        w = Worker(list(map(Queue, listen)))
        w.work()


if __name__ == "__main__":
    run_worker()
