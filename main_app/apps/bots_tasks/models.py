import uuid
from enum import Enum, unique
from datetime import datetime
from apps.site.utils import get_time_now
from pymongo.results import InsertOneResult
from pydantic import BaseModel, Field, UUID4, validator, ValidationError, root_validator
from typing import Optional, Union

from database.main_db import db_provider
from pymongo import ReturnDocument

from apps.bots.models import PlatformEnum

class TaskTypeEnum(str, Enum):
    like_post = 'like_post'
    repost_post = 'repost_post'
    dummy = 'dummy'

class FrequencyTypeEnum(str, Enum):
    once = 'once'
    periodicly = 'periodicly'

class WorkLagEnum(str, Enum):
    immediately = 'Immediately'
    one_minute = '1 minute'
    five_minutes = '5 minutes'
    ten_minutes = '10 minutes'
    thirty_minutes = '30 minutes'
    one_hour = '1 hour'
    three_hours = '3 hours'
    one_day = '1 day'
    two_days = '2 days'
    three_days = '3 days'
    one_week = '1 week'
    one_month = 'one month' 
    custom_date = 'Custom date'

class TimeFrequency(BaseModel):
    pass

class TaskDateFinish(BaseModel):
    date: datetime

class LikePostTargetData(BaseModel):
    post_link: str
    like_count: int
    work_lag: WorkLagEnum = WorkLagEnum.one_minute
    date_finish: Optional[TaskDateFinish] = None

    @root_validator
    def validate_like_post_target_data(cls, values):
        work_lag = values.get('work_lag')
        date_finish = values.get('date_finish')

        if not isinstance(work_lag, WorkLagEnum):
            raise ValueError('incorrect work_lag value')
        if work_lag == WorkLagEnum.custom_date:
            if not isinstance(date_finish, TaskDateFinish):
                raise ValueError('provide date_finish')
        return values
        

class TaskTargetData(BaseModel):
    """
        Task target data model
    """
    like_post: Optional[LikePostTargetData] = None

class TaskType(BaseModel):
    """
        Task type model
    """
    id: TaskTypeEnum
    name: str
    platforms: list[PlatformEnum]

class CreateBotTask(BaseModel):
    """
        Base create bot task
    """
    title: str = ""
    platform: PlatformEnum
    task_type: TaskTypeEnum
    task_target_data: TaskTargetData

    @root_validator
    def validate_create_bot(cls, values):
        task_type = values.get('task_type')
        task_target_data = values.get('task_target_data')
        if not isinstance(task_type, TaskTypeEnum):
            raise ValueError('provide correct task_type')
        if not isinstance(task_target_data, TaskTargetData):
            raise ValueError('provide correct task_target_data')

        if task_type is TaskTypeEnum.like_post:
            if not task_target_data.like_post:
                raise ValueError('provide like_post')
        """
        if cls.task_type is TaskTypeEnum.repost_post:
            if not cls.task_target_data.repost_post:
                raise ValueError('provide repost_post')
        """
        return values


class BotTask(BaseModel):
    """
        Base bot account model
    """
    id: UUID4 = Field(default_factory=uuid.uuid4, alias="_id")
    is_active: bool = True
    is_finished: bool = False
    has_error: bool = False
    created_date: datetime = Field(default_factory=get_time_now)
    updated_date: datetime = Field(default_factory=get_time_now)
    next_run_timestamp: Optional[int] = None
    title: str = ""
    platform: Optional[PlatformEnum] = None
    task_type: TaskTypeEnum = TaskTypeEnum.dummy
    error_msg: str = ""
    task_target_data: TaskTargetData

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
    task_type: TaskTypeEnum | None
    is_active: bool | None
    is_finished: bool | None
    has_error: bool | None

    def __init__(
        self,
        skip: int = 0,
        limit: int =10,
        platform: PlatformEnum = None,
        task_type: TaskTypeEnum = None,
        is_active: bool = None,
        is_finished: bool = None,
        has_error: bool = None
    ):
        self.skip = skip
        self.limit = limit
        self.platform = platform
        self.task_type = task_type
        self.is_active = is_active
        self.is_finished = is_finished
        self.has_error = has_error 

    def collect_db_filters_query(self) -> dict:
        filters = {}

        if (self.platform):
            filters['platform'] = self.platform
        if (self.task_type):
            filters['task_type'] = self.task_type
        if (self.is_active):
            filters['is_active'] = self.is_active
        if (self.is_finished):
            filters['is_finished'] = self.is_finished
        if (self.has_error):
            filters['has_error'] = self.has_error

        return filters

