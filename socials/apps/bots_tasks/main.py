from socials.apps.bots_tasks.like_post.like_post import process_like_post_task
from socials.database.main_db import db_provider
from socials.logging import lgd, lgw
from .models import *
from .bots_tasks_exceptions import *
# from socials.apps.bots.models import BotSearchQuery, Bot
# from socials.apps.bots.bots import get_bots

# from socials.apps import bots_tasks

import socials.apps.bots_tasks.regular_like_group.main

def get_tasks_types() -> list[TaskType]:
    tasks_types_dict = db_provider.tasks_types_db.find({})
    tasks_types = [TaskType(**task_type) for task_type in tasks_types_dict]
    return tasks_types

def create_task_type(new_task_type: TaskType):
    task_types_raw = db_provider.tasks_types_db.find(
        {"id": new_task_type.id}
    )
    task_types = [task_type for task_type in task_types_raw]

    if len(task_types) > 0:
        raise TaskTypeExist()

    new_task_type.save_db()
    

def get_bot_tasks(
    query: BotTasksSearchQuery
) -> BotTasksSearch:
    filters: dict = query.collect_db_filters_query()
    bot_tasks_total_count = db_provider.bots_tasks_db.count_documents({})
    bot_tasks_raw = db_provider.bots_tasks_db.find(
        filters
    ).skip(query.skip).limit(query.limit).sort('created_date', -1)
    bot_tasks: list[BotTask] = [BotTask(**task) for task in bot_tasks_raw]
    bot_tasks_search = BotTasksSearch(
        bot_tasks=bot_tasks,
        total=bot_tasks_total_count
    )
    return bot_tasks_search

def create_bot_task(
    new_task: CreateBotTask
):
    task = BotTask(
        **new_task.dict(by_alias=True)
    )
    task.save_db()

def get_bot_task_by_id(
    id: UUID4
) -> BotTask | None:
    bot_task_raw = db_provider.bots_tasks_db.find_one(
        {"_id": id}
    )
    try:
        if (bot_task_raw):
            bot_task = BotTask(**bot_task_raw)
            return bot_task
        return None
    except:
        return None

def delete_bot_task(
    id: UUID4
):
    bot_task: BotTask | None = get_bot_task_by_id(id)
    if not bot_task:
        raise BotTaskNotFound()
    bot_task.remove_db()

def update_bot_task(
    id: UUID4,
    new_task: CreateBotTask
):
    bot_task: BotTask | None = get_bot_task_by_id(id)

    if not bot_task:
        raise BotTaskNotFound()
    # check if task is already finished & raise error
    if bot_task.isFinished():
        raise UpdateFinishedTaskError()

    bot_task = bot_task.copy(update=new_task.dict())
    # Reset errors & next time run on save
    reset_bot_task_params(
        task = bot_task,
        reset_errors=True,
        reset_next_run=True,
        reset_status_if_active=True
    )
    # saving task
    bot_task.update_db()

def reset_bot_task_params(
    task: BotTask,
    reset_errors: bool = True,
    reset_next_run: bool = True,
    reset_status_if_active: bool = True
):
    # TODO: add bot_used resetting
    # mb when change task_type or 
    # task target data
    if reset_errors:
        task.error = None
    if reset_next_run:
        task.next_run_timestamp = None
    if reset_status_if_active:
        if task.is_active:
            task.status = BotTaskStatusEnum.running

def bot_task_check_need_run(
    bot_task: BotTask
):
    """
    Check, if bot task need to run
    Task will not run if:
        - task status is not 'running'
        - task not is_active
        - if next_run_timestamp is not None and time not
        come yet
    """
    # check status & active
    if ((not bot_task.status == BotTaskStatusEnum.running) or 
        (not bot_task.is_active)):
        return False
    print('first check passed')
    # check, if time come
    # TODO: fix behavior
    now =  int(get_time_now().timestamp())
    need_run = bot_task.next_run_timestamp
    if ((not need_run is None) and
        (need_run > now)):
        return False
    return True


def process_bot_task(
    bot_task: BotTask
):
    # TODO add logging?
    """
        Call function that responsbile for
        task processing, that function should
            - check if bot need to run task
            - run task according task type
    """
    # check, if need to run task
    if not bot_task_check_need_run(bot_task):
        lgd('Task dont need to be run')
        return False
    # process like_post task
    if bot_task.task_type == TaskTypeEnum.like_post:
        process_like_post_task(bot_task)
    # process regular_like_group task
    if bot_task.task_type == TaskTypeEnum.regular_like_group:
        socials.apps.bots_tasks.regular_like_group.main.process_regular_like_group_task(
            bot_task
        )
