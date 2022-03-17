from apps.bots.bots import get_bots
from apps.bots.models import Bot, BotSearch, BotSearchQuery, PlatformEnum
from apps.bots_events.models import BotEvent
from apps.bots_tasks.enums import TaskTypeEnum
from apps.bots_tasks.like_post.models import LikePostResultMetrics, LikePostTargetData
from apps.bots_tasks.models import BotTask, BotTaskError
from apps.bots_tasks.task_errors import NoBotsForTaskError, VkErrorGetWallPost, VkErrorPostUrl
from apps.bots_tasks.utils import calculate_next_time_run, get_time_left_delimeter_from_timestamp
# from ..vk_core.client import VkClient
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
    # check if can get wall post
    if not bot_task.task_target_data.like_post:
        bot_task.setError(VkErrorGetWallPost)
        return
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
    print('wall is', wall.__dict__)
    print('post url info is', postUrlInfo)
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
            # add metrics TODO
            metrics.like_count += 1
            # add bot event TODO
            event = BotEvent(
                event_type = TaskTypeEnum.like_post, 
                platform = PlatformEnum.vk,
                bot_id = bot.id,
                task_id = bot_task.id,
                count_amount = 1
            )
            event.save_db()
        except Exception as e:
            print('exception occured', e)
            bot_task.setError(BotTaskError.dummy_error(e))

def process_like_post_task(
    bot_task: BotTask
):
    # return if not platform specified
    if not bot_task.platform:
        return
    # return id not data for liked post
    if not bot_task.task_target_data.like_post:
        return
    # if not metrics add, add it
    if not bot_task.task_result_metrics.like_post:
        bot_task.task_result_metrics.like_post = LikePostResultMetrics()
    # assign values
    data: LikePostTargetData = bot_task.task_target_data.like_post
    metrics: LikePostResultMetrics = bot_task.task_result_metrics.like_post

    need_like_total: int = data.like_count
    already_liked: int =  metrics.like_count
    # get time delimeter
    time_delimeter: int = get_time_left_delimeter_from_timestamp(
        data.date_finish.int_timestamp()
    )
    # count need process now 
    process_now_count = int((need_like_total - already_liked) / time_delimeter)
    if process_now_count < 1:
        process_now_count = 1
    # define bots search filters
    bot_filter_query = BotSearchQuery(
        is_active = True,
        is_in_use = True,
        limit = process_now_count,
        platform = bot_task.platform,
        exclude_by_ids = bot_task.bots_used,
    )
    # get bots for task 
    bot_search: BotSearch = get_bots(bot_filter_query)
    bots: list[Bot] = bot_search.bots
    # check if not bots stop task attach error
    if len(bots) == 0:
        bot_task.setError(NoBotsForTaskError)
        bot_task.update_db()
        return
    # 
    print('time delimeter is', time_delimeter)
    print('need process now:', process_now_count)
    # wall print('bots for task are', bots)
    print('bots len is ', len(bots))
    print('run process like post task')
    # run task based on platform type
    if bot_task.platform == PlatformEnum.vk:
        like_post_vk(
            bots = bots,
            like_count = process_now_count,
            metrics = metrics,
            bot_task = bot_task
        )
        bot_task.update_db()
    if not bot_task.isRunning():
        return
    # get fresh data TODO: can be improved
    data: LikePostTargetData = bot_task.task_target_data.like_post
    metrics: LikePostResultMetrics = bot_task.task_result_metrics.like_post

    need_like_total: int = data.like_count
    already_liked: int =  metrics.like_count

    # check if task is completed
    # set task finished if task completed
    if already_liked >= need_like_total:
        bot_task.setFinished()
        bot_task.update_db()
        return

    # calculate next time need run TODO
    next_time_run = calculate_next_time_run(
        time_end = data.date_finish.int_timestamp(),
        need_make = need_like_total - already_liked,
    )
    bot_task.next_run_timestamp = next_time_run
    # update bot db
    bot_task.update_db()
    # ?

