from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic.fields import Field
from pydantic import UUID4
from pymongo.results import InsertOneResult

from socials.apps.bots.models import PlatformEnum
from socials.apps.bots_tasks.enums import TaskTypeEnum
from socials.apps.site.utils import get_time_now, get_time_now_timestamp
import uuid

from socials.database.main_db import db_provider

class BotEvent(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4, alias="_id")
    timestamp: int = get_time_now_timestamp()
    date: datetime = Field(default_factory=get_time_now)
    event_type: TaskTypeEnum
    platform: PlatformEnum
    bot_id: Optional[UUID4]
    task_id: Optional[UUID4] = None
    count_amount: int = 0

    class Config:
        use_enum_values = True

    def save_db(self) -> InsertOneResult | None:
        inserted_event: InsertOneResult = db_provider.bots_events_db.insert_one(
            self.dict(by_alias=True)
        )
        return inserted_event or None

class GetBotEventsQuery:
    skip: int
    limit: int
    platform: PlatformEnum | None
    bot_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None
    event_type: TaskTypeEnum | None

    def __init__(
        self,
        skip = 0,
        limit = 40,
        platform = None,
        bot_id = None,
        task_id = None,
        event_type = None
    ):
        self.skip = skip
        self.limit = limit
        self.platform = platform
        if bot_id:
            self.bot_id = uuid.UUID(bot_id)
        self.task_id = task_id
        if task_id:
            self.task_id = uuid.UUID(task_id)
        self.event_type = event_type

    def collect_db_filters_query(self) -> dict:
        filters = {}

        if (self.platform):
            filters['platform'] = self.platform
        if (self.bot_id):
            filters['bot_id'] = self.bot_id
        if (self.task_id):
            filters['task_id'] = self.task_id
        if (self.event_type):
            filters['event_type'] = self.event_type

        return filters

class BotEventsSearch(BaseModel):
    """
        Base bot events search model
    """
    events: list[BotEvent]
    total: int = 0
