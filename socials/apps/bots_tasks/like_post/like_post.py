from socials.apps.bots.bots import get_bots
from socials.apps.bots.models import Bot, BotSearch, BotSearchQuery, BotSortByEnum, PlatformEnum
from socials.apps.bots_tasks.like_post.like_post_ok import like_post_ok
from socials.apps.bots_tasks.like_post.like_post_vk import like_post_vk
from socials.apps.bots_tasks.like_post.models import LikePostResultMetrics, LikePostTargetData
from socials.apps.bots_tasks.models import BotTask
from socials.apps.bots_tasks.task_errors import CantProceedTaskPlatform, NoBotsForTaskError
from socials.apps.bots_tasks.utils import calculate_next_time_run, get_time_left_delimeter_from_timestamp

from socials.logging import lgd,lgw,lge

def process_like_post_task(
    bot_task: BotTask
):
    # return if not platform specified
    if not bot_task.platform:
        lge('Error no task platform specified')
        return
    # return id not data for liked post
    if not bot_task.task_target_data.like_post:
        lge('task target data not specified')
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
    lgd(f'need to set now likes: {process_now_count}')
    # define bots search filters
    bot_filter_query = BotSearchQuery(
        is_active = True,
        is_in_use = True,
        limit = process_now_count,
        platform = bot_task.platform,
        sort_by = BotSortByEnum.last_used,
        sort_direction = 1,
        exclude_by_ids = bot_task.bots_used,
        filter_by_rate_limits = 1
    )
    # get bots for task 
    bot_search: BotSearch = get_bots(bot_filter_query)
    bots: list[Bot] = bot_search.bots
    # check if not bots stop task attach error
    if len(bots) < process_now_count:
        lgw(f'bots are lower than need to like - {len(bots)} {process_now_count}')
    if len(bots) == 0:
        lge(NoBotsForTaskError.error_msg)
        bot_task.setError(NoBotsForTaskError)
        if bot_task.delete_after_finished:
            bot_task.remove_db()
        else:
            bot_task.update_db()
        return

    lgd('run process like post task')

    """
    if bot_task.is_testing:
        lgw('✔️ just success testing task, removing it ...')
        bot_task.remove_db()
        return
    """
    """
    Run task based on platform type
    """
    if bot_task.platform == PlatformEnum.vk:
        # run on vk platform
        like_post_vk(
            bots = bots,
            like_count = process_now_count,
            metrics = metrics,
            bot_task = bot_task
        )
        bot_task.update_db()
    elif bot_task.platform == PlatformEnum.ok:
        # run on ok platform
        like_post_ok(
            bots = bots,
            like_count = process_now_count,
            metrics = metrics,
            bot_task = bot_task
        )
    else:
        # no platform found, add error
        lge(CantProceedTaskPlatform.error_msg)
        bot_task.setError(CantProceedTaskPlatform)
        bot_task.update_or_remove_db()
        return
    if not bot_task.isRunning():
        lgw('task is not running')
        bot_task.update_db()
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
