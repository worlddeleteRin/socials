from socials.apps.bots.models import Bot, PlatformEnum
from socials.apps.bots_events.models import BotEvent
from socials.apps.bots_tasks.enums import TaskTypeEnum
from socials.apps.bots_tasks.like_post.models import LikePostResultMetrics
from socials.apps.bots_tasks.models import BotTask, BotTaskError
from socials.apps.bots_tasks.task_errors import VkErrorGetWallPost, VkErrorPostUrl
from vk_core.client import VkClient
from vk_core.likes.likes import AddLikeQuery, IsLikedQuery, LikeTargetEnum, Likes
from vk_core.likes.models import IsLikedResponse
from vk_core.wall.wall import VkPost, VkWall, WallPostGetByIdQuery


def like_post_vk(
    bots: list[Bot],
    like_count: int,
    metrics: LikePostResultMetrics,
    bot_task: BotTask
):
    print('run like post vk')
    # check if target data specified
    if not bot_task.task_target_data.like_post:
        bot_task.setError(VkErrorGetWallPost)
        return
    # check if can get wall post
    link = bot_task.task_target_data.like_post.post_link
    postUrlInfo = VkWall.getOwnerItemIdsFromUrl(
        link
    )
    if not postUrlInfo:
        bot_task.setError(VkErrorPostUrl)
        return

    defaultClient = VkClient(
        access_token = bots[0].access_token
    )
    wall = VkWall(client = defaultClient, owner_id = int(postUrlInfo[0]))
    postQuery = WallPostGetByIdQuery(
        posts = f"{postUrlInfo[0]}_{postUrlInfo[1]}"
    )
    # print('wall is', wall.__dict__)
    # print('post url info is', postUrlInfo)
    try:
        currentPost: VkPost = wall.getById(query = postQuery)[0]
    except Exception as e:
        print('error get post', e)
        bot_task.setError(VkErrorGetWallPost)
        return
    isLikedQuery = IsLikedQuery(
        type = LikeTargetEnum.post,
        owner_id = wall.owner_id,
        item_id = currentPost.id
    )
    likeQuery = AddLikeQuery(
        type = LikeTargetEnum.post,
        owner_id = wall.owner_id,
        item_id = currentPost.id
    )

    print('post id kis', currentPost.id)
    print('like Query is', likeQuery)
    for bot in bots:
        # set up client
        client = VkClient(
            access_token = bot.access_token
        )
        print('client is', client)
        # check, if bot already like post
        isLiked: IsLikedResponse = Likes(client = client).isLiked(
            query = isLikedQuery
        )
        print('isLiked query is', isLiked)
        if (isLiked.isLiked()):
            bot_task.bots_used.append(bot.id)
            continue

        # try to like post
        response = Likes(client = client).add(query = likeQuery)
        print('response is', response)
        # add bot id to used
        try:
            bot_task.bots_used.append(bot.id)
            # add metrics 
            bot_task.sync_metrics()
            metrics = bot_task.task_result_metrics.like_post
            metrics.like_count += 1
            bot_task.update_db()
            # add bot event
            event = BotEvent(
                event_type = TaskTypeEnum.like_post, 
                platform = PlatformEnum.vk,
                bot_id = bot.id,
                task_id = bot_task.id,
                count_amount = 1
            )
            event.save_db()
            # TODO need sync
            # update bot metrics like_count
            bot.daily_metrics.like_count += 1
            bot.hourly_metrics.like_count += 1
            # update bot last used
            bot.update_db(update_used=True)
        except Exception as e:
            print('exception occured', e)
            bot_task.setError(BotTaskError.dummy_error(e))
