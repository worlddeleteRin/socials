# import pytz
from datetime import datetime

# current_timezone = pytz.timezone('Europe/Moscow')

def get_time_now() -> datetime:
    time = datetime.utcnow()
    return time

def get_time_fromtimestamp(t: int) -> datetime:
    return datetime.fromtimestamp(t)

def get_time_now_timestamp() -> int:
    time_now = get_time_now()
    return int(time_now.timestamp())
