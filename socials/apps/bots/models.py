import uuid
from enum import Enum, unique
from pydantic import BaseModel, UUID4, Field
from datetime import datetime

from pymongo.results import InsertOneResult
from socials.apps.bots.enums import CountryEnum
from socials.apps.bots_tasks.enums import TaskTypeEnum
from socials.apps.site.utils import get_time_now
from typing import Optional

from socials.database.main_db import db_provider
from pymongo import ReturnDocument

from vk_core.users.main import VkUserModel


@unique
class PlatformEnum(str, Enum):
    vk = "vk"
    ok = "ok"
    instagram = "instagram"
    yt = "youtube"

selenium_tasks = {
    TaskTypeEnum.like_post: [
        PlatformEnum.ok
    ],
    TaskTypeEnum.watch_video: [
        PlatformEnum.yt
    ]
}

@unique
class GenderEnum(str, Enum):
    male = "male"
    female = "female"

@unique
class BotSortByEnum(str, Enum):
    created_time = 'created_time'
    last_used = 'last_used'

class BotDailyMetrics(BaseModel):
    """
    Bot dialy metrics model
    """
    like_count: int = 0
    reply_count: int = 0
    comment_count: int = 0

class BotRateLimits(BaseModel):
    daily: BotDailyMetrics = BotDailyMetrics()
    hourly: BotDailyMetrics = BotDailyMetrics()

    def append_dialy_hourly_filters(
        self,
        filters: dict
    ) -> dict:
        filters = self.daily_append_as_db_filter(filters)
        filters = self.hourly_append_as_db_filter(filters)
        return filters
    def daily_append_as_db_filter(self, filters: dict) -> dict:
        filters['daily_metrics.like_count'] = {
            "$lte": self.daily.like_count
        }
        filters['daily_metrics.reply_count'] = {
            "$lte": self.daily.reply_count
        }
        filters['daily_metrics.comment_count'] = {
            "$lte": self.daily.comment_count
        }
        return filters
    def hourly_append_as_db_filter(self, filters: dict) -> dict:
        filters['hourly_metrics.like_count'] = {
            "$lte": self.hourly.like_count
        }
        filters['hourly_metrics.reply_count'] = {
            "$lte": self.hourly.reply_count
        }
        filters['hourly_metrics.comment_count'] = {
            "$lte": self.hourly.comment_count
        }
        return filters

dailyRateLimits = BotDailyMetrics(
    like_count = 30,
    reply_count = 10,
    comment_count = 40
)

hourlyRateLimits = BotDailyMetrics(
    like_count = 8,
    reply_count = 3,
    comment_count = 10 
)

rate_limits = BotRateLimits(
    daily = dailyRateLimits,
    hourly = hourlyRateLimits
)



class BotPlatformData(BaseModel):
    vk: Optional[VkUserModel] = None

class BotCreate(BaseModel):
    """
        Bot create model
    """
    username: str
    password: str
    access_token: str = ""
    is_active: bool = True
    is_in_use: bool = False
    platform: PlatformEnum
    gender: GenderEnum
    country: CountryEnum = CountryEnum.russia
    rest_until: Optional[datetime]

class Bot(BaseModel):
    """
        Base bot account model
    """
    id: UUID4 = Field(default_factory=uuid.uuid4)
    username: str = ""
    password: str = ""
    access_token: str = ""
    refresh_token: str = ""
    expires_in: str = ""
    created_time: datetime = Field(default_factory=get_time_now)
    # bot platform data
    platform_data: BotPlatformData = BotPlatformData()
    # TODO: replace with enum mb?
    created_source: Optional[str] = ""
    last_used: Optional[datetime] = None
    is_active: bool = False
    is_in_use: bool = False
    is_banned: bool = False
    is_resting: bool = False
    need_action: bool = False
    like_count: int = 0
    reply_count: int = 0
    comment_count: int = 0
    country: CountryEnum = CountryEnum.russia
    platform: Optional[PlatformEnum] = None
    gender: Optional[GenderEnum] = None
    rest_until: Optional[datetime] = None
    # daily metrics like|reply|comment etc. counts
    daily_metrics: BotDailyMetrics = BotDailyMetrics()
    # hourly metrics like|reply|comment etc. counts
    hourly_metrics: BotDailyMetrics = BotDailyMetrics()


    def save_db(self) -> InsertOneResult | None:
        inserted_bot: InsertOneResult = db_provider.bots_db.insert_one(self.dict(by_alias=True)
        )
        return inserted_bot or None

    def update_db(
            self,
            update_used: bool = False
        ):
        if update_used:
            self.last_used = get_time_now()
        updated_bot = db_provider.bots_db.find_one_and_update(
            {"id": self.id},
            {"$set": self.dict(by_alias=True)},
            return_document=ReturnDocument.AFTER
        )
        if updated_bot:
            return Bot(**updated_bot)
        return None

    def replace_db(self):
        replaced_bot = db_provider.bots_db.find_one_and_replace(
            {"id": self.id},
            self.dict(by_alias=True),
            return_document=ReturnDocument.AFTER
        )
        if replaced_bot:
            # return Bot(**replaced_bot)
            return replaced_bot

    def remove_db(self):
        db_provider.bots_db.delete_one(
            {"id": self.id},
        )

    def set_banned(self):
        self.is_banned = True
        self.is_active = False
        self.is_in_use = False
        self.is_resting = False
        self.rest_until = None

    def deactivate(self):
        self.is_active = False
        self.is_in_use = False

    def set_awake(self):
        self.is_active = True
        self.is_in_use = True
        self.is_resting = False
        self.rest_until = None

    def set_resting(self):
        self.is_active = False
        self.is_in_use = False
        self.is_resting = True

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
    is_in_use: int | None
    platform: PlatformEnum | None
    gender: GenderEnum | None
    sort_by: BotSortByEnum
    sort_direction: int
    exclude_by_ids: list[UUID4]
    filter_by_rate_limits: int
    has_rest_until: int
    def __init__(
        self,
        platform: Optional[PlatformEnum] = None,
        gender: Optional[GenderEnum] = None,
        limit: int = 10,
        offset: int = 0,
        is_active: Optional[int] = None,
        is_in_use: Optional[int] = None,
        sort_by: BotSortByEnum = BotSortByEnum.created_time,
        sort_direction: int = -1,
        exclude_by_ids: list[UUID4] = [],
        filter_by_rate_limits: int = 0,
        has_rest_until: int = 0
    ):
        self.limit = limit
        self.offset = offset
        self.is_active = is_active
        self.is_in_use = is_in_use
        self.platform = platform
        self.gender = gender
        self.sort_by = sort_by
        self.sort_direction = sort_direction
        self.exclude_by_ids = exclude_by_ids
        self.filter_by_rate_limits = filter_by_rate_limits
        self.has_rest_until = has_rest_until

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

        # exclude by ids filter
        if len(self.exclude_by_ids) > 0:
            filters['id'] = {
                '$nin': self.exclude_by_ids
            }
        
        # apply filter by rate limits
        if bool(self.filter_by_rate_limits):
            filters = rate_limits.append_dialy_hourly_filters(filters)

        # rest_until filter
        if bool(self.has_rest_until):
            filters['rest_until'] = {
                '$ne': None
            }

        return filters


