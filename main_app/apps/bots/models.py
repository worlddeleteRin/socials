import uuid
from pydantic import BaseModel, UUID4, Field
from datetime import datetime

from pymongo.results import InsertOneResult
from apps.site.utils import get_time_now
from typing import Optional

from database.main_db import db_provider
from pymongo import ReturnDocument

class Bot(BaseModel):
    """
        Base bot account model
    """
    id: UUID4 = Field(default_factory=uuid.uuid4)
    username: str = ""
    password: str = ""
    access_token: str = ""
    created_time: datetime = Field(default_factory=get_time_now)
    # TODO: replace with enum mb?
    created_source: Optional[str] = ""
    last_used: Optional[datetime] = None
    is_active: bool = False
    is_in_use: bool = False
    like_count: int = 0
    reply_count: int = 0
    comment_count: int = 0

    def save_db(self) -> InsertOneResult | None:
        inserted_bot: InsertOneResult = db_provider.bots_db.insert_one(self.dict(by_alias=True)
        )
        return inserted_bot or None

    def update_db(self):
        updated_bot = db_provider.bots_db.find_one_and_update(
            {"_id": self.id},
            {"$set": self.dict(by_alias=True)},
            return_document=ReturnDocument.AFTER
        )
        if updated_bot and updated_bot.dict():
            return Bot(**updated_bot.dict())
        return None

    def remove_db(self):
        db_provider.carts_db.remove(
            {"_id": self.id},
        )

    class Config:
        allow_population_by_field_name = True
