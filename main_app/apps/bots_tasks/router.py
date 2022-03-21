from fastapi.routing import APIRouter
from fastapi import Depends
from apps.users.user import get_current_admin_user
from utils.responses import simple_success_response
from .bots_tasks import *
from .models import *
from .bots_tasks_exceptions import *


router = APIRouter(
    prefix= "/bots_tasks",
    tags= ["bots_tasks"]
)

@router.get("/", response_model=BotTasksSearch, response_model_by_alias=False)
def get_bots_tasks_request(
    admin_user = Depends(get_current_admin_user),
    query: BotTasksSearchQuery = Depends()
):
    return get_bot_tasks(query)

@router.post("/")
def create_bot_task_request(
    new_task: CreateBotTask,
    admin_user = Depends(get_current_admin_user)
):
    create_bot_task(new_task)
    return simple_success_response()

@router.get("/{id}")
def get_bot_task_by_id_request(
    id: UUID4
):
    return get_bot_task_by_id(id)

@router.delete("/{id}")
def delete_bot_task_request(
    id: UUID4
):
    delete_bot_task(id)
    return simple_success_response()

@router.patch("/{id}")
def update_bot_task_request(
    id: UUID4,
    new_task: CreateBotTask,
):
    update_bot_task(
        id = id, 
        new_task = new_task
    )
    return simple_success_response()
