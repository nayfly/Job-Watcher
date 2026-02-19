from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AlertBase(BaseModel):
    watchlist_id: int
    job_posting_id: int


class AlertCreate(AlertBase):
    pass


class AlertRead(AlertBase):
    id: int
    created_at: datetime
    sent_at: Optional[datetime]

    model_config = {"from_attributes": True}
