from enum import Enum

class TaskTypeEnum(str, Enum):
    like_post = 'like_post'
    repost_post = 'repost_post'
    dummy = 'dummy'

class BotTaskStatusEnum(str, Enum):
    running = 'running'
    stopped = 'stopped'
    finished = 'finished'
    error = 'error'

class FrequencyTypeEnum(str, Enum):
    once = 'once'
    periodicly = 'periodicly'

class WorkLagEnum(str, Enum):
    immediately = 'Immediately'
    one_minute = '1 minute'
    five_minutes = '5 minutes'
    ten_minutes = '10 minutes'
    thirty_minutes = '30 minutes'
    one_hour = '1 hour'
    three_hours = '3 hours'
    one_day = '1 day'
    two_days = '2 days'
    three_days = '3 days'
    one_week = '1 week'
    one_month = 'one month' 
    custom_date = 'Custom date'