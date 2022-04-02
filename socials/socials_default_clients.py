from vk_core.client import VkClient
from socials.config import settings


vk_default_client = VkClient(
    access_token=settings.vk_default_client_token
)
