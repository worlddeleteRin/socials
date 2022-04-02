from socials.apps.bots.bot_exceptions import PlatformBotNotFoundException
from socials.apps.bots.models import Bot
from vk_core.client import VkClient
from vk_core.models import BaseVkErrorException
from vk_core.users.main import VkGetUsersQuery, VkUser, VkUserModel

def check_banned_vk(bot: Bot) -> bool:
    client = VkClient(
        access_token=bot.access_token
    )

    try:
        users: list[VkUserModel] = VkUser(
            client=client
        ).get()
    except BaseVkErrorException as e:
        print('handling base vk error exception')
        # TODO: move to vk core method mb
        if e.response:
            print('response json is', e.response.json())
            if e.response.json()['error']['error_code'] == 5:
                return True
        raise e

    if len(users) == 0:
        raise PlatformBotNotFoundException()
    vk_user = users[0]
    if not bot.platform_data.vk:
        bot.platform_data.vk = vk_user
    return vk_user.is_banned()
