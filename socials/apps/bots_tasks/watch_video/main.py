from socials.apps.bots.models import PlatformEnum
from socials.apps.bots_tasks.models import BotTask
from socials.apps.bots_tasks.task_errors import BotErrorsEnum, BotInfoEnum, NoPlatformSpecified, err, info_error
from socials.apps.bots_tasks.utils import calculate_next_time_run, get_time_left_delimeter_from_timestamp
from socials.apps.bots_tasks.watch_video.models import WatchVideoResultMetrics, WatchVideoTargetData
from socials.apps.bots_tasks.watch_video.watch_video_yt import watch_video_yt
from socials.apps.site.utils import get_time_now
from socials.logging import lgd,lgw,lge


def process_watch_video_task(
    task: BotTask,
):
    lgd("** Run process watch video task **")
    # return if not platform specified
    if not task.platform:
        msg = BotErrorsEnum.no_platform_specified
        lge(msg)
        task.setError(err(msg))
        return
    # retur if no task data specified
    if not task.task_target_data.watch_video:
        msg = BotErrorsEnum.no_platform_specified
        lge(msg)
        task.setError(err(msg))
        return
    # add metrics if not exist
    if not task.task_result_metrics.watch_video:
        task.task_result_metrics.watch_video = WatchVideoResultMetrics()

    # assign values
    data: WatchVideoTargetData = task.task_target_data.watch_video
    metrics: WatchVideoResultMetrics = task.task_result_metrics.watch_video

    need_watch_count: int = data.watch_count
    need_watch_seconds:int = data.watch_second
    already_watched: int = metrics.watch_count

    # get time delimeter
    time_delimeter: int = get_time_left_delimeter_from_timestamp(
        data.date_finish.int_timestamp()
    )
    # count need process now 
    process_now_count = int((need_watch_count - already_watched) / time_delimeter)
    lgd(f'date finish: {data.date_finish}, now: {get_time_now()}')
    lgd(f'need: {need_watch_count}, watched: {already_watched}, delimeter: {time_delimeter}')
    lgd(f'process now count is {process_now_count}')
    if process_now_count < 1:
        process_now_count = 1

    """
    # handle testing task
    if task.is_testing:
        lgd(BotInfoEnum.just_success_testing)
        task.remove_db()
        return
    """

    # run task
    if task.platform == PlatformEnum.yt:
        # run on youtube platform
       watch_video_yt(
            task=task,
            data=data,
            metrics=metrics,
            process_now=process_now_count
        )

    metrics = task.task_result_metrics.watch_video

    # task.update_db()
    if task.hasError():
        task.update_or_remove_db()
        return

    if metrics.watch_count >= data.watch_count:
        task.setFinished()
        task.update_or_remove_db()
        return

    # calculate next time need run
    next_time_run = calculate_next_time_run(
        time_end = data.date_finish.int_timestamp(),
        need_make = data.watch_count - metrics.watch_count,
    )
    lgd(f'Time end: {data.date_finish}')
    lgd(f'Next time run: {next_time_run}')
    task.next_run_timestamp = next_time_run
    # update bot db
    lgd(f'out of scope task metrics watch count: {task.task_result_metrics.watch_video.watch_count}')
    task.update_db(update_metrics=False)
