import uuid
# from enum import Enum, unique
from datetime import datetime
from apps.site.utils import get_time_now
from pymongo.results import InsertOneResult
from pydantic import BaseModel, Field, UUID4, root_validator
from typing import Any, Optional

from database.main_db import db_provider
from pymongo import ReturnDocument

from apps.bots.models import PlatformEnum
from apps.bots_tasks.like_post.models import *
from apps.bots_tasks.enums import *

class BotTaskError(BaseModel):
    error_msg: str = ''
    detail_msg: str = ''

    @staticmethod
    def dummy_error(msg: Any):
        return BotTaskError(error_msg = f'{msg}')

class TaskTargetData(BaseModel):
    """
    Task target data model
    """
    like_post: Optional[LikePostTargetData] = None

class TaskResultMetrics(BaseModel):
    """
    Task result metrics data
    """
    like_post: Optional[LikePostResultMetrics] = None

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
    status: BotTaskStatusEnum = BotTaskStatusEnum.running
    created_date: datetime = Field(default_factory=get_time_now)
    updated_date: datetime = Field(default_factory=get_time_now)
    next_run_timestamp: Optional[int] = None
    title: str = ""
    platform: Optional[PlatformEnum] = None
    task_type: TaskTypeEnum = TaskTypeEnum.dummy
    error: Optional[BotTaskError] = None
    task_result_metrics: TaskResultMetrics = TaskResultMetrics()
    task_target_data: TaskTargetData
    bots_used: list[UUID4] = []

    def setFinished(self):
        self.status = BotTaskStatusEnum.finished
        self.is_active = False
        self.next_run_timestamp = None

    def setError(self, error: BotTaskError):
        self.error = error
        self.status = BotTaskStatusEnum.error
        self.is_active = False

    def hasError(self):
        if self.error:
            return True
        return False

    def isRunning(self):
        return (
            self.status is BotTaskStatusEnum.running and
            self.is_active
        )

    def isFinished(self):
        return self.status is BotTaskStatusEnum.finished

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
    status: BotTaskStatusEnum | None

    def __init__(
        self,
        skip: int = 0,
        limit: int = 10,
        platform: Optional[PlatformEnum] = None,
        task_type: Optional[TaskTypeEnum] = None,
        is_active: Optional[bool] = None,
        status: Optional[BotTaskStatusEnum] = None
    ):
        self.skip = skip
        self.limit = limit
        self.platform = platform
        self.task_type = task_type
        self.is_active = is_active
        self.status = status

    def collect_db_filters_query(self) -> dict:
        filters = {}

        if (self.platform):
            filters['platform'] = self.platform
        if (self.task_type):
            filters['task_type'] = self.task_type
        if (self.is_active):
            filters['is_active'] = self.is_active
        if (self.status):
            filters['status'] = self.status

        return filters

