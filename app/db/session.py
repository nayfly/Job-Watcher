from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# SQLite needs a special flag to allow cross-thread access; other DBs ignore it
# settings.DATABASE_URL is an AnyUrl; convert to str for string operations
url = str(settings.DATABASE_URL)
connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}

engine = create_engine(url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
