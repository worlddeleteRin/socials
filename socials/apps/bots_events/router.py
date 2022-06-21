from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from socials.apps.bots_events.bots_events import get_bot_events

from socials.apps.bots_events.models import BotEventsSearch, GetBotEventsQuery
from socials.apps.users.user import get_current_admin_user


router = APIRouter(
    prefix= "/bots_events",
    tags= ["bots_events"],
    dependencies=[
        # admin dependency
        Depends(get_current_admin_user)
    ]
)

@router.get("/", response_model=BotEventsSearch)
def get_bots_events(
    query: GetBotEventsQuery = Depends()
):
    return get_bot_events(query=query)
