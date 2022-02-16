import uuid
from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from apps.site.utils import get_time_now
from typing import Optional

class Bot(BaseModel):
    """
        Base bot account model
    """
    id: UUID4 = Field(default_factory=uuid.uuid4)
    username: str = ""
    password: str = ""
    access_token: str = ""
    created_time: datetime = Field(default_factory=get_time_now)
    # TODO: replace with enum mb?
    created_source: str = ""
    last_used: Optional[datetime] = None
    is_active: bool = False
    is_in_use: bool = False
    like_count: int = 0
    reply_count: int = 0
    comment_count: int = 0

    class Config:
        allow_population_by_field_name = True
