import uuid
from enum import Enum, unique
from pydantic import BaseModel, UUID4, Field
from datetime import datetime

from pymongo.results import InsertOneResult
from apps.site.utils import get_time_now
from typing import Optional, Union

from database.main_db import db_provider
from pymongo import ReturnDocument

from utils.checks import can_be_numeric

@unique
class PlatformEnum(str, Enum):
    vk = "vk"
    instagram = "instagram"

@unique
class GenderEnum(str, Enum):
    male = "male"
    female = "female"

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
    created_source: Optional[str] = ""
    last_used: Optional[datetime] = None
    is_active: bool = False
    is_in_use: bool = False
    like_count: int = 0
    reply_count: int = 0
    comment_count: int = 0
    platform: Optional[PlatformEnum] = None
    gender: Optional[GenderEnum] = None

    def save_db(self) -> InsertOneResult | None:
        inserted_bot: InsertOneResult = db_provider.bots_db.insert_one(self.dict(by_alias=True)
        )
        return inserted_bot or None

    def update_db(self):
        updated_bot = db_provider.bots_db.find_one_and_update(
            {"_id": self.id},
            {"$set": self.dict(by_alias=True)},
            return_document=ReturnDocument.AFTER
        )
        if updated_bot and updated_bot.dict():
            return Bot(**updated_bot.dict())
        return None

    def remove_db(self):
        db_provider.carts_db.remove(
            {"_id": self.id},
        )

    class Config:
        allow_population_by_field_name = True

class BotSearch(BaseModel):
    """
        Base bot search model
    """
    bots: list[Bot]
    total: int = 0
    # TODO: implement in future
    # filter_values: list[FilterValue]

class BotSearchQuery:
    limit: int
    offset: int
    is_active: int | None
    is_in_use: int | str | None
    platform: PlatformEnum | None
    gender: GenderEnum | None
    def __init__(
        self,
        platform: PlatformEnum = None,
        gender: GenderEnum = None,
        limit: int = 10,
        offset: int = 0,
        is_active: int = None,
        is_in_use: Union[int,str] = None,
    ):
        self.limit = limit
        self.offset = offset
        self.is_active = is_active
        self.is_in_use = is_in_use
        self.platform = platform
        self.gender = gender

    def collect_db_filters_query(self) -> dict:
        filters = {}

        if (self.is_active is not None):
            filters['is_active'] = bool(self.is_active)

        if self.is_in_use is not None: 
            filters['is_in_use'] = bool(self.is_in_use)

        if self.platform is not None:
            filters['platform'] = self.platform

        if self.gender is not None:
            filters['gender'] = self.gender

        return filters


