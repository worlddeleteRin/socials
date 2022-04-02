from apps.bots.models import Bot
from apps.bots_tasks.like_post.models import LikePostResultMetrics
from apps.bots_tasks.models import BotTask
from ok_core.client import OkClient
from ok_core.group.main import OkGroup
from ok_core.likes.main import OkAddLikeQuery, OkLikes
from ok_core.likes.models import OkAddLikeProviderEnum
from ok_core.mediatopic.main import GetMediatopicByIdsQuery, OkMediatopicResponse
from ok_core.mediatopic.main import OkMediatopic
from ok_core.user.main import OkUser


def like_post_ok(
    bots: list[Bot],
    like_count: int,
    metrics: LikePostResultMetrics,
    bot_task: BotTask
):
    print('run like post ok')
    # check if target data specified
    if not bot_task.task_target_data.like_post:
        # TODO
        # bot_task.setError(OkErrorGetTopic)
        return
    # check if can get topic post
    link = bot_task.task_target_data.like_post.post_link
    postUrlInfo = OkGroup.parseGroupTopicIdsFromUrl(url=link)
    if not postUrlInfo:
        # TODO
        # bot_task.setError(OkErrorPostUrl)
        return
    # init def client
    def_client = OkClient()
    # try to get media topic by id
    mt = OkMediatopic(client=def_client)
    topic_query = GetMediatopicByIdsQuery(
        topic_ids=f"{postUrlInfo[1]}"
    )
    try:
        topic_resp: OkMediatopicResponse = mt.get_by_ids(
            query=topic_query
        )
    except Exception as e:
        print('error get topic', e)
        # TODO
        # bot_task.setError(OkErrorGetTopic)
        return

    query = OkAddLikeQuery(
        group_id = postUrlInfo[0],
        item_id = postUrlInfo[1]
    )

    for bot in bots:
        # set up client
        user = OkUser(
            username = bot.username,
            password = bot.password
        )
        client = OkClient(user=user)
        likes = OkLikes(client=client)
        # try to like post
        likes.add(
            provider=OkAddLikeProviderEnum.selenium,
            query=query
        )
