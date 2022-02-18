from fastapi.routing import APIRouter
from fastapi import Depends
from apps.users.user import get_current_admin_user
from .bots import *
from .models import *


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

@router.get("/{id}", response_model = Bot)
def get_bot_request(
    id: UUID4,
    admin_user = Depends(get_current_admin_user)
):
    print('id is', id)
    bot = get_bot_by_id(id)
    if not bot:
        return None
    # return []
    return bot.dict()
