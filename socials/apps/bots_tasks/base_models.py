from pydantic.main import BaseModel


class BaseTaskTargetData(BaseModel):

    def on_create(self):
        pass
