from pydantic.class_validators import root_validator
from pydantic.main import BaseModel
from socials.apps.bots_tasks.base_models import BaseTaskTargetData
from socials.apps.bots_tasks.common_models import TaskDateFinish

from socials.apps.bots_tasks.enums import WorkLagEnum
from socials.apps.bots_tasks.utils import get_datetime_from_work_lag
from socials.logging import lgd

d = get_datetime_from_work_lag(
    WorkLagEnum.one_minute
)
default_date_finish: TaskDateFinish = TaskDateFinish(date = d)

class WatchVideoTargetData(BaseTaskTargetData):
    video_link: str
    watch_count: int
    watch_second: int = 20
    work_lag: WorkLagEnum = WorkLagEnum.five_minutes
    date_finish: TaskDateFinish = default_date_finish

    @root_validator
    def validate_watch_video_target_data(cls, values):
        work_lag = values.get('work_lag')
        date_finish = values.get('date_finish')
        if (
            (not work_lag) and
            (not date_finish)
        ):
            raise ValueError('Specify work_lag or date_finish')
        if work_lag and (not isinstance(work_lag, WorkLagEnum)):
            raise ValueError('incorrect work_lag value')
        if work_lag == WorkLagEnum.custom_date:
            if not isinstance(date_finish, TaskDateFinish):
                raise ValueError('provide date_finish')
        return values

    def on_create(self):
        if not (self.work_lag == WorkLagEnum.custom_date):
            d = get_datetime_from_work_lag(self.work_lag)
            self.date_finish = TaskDateFinish(date=d)

class WatchVideoResultMetrics(BaseModel):
    watch_count: int = 0
