from apps.bots.models import Bot
from apps.site.utils import get_time_now_timestamp

def check_bot_need_awake(
    bot: Bot
) -> bool:
    if not bot.rest_until:
        return True
    # compare time
    wake_time = int(bot.rest_until.timestamp())
    time_now = get_time_now_timestamp()
    if time_now >= wake_time:
        return True
    return False


def process_bot_awake(
    bot: Bot
):
    need_awake = check_bot_need_awake(bot=bot)
    if not need_awake:
        if not bot.is_resting:
            bot.set_resting()
            bot.update_db()
        return
    if need_awake:
        # call awake bot
        bot.set_awake()
        # update bot in db
        bot.update_db()
