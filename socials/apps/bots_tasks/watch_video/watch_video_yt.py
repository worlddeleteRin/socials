from socials.apps.bots.models import PlatformEnum
from socials.apps.bots_events.models import BotEvent
from socials.apps.bots_tasks.enums import TaskTypeEnum
from socials.apps.bots_tasks.models import BotTask
from socials.apps.bots_tasks.task_errors import info_error
from socials.apps.bots_tasks.watch_video.models import WatchVideoResultMetrics, WatchVideoTargetData
from yt_core.videos.main import YtVideo
from yt_core.videos.models import SeleniumWatchVideoParams


def watch_video_yt(
    task: BotTask,
    data: WatchVideoTargetData,
    metrics: WatchVideoResultMetrics,
    process_now: int
):
    instances_count = 4
    if process_now < instances_count:
        instances_count = process_now

    q = SeleniumWatchVideoParams(
        instances_count=instances_count,
        video_link=data.video_link,
        watch_time=data.watch_second
    )
    try:
        YtVideo.selenium_watch_video(q)
    except Exception as e:
        task.setError(info_error(e))
        return
    # set metrics after task done
    metrics.watch_count += instances_count
    # add event
    event = BotEvent(
        event_type = TaskTypeEnum.watch_video, 
        platform = PlatformEnum.yt,
        task_id = task.id,
        count_amount = instances_count
    )
    event.save_db()
