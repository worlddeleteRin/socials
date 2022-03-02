import time
from apps.bots_tasks.models import *
from apps.bots_tasks.bots_tasks import get_bot_tasks, process_bot_task

time_to_sleep = 3

def process_tasks():
    print('run process tasks...')
    bot_tasks_query = BotTasksSearchQuery(
        is_finished=False,
        is_active=True,
        has_error=False  
    )
    bot_tasks_search: BotTasksSearch = get_bot_tasks(
        query = bot_tasks_query
    )
    # print('bot tasks are', bot_tasks)
    for bot_task in bot_tasks_search.bot_tasks:
        process_bot_task(
            bot_task
        )
    time.sleep(3)
    process_tasks()

if __name__ == '__main__':
    process_tasks()
