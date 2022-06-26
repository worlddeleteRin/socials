import os
from socials.config import settings
os.environ['env_mode'] = settings.env_mode
import time
from socials.apps.bots_tasks.models import *
from socials.apps.bots_tasks.enums import *
from socials.apps.bots_tasks.main import get_bot_tasks, process_bot_task
from socials.logging import lgd,lgw,lge

time_to_sleep = 3

def process_tasks(
    include_selenium_tasks = False,
    process_tasks_per_cycle = 10
):
    lgd('** Run process youtube tasks **')
    try:
        bot_tasks_query = BotTasksSearchQuery(
            platform = PlatformEnum.yt,
            status = BotTaskStatusEnum.running,
            is_active=True,
            include_hidden=True,
            limit=process_tasks_per_cycle,
            include_selenium_tasks=include_selenium_tasks,
            sort_by_updated_date=SortingOrder.ascending
        )
        bot_tasks_search: BotTasksSearch = get_bot_tasks(
            query = bot_tasks_query
        )
        for bot_task in bot_tasks_search.bot_tasks:
            process_bot_task(
                bot_task
            )
    except Exception as e:
        lge(f'error while run process tasks {e}')
        pass
    time.sleep(time_to_sleep)

if __name__ == '__main__':
    while True:
        process_tasks()
