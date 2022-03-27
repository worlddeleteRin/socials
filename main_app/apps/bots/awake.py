from apps.bots.models import Bot

def check_bot_need_awake(
    bot: Bot
) -> bool:
    # compare time
    return False

def process_bot_awake(
    bot: Bot
):
    need_awake = check_bot_need_awake(bot=bot)
    if not need_awake:
        return
    # call awake bot
    # update bot in db
