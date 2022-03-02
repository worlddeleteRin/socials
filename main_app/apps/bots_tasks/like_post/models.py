from pydantic import BaseModel, root_validator
from apps.bots_tasks.enums import *
from apps.bots_tasks.common_models import *
from typing import Optional

from apps.site.utils import get_time_now, get_time_now_timestamp

class LikePostTargetData(BaseModel):
    post_link: str
    like_count: int
    work_lag: WorkLagEnum = WorkLagEnum.one_minute
    date_finish: Optional[TaskDateFinish] = None

    @root_validator
    def validate_like_post_target_data(cls, values):
        work_lag = values.get('work_lag')
        date_finish = values.get('date_finish')

        if not isinstance(work_lag, WorkLagEnum):
            raise ValueError('incorrect work_lag value')
        if work_lag == WorkLagEnum.custom_date:
            if not isinstance(date_finish, TaskDateFinish):
                raise ValueError('provide date_finish')
        if not (work_lag == WorkLagEnum.custom_date):
            values['date_finish'] = get_time_now()
        return values

class LikePostResultMetrics(BaseModel):
    like_count: int = 0
