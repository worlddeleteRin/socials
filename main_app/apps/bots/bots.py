from database.main_db import db_provider
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
    ).sort('created_time', -1).skip(query.offset).limit(query.limit)

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



