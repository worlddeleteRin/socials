from pydantic import BaseModel
from datetime import datetime

class TaskDateFinish(BaseModel):
    date: datetime

    """
    @staticmethod
    def from_work_lag_enum(
    ):
        pass
    """
    def int_timestamp(self):
        return int(self.date.timestamp())

