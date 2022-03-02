from database.main_db import db_provider
from .models import *
from .bots_tasks_exceptions import *


def get_bot_tasks(
    query: BotTasksSearchQuery
) -> BotTasksSearch:
    filters: dict = query.collect_db_filters_query()
    bot_tasks_total_count = db_provider.bots_tasks_db.count_documents({})
    bot_tasks_raw = db_provider.bots_tasks_db.find(
        filters
    ).skip(query.skip).limit(query.limit)
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
    bot_task = bot_task.copy(update=new_task.dict())
    bot_task.update_db()

def bot_task_check_need_run(
    bot_task: BotTask
):
    pass
    # if bot_task.

def process_bot_task(
    bot_task: BotTask
):
    # TODO add logging?
    # check if bot need to run task
    """
        Call function that responsbile for
        task processing, that function should
            - count how much of task need to be run
            - set bots that will make that task
            - call platform plugin, paste task bots 
            make actual task
            - update metrics, both task | bot
            - ?
    """
    print('run process bot task')
