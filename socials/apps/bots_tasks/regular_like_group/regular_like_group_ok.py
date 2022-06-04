from ok_core.client import OkClient
from ok_core.group.main import GetGroupPostIdsQuery, OkGroup
from ok_core.likes.main import OkLikes
from ok_core.user.main import OkUser
from socials.apps.bots_tasks.regular_like_group.models import RegularLikeGroupResultMetrics, RegularLikeGroupTargetData
from socials.apps.bots.models import Bot, PlatformEnum
from socials.apps.bots.bots import get_random_bot_client_by_platform
from socials.apps.bots_tasks.task_errors import ErrorGettingDefaultBotClient, info_error
from socials.apps.bots_tasks.enums import TaskTypeEnum
from socials.apps.bots_tasks.like_post.models import LikePostTargetData
from socials.apps.bots_tasks.models import BotTask, CreateBotTask, TaskTargetData
from socials.apps.bots_tasks.regular_like_group.errors import ErrorGettingGroupInfo
from socials.logging import lgd,lgw,lge

import socials.apps.bots_tasks.main

"""
    Regular like group for ok platform
"""
def regular_like_group_ok(
    task: BotTask,
    data: RegularLikeGroupTargetData,
    metrics: RegularLikeGroupResultMetrics
):
    lgd('** Run regular like group ok task **')
    # assign necessary data params
    group_id = data.group_id
    posts_check_count = data.last_posts_check_count
    work_lag = data.work_lag
    last_posts_ids = metrics.processed_posts_ids

    # get random bot for default client
    try:
        bot: Bot = get_random_bot_client_by_platform(PlatformEnum.ok)
    except:
        task.setError(ErrorGettingDefaultBotClient)
        return  
    # initialize default client
    client = OkClient()
    # initialize ok user
    user = OkUser(client=client, **bot.dict())
    # lgd(f'user: {user}')
    # initialize group instance
    group = OkGroup(id=group_id, client=client)
    # TODO implement check group info

    # try to get last n posts
    query = GetGroupPostIdsQuery(
        last_n_posts=posts_check_count
    )
    post_ids: list[str] = []
    try:
        post_ids = group.get_group_post_ids(
            user=user,
            query=query
        )
    except Exception as e:
        task.setError(info_error(e))
        return
    if len(post_ids) == 0:
        task.setError(info_error(
            "Cant get group post ids"
        ))
        return
    # filter for post that not processed
    not_processed = [
        id for id in post_ids if id not in last_posts_ids
    ]
    # add new post ids to processed
    metrics.processed_posts_ids = not_processed
    if len(not_processed) == 0:
        lgd('All posts are processed')
        return

    # create like task for each not processed post
    for id in not_processed:
        like_post_data = LikePostTargetData(
            post_link=group.makeGroupTopicUrl(id),
            like_count = data.get_like_count(),
            work_lag = work_lag
        )
        new_task = CreateBotTask(
            title = f"regular task like for {group_id}",
            platform = PlatformEnum.ok,
            task_type = TaskTypeEnum.like_post,
            task_target_data = TaskTargetData(
                like_post = like_post_data
            ),
            delete_after_finished = True,
            is_hidden = True,
            is_active = True,
            is_testing=task.is_testing)
        try:
            socials.apps.bots_tasks.main.create_bot_task(new_task=new_task)
        except Exception as e:
            lge(f"error while create hidden like task: {e}")
            pass
