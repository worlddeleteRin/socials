from socials.apps.bots.vk_utils import check_banned_vk
from socials.database.main_db import db_provider
from pymongo.cursor import Cursor 
from pydantic import UUID4
# local imports
from .models import *
from .bot_exceptions import *



def get_bots(
    query: BotSearchQuery
):
    botsTotal = db_provider.bots_db.count_documents({})

    bot_filters: dict = query.collect_db_filters_query()
    botsCursor: Cursor = db_provider.bots_db.find(
        bot_filters
    ).sort(query.sort_by, query.sort_direction).skip(query.offset).limit(query.limit)

    bots: list[Bot] = [Bot(**bot) for bot in botsCursor]
    botSearch = BotSearch(
        bots = bots,
        total = botsTotal
    )
    return botSearch

def get_bot_by_id(id: UUID4) -> Bot | None:
    botDict = db_provider.bots_db.find_one(
        {"id": id}
    )
    if not botDict:
        return None
    bot: Bot = Bot(**botDict)
    return bot

def delete_bot_by_id(id: UUID4):
    bot = get_bot_by_id(id)
    if not bot:
        raise BotNotFound()
    bot.remove_db()

def update_bot_by_id(
    id: UUID4,
    update_bot: BotCreate
):
    bot = get_bot_by_id(id)
    if not bot:
        raise BotNotFound()
    try:
        bot = bot.copy(update=update_bot.dict())
        bot.update_db()
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"error while updating bot {e}"
        )

def get_bot_by_username(username: str) -> Bot | None:
    botDict = db_provider.bots_db.find_one(
        {"username": username}
    )
    if not botDict:
        return None
    bot: Bot = Bot(**botDict)
    return bot

def create_bot(bot: BotCreate) -> dict:
    exist_bot = get_bot_by_username(bot.username)
    if exist_bot:
        raise BotAlreadyExists()
    new_bot = Bot(
        **bot.dict()
    )
    new_bot.save_db()
    return {
        "success": True
    }

def check_rate_limits(
    bot: Bot,
    check_like_limits: bool = False,
    check_reply_limits: bool = False,
    check_comment_limits: bool = False
) -> bool:
    # TODO: improve method
    if check_like_limits:
        h_like_limit = rate_limits.hourly.like_count
        d_like_limit = rate_limits.daily.like_count
        h_like = bot.hourly_metrics.like_count
        d_like = bot.daily_metrics.like_count
        if (
            (h_like >= h_like_limit) or
            (d_like >= d_like_limit)
        ):
            return False
    if check_reply_limits:
        h_reply_limit = rate_limits.hourly.like_count
        d_reply_limit = rate_limits.daily.like_count
        h_reply = bot.hourly_metrics.like_count
        d_reply = bot.daily_metrics.like_count
        if (
            (h_reply >= h_reply_limit) or
            (d_reply >= d_reply_limit)
        ):
            return False
    if check_comment_limits:
        h_comment_limit = rate_limits.hourly.like_count
        d_comment_limit = rate_limits.daily.like_count
        h_comment = bot.hourly_metrics.like_count
        d_comment = bot.daily_metrics.like_count
        if (
            (h_comment >= h_comment_limit) or
            (d_comment >= d_comment_limit)
        ):
            return False
    return True

def get_random_bot_client_by_platform(
    platform: PlatformEnum
) -> Bot: 
    query = BotSearchQuery(
        limit = 1, 
        is_active = 1,
        is_in_use = 1,
        platform = platform,
        sort_by = BotSortByEnum.last_used,
        sort_direction = 1,
    )
    bot_search = get_bots(query = query)
    return bot_search.bots[0]

def check_is_banned(
    bot: Bot
) -> bool:
    if bot.platform == PlatformEnum.vk:
        return check_banned_vk(bot = bot)
    return False
