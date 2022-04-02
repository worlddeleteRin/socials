from datetime import datetime
from socials.apps.bots_tasks.enums import WorkLagEnum
from socials.apps.site.utils import get_time_now, get_time_now_timestamp


def get_time_left_delimeter_from_timestamp(
    time_end: int
) -> int:
    time_now: int = get_time_now_timestamp()
    time_left_seconds: int = time_end - time_now 
    time_left_minutes: int = int(time_left_seconds / 60)
    time_left_hours: int = int(time_left_minutes / 60)
    time_left_days: int = int(time_left_hours / 60)

    if time_left_days > 1:
        return time_left_days
    if time_left_hours > 1:
        return time_left_hours
    if time_left_minutes > 1:
        return time_left_minutes
    if time_left_seconds < 1:
        return 1
    return time_left_seconds

def get_datetime_from_work_lag(
    lag: WorkLagEnum
) -> datetime:
    seconds = 0
    if lag == WorkLagEnum.immediately:
        return datetime.now()
    if lag == WorkLagEnum.one_minute:
        seconds = 60
    if lag == WorkLagEnum.five_minutes:
        seconds = 5 * 60
    if lag == WorkLagEnum.ten_minutes:
        seconds = 10 * 60
    if lag == WorkLagEnum.thirty_minutes:
        seconds = 30 * 60
    if lag == WorkLagEnum.one_hour:
        seconds = 1 * 60 * 60
    if lag == WorkLagEnum.three_hours:
        seconds = 3 * 60 * 60
    if lag == WorkLagEnum.one_day:
        seconds = 1 * 24 * 60 * 60
    if lag == WorkLagEnum.two_days:
        seconds = 2 * 24 * 60 * 60
    if lag == WorkLagEnum.three_days:
        seconds = 3 * 24 * 60 * 60
    if lag == WorkLagEnum.one_week:
        seconds = 1 * 7 * 24 * 60 * 60
    if lag == WorkLagEnum.one_month:
        seconds = 1 * 30 * 24 * 60 * 60
    timestamp = int(datetime.now().timestamp())
    final_timestamp = timestamp + seconds
    date = datetime.fromtimestamp(final_timestamp)
    return date

def calculate_next_time_run(
    # int timestamp of date finish
    time_end: int,
    # how much count need to make more
    need_make: int
) -> int:
    now = get_time_now_timestamp()
    if now > time_end:
        return now
    process_time = time_end - now
    time_per_task = process_time / need_make
    next_time = now + time_per_task
    if next_time > time_end:
        return int(time_end)
    return int(next_time)
    

