import time
import os
from socials.config import settings
# os.environ['env_mode'] = 'prod'
os.environ['env_mode'] = settings.env_mode
from socials.apps.bots.awake import process_bot_awake
from socials.apps.bots.bots import get_bots

from socials.apps.bots.models import BotSearchQuery

sleep_between_repeat = 3

def process_awake():
    print('run process awake...')
    try:
        bots_query = BotSearchQuery(
            has_rest_until=1,
            limit=100
        )
        bots = get_bots(query=bots_query).bots
        for bot in bots:
            process_bot_awake(bot=bot)
        print('bots len is ', len(bots))
    except:
        pass
    # time.sleep(sleep_between_repeat)
    # process_awake()

if __name__ == '__main__':
    process_awake()
