from enum import Enum
from typing import Any
from socials.apps.bots_tasks.models import BotTaskError

def info_error(error: Any):
    return BotTaskError(
        error_msg = f"{error}"
    )

class BotErrorsEnum(str, Enum):
    no_platform_specified = 'Не указана платформа для таска'
    no_task_data_specified = 'Не указаны данные для таска'

class BotInfoEnum(str, Enum):
    just_success_testing = '✔️ Просто удачный тестовый таск'

def err(e: BotErrorsEnum):
    return BotTaskError(
        error_msg = e
    )

NoBotsForTaskError = BotTaskError(
    error_msg = 'No more bots to make task'
)
VkErrorPostUrl = BotTaskError(
    error_msg = 'Vk error not correct post url',
)
VkErrorGetWallPost = BotTaskError(
    error_msg = 'Vk error get wall post',
)

NoPlatformSpecified = BotTaskError(
    error_msg = 'No platform specified',
)

NoTaskDataSpecified = BotTaskError(
    error_msg = 'No task data specified',
)

ErrorGettingDefaultBotClient = BotTaskError(
    error_msg = 'Error while getting default bot client for task',
)

CantProceedTaskPlatform = BotTaskError(
    error_msg = 'Cant run task on specified platform'
)

# ok exceptions
OkErrorGetTopic = BotTaskError(
    error_msg = 'Не выходит получить инфу о посте, скорее всего указана неверная ссылка, либо пост удален, либо его нет в группе. В крайнем случае стоит проверить код 🤓',
)
OkErrorData = BotTaskError(
    error_msg = 'Похоже что в задаче нехватает данных'
)
OkErrorPostUrl = BotTaskError(
    error_msg = 'Неверно указана ссылка на пост'
)


