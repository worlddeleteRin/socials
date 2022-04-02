import os
from config import settings
os.environ['env_mode'] = settings.env_mode
import time
from apps.bots_tasks.models import *
from apps.bots_tasks.enums import *
from apps.bots_tasks.main import get_bot_tasks, process_bot_task

time_to_sleep = 3

def process_tasks():
    print('run process tasks...')
    try:
        bot_tasks_query = BotTasksSearchQuery(
            status = BotTaskStatusEnum.running,
            is_active=True,
            include_hidden=True
        )
        bot_tasks_search: BotTasksSearch = get_bot_tasks(
            query = bot_tasks_query
        )
        # print('bot tasks are', bot_tasks_search.bot_tasks)
        for bot_task in bot_tasks_search.bot_tasks:
            process_bot_task(
                bot_task
            )
    except Exception as e:
        print('error while run process tasks', e)
        pass
    time.sleep(time_to_sleep)
    # process_tasks()

if __name__ == '__main__':
    while True:
        process_tasks()
