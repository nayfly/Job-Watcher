from .base import Base
from .session import engine


def init_db():
    """Create all tables. Intended for simple SQLite/dev usage."""
    Base.metadata.create_all(bind=engine)
