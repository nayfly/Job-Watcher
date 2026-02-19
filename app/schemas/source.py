from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class SourceBase(BaseModel):
    name: str
    url: HttpUrl
    is_active: Optional[bool] = True


class SourceCreate(SourceBase):
    pass


class SourceRead(SourceBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
