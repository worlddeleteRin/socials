from apps.bots_tasks.like_post.models import LikePostResultMetrics, LikePostTargetData
from apps.bots_tasks.models import BotTask


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

    # count how much tasks need to be done
    # count how much bots need for task
    print('run process like post task')
