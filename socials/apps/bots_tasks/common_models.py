from pydantic import BaseModel
from datetime import datetime

from pydantic.class_validators import validator

from socials.apps.site.utils import get_time_now

class TaskDateFinish(BaseModel):
    date: datetime

    """
    @staticmethod
    def from_work_lag_enum(
    ):
        pass
    """
    @validator('date', pre=True)
    def check_date(cls, v):
        if v == '':
            return get_time_now()
        return v
    def int_timestamp(self):
        return int(self.date.timestamp())

