import random
from pydantic.class_validators import root_validator
from pydantic.main import BaseModel

from socials.apps.bots_tasks.common_models import TaskDateFinish
from socials.apps.bots_tasks.enums import WorkLagEnum

class RegularLikeGroupTargetData(BaseModel):
    # group|account id
    group_id: str
    # like count for each post
    like_count: int
    # like random threshold
    like_random_threshold: int = 0
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
    def get_like_count(self) -> int:
        """
            Returns random like count in range
            `(like_count - like_random_threshold; like_count)`
        """
        if self.like_random_threshold == 0:
            return self.like_count
        if self.like_random_threshold > self.like_count:
            self.like_random_threshold = self.like_count - 2
        rnd = random.randrange(
            self.like_count - self.like_random_threshold,
            self.like_count
        )
        return rnd


class RegularLikeGroupResultMetrics(BaseModel):
    like_count: int = 0
    processed_posts_ids: list[str] = []
