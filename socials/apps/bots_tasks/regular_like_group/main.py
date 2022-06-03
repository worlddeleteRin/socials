from socials.apps.bots.models import PlatformEnum
from socials.apps.bots_tasks.models import BotTask
from socials.apps.bots_tasks.regular_like_group.models import RegularLikeGroupResultMetrics, RegularLikeGroupTargetData
from socials.apps.bots_tasks.regular_like_group.regular_like_group_vk import regular_like_group_vk
from socials.apps.bots_tasks.task_errors import NoPlatformSpecified, NoTaskDataSpecified
from socials.apps.bots_tasks.utils import get_datetime_from_work_lag
from socials.apps.site.utils import get_time_now_timestamp
from socials.logging import lgd,lgw,lge


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


