from apps.bots_tasks.models import BotTaskError

NoBotsForTaskError = BotTaskError(
    error_msg = 'No more bots to make task'
)
VkErrorPostUrl = BotTaskError(
    error_msg = 'Vk error not correct post url',
)
VkErrorGetWallPost = BotTaskError(
    error_msg = 'Vk error get wall post',
)
