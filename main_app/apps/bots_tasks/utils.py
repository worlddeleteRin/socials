
from apps.site.utils import get_time_now, get_time_now_timestamp


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
    return time_left_seconds
