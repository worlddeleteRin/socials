import uuid
# from enum import Enum, unique
from datetime import datetime
from socials.apps.bots_tasks.regular_like_group.models import RegularLikeGroupResultMetrics, RegularLikeGroupTargetData
from socials.apps.bots_tasks.watch_video.models import WatchVideoResultMetrics, WatchVideoTargetData
from socials.apps.site.utils import get_time_now
from pymongo.results import InsertOneResult
from pydantic import BaseModel, Field, UUID4, root_validator
from typing import Any, Optional
from socials.database.enums import SortingOrder

from socials.database.main_db import db_provider
from pymongo import ReturnDocument

from socials.apps.bots.models import PlatformEnum
from socials.apps.bots_tasks.like_post.models import *
from socials.apps.bots_tasks.enums import *
from socials.logging import lgd,lgw,lge
from socials.apps.bots.models import selenium_tasks
# import socials.apps

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
    watch_video: Optional[WatchVideoTargetData] = None
    regular_like_group: Optional[RegularLikeGroupTargetData] = None

class TaskResultMetrics(BaseModel):
    """
    Task result metrics data
    """
    like_post: LikePostResultMetrics = LikePostResultMetrics()
    watch_video: WatchVideoResultMetrics = WatchVideoResultMetrics()
    regular_like_group: RegularLikeGroupResultMetrics = RegularLikeGroupResultMetrics()

    @validator('like_post', pre=True, always=True, check_fields=False)
    def validate_like_post(cls, v):
        if not v:
            return LikePostResultMetrics()
        return v

    @validator('regular_like_group', pre=True, always=True, check_fields=False)
    def validate_regular_like_group(cls, v):
        if not v:
            return RegularLikeGroupResultMetrics()
        return v

class TaskType(BaseModel):
    """
    Task type model
    """
    id: TaskTypeEnum
    name: str
    description: str = ""
    platforms: list[PlatformEnum]
    duration_type: TaskDurationTypeEnum
    is_active: bool

    def save_db(self) -> InsertOneResult | None:
        inserted_bot: InsertOneResult = db_provider.tasks_types_db.insert_one(self.dict(by_alias=True)
        )
        return inserted_bot or None

    def update_db(self):
        updated_task_type = db_provider.tasks_types_db.find_one_and_update(
            {"_id": self.id},
            {"$set": self.dict(by_alias=True)},
            return_document=ReturnDocument.AFTER
        )
        if updated_task_type:
            return TaskType(**updated_task_type)
        return None

    def remove_db(self):
        db_provider.tasks_types_db.delete_one(
            {"id": self.id},
        )

class CreateBotTask(BaseModel):
    """
    Base create bot task
    """
    title: str = ""
    platform: PlatformEnum
    task_type: TaskTypeEnum
    task_target_data: TaskTargetData
    is_active: bool = False 
    # hidden fields
    delete_after_finished: bool = False
    is_hidden: bool = False
    is_testing: bool = False
    is_selenium: bool = False

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
    id: UUID4 = Field(default_factory=uuid.uuid4)
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
    delete_after_finished: bool = False
    is_hidden: bool = False
    is_testing: bool = False
    is_selenium: bool = False

    @validator('is_selenium', pre=True, always=True)
    def valid_is_selenium(cls, v):
        if not v:
            return False
        return v

    @staticmethod
    def get_bot_task_by_id(
        id: UUID4
    ):
        bot_task_raw = db_provider.bots_tasks_db.find_one(
            {"id": id}
        )
        try:
            if (bot_task_raw):
                bot_task = BotTask(**bot_task_raw)
                return bot_task
            return None
        except:
            return None

    def setFinished(self):
        self.status = BotTaskStatusEnum.finished
        self.is_active = False
        self.next_run_timestamp = None
        lgd('✅Bot task is finished')
        if self.delete_after_finished:
            self.remove_db()

    def setError(self, error: BotTaskError, update: bool = False):
        lge(error.error_msg)
        self.error = error
        self.status = BotTaskStatusEnum.error
        self.is_active = False
        # mb make update or remove?
        if update:
            self.update_db()

    def hasError(self):
        if self.error:
            return True
        return False

    def isRunning(self) -> bool:
        return (
            self.status is BotTaskStatusEnum.running and
            self.is_active
        )

    def isFinished(self):
        return self.status is BotTaskStatusEnum.finished


    def sync_metrics(self):
        fresh_task = self.get_fresh()
        if fresh_task:
            self.task_result_metrics = TaskResultMetrics(**fresh_task.task_result_metrics.dict())

    def get_fresh(self):
        return self.get_bot_task_by_id(
            self.id
        )

    def save_db(self) -> InsertOneResult | None:
        inserted_bot: InsertOneResult = db_provider.bots_tasks_db.insert_one(self.dict(by_alias=True)
        )
        return inserted_bot or None

    def update_db(
        self,
        update_metrics: bool = True
    ):
        exclude={}
        if not update_metrics:
            exclude = {"task_result_metrics"}
        self.updated_date = get_time_now()
        updated_bot = db_provider.bots_tasks_db.find_one_and_update(
            {"id": self.id},
            {"$set": self.dict(
                by_alias=True,
                exclude=exclude
            )},
            return_document=ReturnDocument.AFTER
        )
        if updated_bot:
            return BotTask(**updated_bot)
        return None

    def update_or_remove_db(self):
        if self.delete_after_finished:
            self.remove_db()
            return
        self.update_db()

    def remove_db(self):
        lgd(f'removing task from database, id: {self.id}')
        db_provider.bots_tasks_db.delete_one(
            {"id": self.id},
        )

    def check_selenium(self):
        if self.task_type in selenium_tasks:
            if self.platform in selenium_tasks[self.task_type]:
                self.is_selenium = True

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
    include_hidden: bool = False
    filter_by_selenium: bool = False
    include_selenium_tasks: bool = True
    sort_by_created_date: int | None
    sort_by_updated_date: SortingOrder | None

    def __init__(
        self,
        skip: int = 0,
        limit: int = 10,
        platform: Optional[PlatformEnum] = None,
        task_type: Optional[TaskTypeEnum] = None,
        is_active: Optional[bool] = None,
        status: Optional[BotTaskStatusEnum] = None,
        include_hidden: bool = False,
        filter_by_selenium: bool = False,
        include_selenium_tasks: bool = True,
        sort_by_created_date: Optional[int] = None,
        sort_by_updated_date: Optional[SortingOrder] = None
    ):
        self.skip = skip
        self.limit = limit
        self.platform = platform
        self.task_type = task_type
        self.is_active = is_active
        self.status = status
        self.include_hidden = include_hidden
        self.filter_by_selenium = filter_by_selenium
        self.include_selenium_tasks = include_selenium_tasks
        self.sort_by_created_date = sort_by_created_date
        self.sort_by_updated_date = sort_by_updated_date

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
        if not (self.include_hidden):
            filters['is_hidden'] = False
        if self.filter_by_selenium:
            filters['is_selenium'] = self.include_selenium_tasks

        return filters

    def collect_db_sort_query(self) -> list:
        sort = []

        if self.sort_by_created_date:
            sort.append(('created_date', self.sort_by_created_date))
        if self.sort_by_updated_date:
            sort.append(('updated_date', self.sort_by_updated_date))

        return sort 

