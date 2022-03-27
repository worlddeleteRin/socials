from fastapi.routing import APIRouter
from fastapi import Depends
from apps.users.user import get_current_admin_user
from utils.responses import simple_success_response
from .bots import *
from .models import *
from .bot_exceptions import *


router = APIRouter(
    prefix= "/bots",
    tags= ["bots, bot"]
)

@router.get("/", response_model = BotSearch)
def get_bots_request(
    admin_user = Depends(get_current_admin_user),
    query: BotSearchQuery = Depends()
):
    botSearch: BotSearch = get_bots(query)
    return botSearch

@router.post("/")
def create_bot_request(
    bot: BotCreate,
    admin_user = Depends(get_current_admin_user),
):
    resp = create_bot(bot)
    return resp



# TODO: remove further?
@router.get("/testfilters")
def testfilters_get_bots_request(
    admin_user = Depends(get_current_admin_user),
    query: BotSearchQuery = Depends()
):
    return {
        "handled": query.__dict__,
        "to_apply": query.collect_db_filters_query()
    }

@router.get("/{id}", response_model = Bot)
def get_bot_request(
    id: UUID4,
    admin_user = Depends(get_current_admin_user)
):
    bot = get_bot_by_id(id)
    if not bot:
        return None
    # return []
    return bot.dict()

"""
Check if bot is banned
"""
@router.get("/{id}/check_banned")
def request_check_bot_banned(
    id: UUID4,
    admin_user = Depends(get_current_admin_user)
):
    bot = get_bot_by_id(id)
    if not bot:
        return None
    is_banned = check_is_banned(bot=bot)
    if is_banned:
        bot.set_banned()
    bot.update_db()
    return simple_success_response()

@router.delete("/{id}")
def remove_bot_request(
    id: UUID4,
    admin_user = Depends(get_current_admin_user)
):
    delete_bot_by_id(id)
    return {
        "success": True
    }

@router.patch("/{id}")
def update_bot_request(
    id: UUID4,
    update_bot: BotCreate,
    admin_user = Depends(get_current_admin_user)
):
    update_bot_by_id(id, update_bot)
    return {
        "success": True
    }
