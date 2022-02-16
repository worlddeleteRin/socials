import pytz
from datetime import datetime

def get_time_now() -> datetime:
    current_timezone = pytz.timezone('Europe/Moscow')
    time = datetime.now(tz = current_timezone)
    return time
