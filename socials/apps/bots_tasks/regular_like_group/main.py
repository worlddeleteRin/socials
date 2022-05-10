from socials.apps.bots.bots import get_random_bot_client_by_platform
from socials.apps.bots.models import Bot, PlatformEnum
# from socials.apps.bots_tasks.main import create_bot_task
from socials.apps.bots_tasks.enums import TaskTypeEnum
from socials.apps.bots_tasks.like_post.models import LikePostTargetData
from socials.apps.bots_tasks.models import BotTask, CreateBotTask, TaskTargetData
from socials.apps.bots_tasks.regular_like_group.errors import ErrorGettingGroupInfo
from socials.apps.bots_tasks.regular_like_group.models import RegularLikeGroupResultMetrics, RegularLikeGroupTargetData
from socials.apps.bots_tasks.task_errors import ErrorGettingDefaultBotClient, NoPlatformSpecified, NoTaskDataSpecified, info_error
from socials.apps.bots_tasks.utils import get_datetime_from_work_lag
from socials.apps.site.utils import get_time_now_timestamp
from vk_core.client import VkClient
from vk_core.group.group import VkGroup, VkGroupModel
from vk_core.wall.wall import VkPost, VkWall, WallPostsGetQuery

import socials.apps.bots_tasks.main

"""
    Regular like group for vk platform
"""
def regular_like_group_vk(
    task: BotTask,
    data: RegularLikeGroupTargetData,
    metrics: RegularLikeGroupResultMetrics
):
    # assign necessary data params
    group_id = data.group_id
    posts_check_count = data.last_posts_check_count
    work_lag = data.work_lag
    last_posts_ids = metrics.processed_posts_ids

    # get random bot for default client
    try:
        bot: Bot = get_random_bot_client_by_platform(PlatformEnum.vk)
    except:
        task.setError(ErrorGettingDefaultBotClient)
        return  
    # initialize default client
    client = VkClient(
        bot.access_token 
    )
    # initialize group instance
    group = VkGroup(
        client = client,
        group_id = group_id
    )
    # try to get group info
    try:
        current_group: VkGroupModel = group.getById()
    except:
        task.setError(ErrorGettingGroupInfo)
        return
    # initialize wall instance
    wall = VkWall(
        client = client,
        owner_id = -current_group.id
    )
    # try to get last n posts from wall
    try:
        query = WallPostsGetQuery(
            count = posts_check_count
        )
        posts: list[VkPost] =  wall.get(query=query).items
    except Exception as e:
        # task.setError(ErrorGettingWallPosts)
        task.setError(info_error(e))
        return
    # filter for posts that not processed
    not_processed_posts = [
        post for post in posts if str(post.id) not in last_posts_ids
    ]
    # assign metrics processed posts with new ids
    metrics.processed_posts_ids = [str(post.id) for post in posts]
    if len(not_processed_posts) == 0:
        return

    # create like task for each not processed post
    for p in not_processed_posts:
        like_post_data = LikePostTargetData(
            post_link = p.get_vk_post_link(),
            like_count = data.get_like_count(),
            work_lag = work_lag
        )
        new_task = CreateBotTask(
            title = f"regular task like for ${group_id}",
            platform = PlatformEnum.vk,
            task_type = TaskTypeEnum.like_post,
            task_target_data = TaskTargetData(
                like_post = like_post_data
            ),
            delete_after_finished = True,
            is_hidden = True,
            is_active = True
        )
        try:
            socials.apps.bots_tasks.main.create_bot_task(new_task=new_task)
        except:
            pass

def process_regular_like_group_task(
    task: BotTask
):
    if not task.platform: 
        task.setError(NoPlatformSpecified)
        return
    if not task.task_target_data.regular_like_group: 
        task.setError(NoTaskDataSpecified)
        return
    if not task.task_result_metrics.regular_like_group:
        task.task_result_metrics.regular_like_group = RegularLikeGroupResultMetrics()

    # TODO: add metrics further
    
    # assign values
    data: RegularLikeGroupTargetData = task.task_target_data.regular_like_group
    metrics: RegularLikeGroupResultMetrics = task.task_result_metrics.regular_like_group

    if task.platform == PlatformEnum.vk:
        regular_like_group_vk(
            task = task,
            data = data,
            metrics = metrics,
        )
    task.task_target_data.regular_like_group = data
    task.task_result_metrics.regular_like_group = metrics
    task.update_db()
    if not task.isRunning() or task.hasError():
        return
    """
    Calculate next_time_run based on current
    check_frequency, if no error in task
    """
    timestamp_now = get_time_now_timestamp()
    check_frequency = data.check_frequency
    check_frequency_timestamp = int(get_datetime_from_work_lag(
        lag = check_frequency
    ).timestamp())
    # task.next_run_timestamp = timestamp_now + (timestamp_now - check_frequency_timestamp)
    task.next_run_timestamp = timestamp_now + (check_frequency_timestamp - timestamp_now)
    # update task in db
    task.update_db()


