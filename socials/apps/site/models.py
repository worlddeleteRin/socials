import uuid
from typing import Optional, List

from pydantic import UUID4, BaseModel, Field

from socials.database.main_db import db_provider

from socials.config import settings

# site models changes here

class SocialContact(BaseModel):
    value: str = ""
    label: str = ""
    link: str = ""

    @staticmethod
    def get_defaults() -> list:
        telegram_link = "https://fast-code.ru/"
        viber_link = "https://fast-code.ru/"
        whatsapp_link = "https://fast-code.ru/"
        vk_link = "https://fast-code.ru/"
        inst_link = "https://fast-code.ru/"
        telegram = SocialContact(
            value = "telegram",
            label = "Telegram",
            link = telegram_link
        )
        viber = SocialContact(
            value = "viber",
            label = "Viber",
            link = viber_link
        )
        whatsapp = SocialContact(
            value = "whatsapp",
            label = "Whatsapp",
            link = whatsapp_link
        )
        vk = SocialContact(
            value = "vk",
            label = "Vk",
            link = vk_link
        )
        inst = SocialContact(
            value = "inst",
            label = "Instagram",
            link = inst_link
        )
        return [telegram, viber, whatsapp, vk, inst]

class CommonInfo(BaseModel):
    main_logo_link: str = ""

    @staticmethod
    def get_default():
        info = CommonInfo(
            main_logo_link = settings.base_static_url + "logo_variant.png",
        )
        return info

    class Config:
        allow_population_by_field_name = True

class ColorARGB(BaseModel):
    a: int = 255
    r: int = 255
    g: int = 255
    b: int = 255

class PickupAddress(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4, alias="_id")
    name: str
    info: str = ""

    def save_db(self):
        db_provider.pickup_addresses_db.insert_one(
            self.dict(by_alias=True)
        )

class StockItem(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4, alias="_id")
    title: str
    description: Optional[str]
    imgsrc: List[str] = []

    def save_db(self):
        db_provider.stocks_db.insert_one(
            self.dict(by_alias=True)
        )

class MenuLink(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4, alias="_id")
    link_name: Optional[str]
    link_path: Optional[str] 
    display_order: Optional[int] = 0


class MainSliderItem(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4, alias="_id")
    link_path: Optional[str] 
    display_order: Optional[int] = 0
    imgsrc: str

class RequestCall(BaseModel):
    name: str = ""
    phone: str = ""
    phone_mask: str = ""
