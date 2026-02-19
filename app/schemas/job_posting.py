from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class JobPostingBase(BaseModel):
    source_id: int
    title: str
    link: HttpUrl
    published_at: Optional[datetime]


class JobPostingCreate(JobPostingBase):
    fingerprint: str
    raw_json: Optional[str] = None


class JobPostingRead(JobPostingBase):
    id: int
    fingerprint: str
    raw_json: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
