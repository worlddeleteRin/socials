from pydantic.class_validators import root_validator
from pydantic.main import BaseModel

from apps.bots_tasks.common_models import TaskDateFinish
from apps.bots_tasks.enums import WorkLagEnum

class RegularLikeGroupTargetData(BaseModel):
    # group|account id
    group_id: str
    # like count for each post
    like_count: int
    # last n posts to parse
    last_posts_check_count: int
    # frequency to parse last n posts
    check_frequency: WorkLagEnum = WorkLagEnum.ten_minutes
    # work_lag for each post like
    work_lag: WorkLagEnum = WorkLagEnum.one_minute

    """ 
    @root_validator
    def validate_like_post_target_data(cls, values):
        pass
    """


class RegularLikeGroupResultMetrics(BaseModel):
    like_count: int = 0
    processed_posts_ids: list[str] = []
