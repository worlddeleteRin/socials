from apps.bots_tasks.models import BotTaskError

NoBotsForTaskError = BotTaskError(
    error_msg = 'No more bots to make task'
)
