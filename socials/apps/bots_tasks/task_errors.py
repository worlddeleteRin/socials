from typing import Any
from socials.apps.bots_tasks.models import BotTaskError

def info_error(error: Any):
    return BotTaskError(
        error_msg = f"{error}"
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


