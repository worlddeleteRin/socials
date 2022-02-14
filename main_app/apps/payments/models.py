from typing import Optional, List
from enum import Enum

from pydantic import UUID4, BaseModel, Field

class PaymentMethodEnum(str, Enum):
    cash = "cash"
    card_courier = "card_courier"
    card = "card"


class PaymentMethod(BaseModel):
	id: str = Field(alias="_id")
	name: str
