from apps.bots.bots import get_bots
from apps.bots.models import Bot, BotSearch, BotSearchQuery, PlatformEnum
from apps.bots_tasks.like_post.models import LikePostResultMetrics, LikePostTargetData
from apps.bots_tasks.models import BotTask
from apps.bots_tasks.utils import get_time_left_delimeter_from_timestamp

def like_post_vk(
    bots: list[Bot],
    like_count: int,
    bot_task: BotTask
):
    pass

def process_like_post_task(
    bot_task: BotTask
):
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
    liked: int =  metrics.like_count
    # get time delimeter
    time_delimeter: int = get_time_left_delimeter_from_timestamp(
        int(data.date_finish.date.timestamp())
    )
    # count need process now 
    process_now_count = int((need_like_total - liked) / time_delimeter)
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
    # 
    print('time delimeter is', time_delimeter)
    print('need process now:', process_now_count)
    print('bots for task are', bots)
    print('bots len is ', len(bots))
    print('run process like post task')
    # run task based on platform type
    if bot_task.platform == PlatformEnum.vk:
        like_post_vk(
            bots = bots,
            like_count =process_now_count,
            bot_task = bot_task
        )
