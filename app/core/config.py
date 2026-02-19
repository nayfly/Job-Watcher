from pydantic import AnyUrl, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration exposed via environment variables."""

    # database
    DATABASE_URL: AnyUrl = "sqlite:///./jobwatcher.db"

    # redis/rq
    REDIS_URL: str = "redis://localhost:6379/0"
    RQ_QUEUE: str = "default"

    # service metadata
    APP_NAME: str = "job-watcher"
    APP_VERSION: str = "0.1.0"

    # optional notifier
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
