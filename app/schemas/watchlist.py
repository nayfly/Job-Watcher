from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WatchlistBase(BaseModel):
    name: str
    keywords: str
    is_active: Optional[bool] = True


class WatchlistCreate(WatchlistBase):
    pass


class WatchlistRead(WatchlistBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
