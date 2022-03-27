import time
from apps.bots.awake import process_bot_awake
from apps.bots.bots import get_bots

from apps.bots.models import BotSearchQuery

sleep_between_repeat = 3

def process_awake():
    print('run process awake...')
    bots_query = BotSearchQuery(
        has_rest_until=1,
        limit=100
    )
    bots = get_bots(query=bots_query).bots
    for bot in bots:
        process_bot_awake(bot=bot)
    print('bots len is ', len(bots))
    time.sleep(sleep_between_repeat)
    process_awake()

if __name__ == '__main__':
    process_awake()
