from typing import Optional
from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.types import UUID4
from pymongo.results import InsertOneResult

from socials.apps.bots.models import PlatformEnum
from socials.apps.bots_tasks.enums import TaskTypeEnum
from socials.apps.site.utils import get_time_now_timestamp
import uuid

from socials.database.main_db import db_provider

class BotEvent(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4, alias="_id")
    timestamp: int = get_time_now_timestamp()
    event_type: TaskTypeEnum
    platform: PlatformEnum
    bot_id: UUID4
    task_id: Optional[UUID4] = None
    count_amount: int = 0

    class Config:
        use_enum_values = True

    def save_db(self) -> InsertOneResult | None:
        inserted_event: InsertOneResult = db_provider.bots_events_db.insert_one(
            self.dict(by_alias=True)
        )
        return inserted_event or None
