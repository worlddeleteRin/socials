from .models import *
from database.main_db import db_provider
from pymongo.cursor import Cursor 
from pydantic import UUID4

def get_bots(
    query: BotSearchQuery
):
    botsTotal = db_provider.bots_db.count_documents({})

    botsCursor: Cursor = db_provider.bots_db.find({
    }).limit(query.limit)

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



