from socials.apps.bots_tasks.models import BotTaskError

ErrorGettingGroupInfo = BotTaskError(
    error_msg = 'Error cant get group info. Mb wrong id'
)

ErrorGettingWallPosts =  BotTaskError(
    error_msg = 'Error while getting group posts'
)
