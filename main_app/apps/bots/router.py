from fastapi.routing import APIRouter
from fastapi import Depends
from apps.users.user import get_current_admin_user
from .bots import *
from .models import Bot


router = APIRouter(
    prefix= "/bots",
    tags= ["bots, bot"]
)

@router.get("/", response_model = list[Bot])
def get_bots_request(
    admin_user = Depends(get_current_admin_user)
):
    bots = get_bots()
    # return []
    return bots

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
