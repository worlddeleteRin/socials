import uuid
from enum import Enum, unique
from datetime import datetime
from apps.site.utils import get_time_now
from pymongo.results import InsertOneResult
from pydantic import BaseModel, Field, UUID4
from typing import Optional, Union

from database.main_db import db_provider
from pymongo import ReturnDocument

from apps.bots.models import PlatformEnum

class CreateBotTask(BaseModel):
    """
        Base create bot task
    """
    title: str = ""
    platform: PlatformEnum


class BotTask(BaseModel):
    """
        Base bot account model
    """
    id: UUID4 = Field(default_factory=uuid.uuid4, alias="_id")
    title: str = ""
    platform: Optional[PlatformEnum] = None

    def save_db(self) -> InsertOneResult | None:
        inserted_bot: InsertOneResult = db_provider.bots_tasks_db.insert_one(self.dict(by_alias=True)
        )
        return inserted_bot or None

    def update_db(self):
        updated_bot = db_provider.bots_tasks_db.find_one_and_update(
            {"_id": self.id},
            {"$set": self.dict(by_alias=True)},
            return_document=ReturnDocument.AFTER
        )
        if updated_bot:
            return BotTask(**updated_bot)
        return None

    def remove_db(self):
        db_provider.bots_tasks_db.remove(
            {"_id": self.id},
        )

    class Config:
        allow_population_by_field_name = True

class BotTasksSearch(BaseModel):
    """
        Base bot tasks search model
    """
    bot_tasks: list[BotTask]
    total: int = 0

class BotTasksSearchQuery:
    skip: int = 0
    limit: int = 10
    platform: PlatformEnum | None
    def __init__(
        self,
        skip: int = 0,
        limit: int =10,
        platform: PlatformEnum = None
    ):
        self.skip = skip
        self.limit = limit
        self.platform = platform

    def collect_db_filters_query(self) -> dict:
        filters = {}

        if (self.platform):
            filters['platform'] = self.platform

        return filters

