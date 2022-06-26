# from fastapi import FastAPI from functools import lru_cache
from functools import lru_cache
import bson
from bson.binary import UuidRepresentation
from bson.codec_options import CodecOptions

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import pytz

from socials.config import settings

from pydantic import BaseModel

# from bson.binary import UuidRepresentation




class DbProvider(BaseModel):
    db_client: MongoClient
    db_main: Database 

    users_db: Collection
    users_addresses_db: Collection
    products_db: Collection
    categories_db: Collection
    carts_db: Collection
    coupons_db: Collection
    orders_db: Collection
    payment_methods_db: Collection
    delivery_methods_db: Collection
    pickup_addresses_db: Collection
    order_statuses_db: Collection
    stocks_db: Collection
    app_clients_db: Collection
    menu_links_db: Collection
    main_sliders_db: Collection
    bonuses_levels_db: Collection
    bots_db: Collection
    bots_tasks_db: Collection
    bots_events_db: Collection
    tasks_types_db: Collection

    class Config:
        arbitrary_types_allowed = True

@lru_cache
def setup_db_main() -> DbProvider:
    print('call setup db_main function')
    codecs: CodecOptions = CodecOptions(
        tz_aware=True,
        tzinfo=pytz.timezone('Europe/Moscow'),
        uuid_representation=UuidRepresentation.STANDARD
    )
    db_client = MongoClient(
        settings.DB_URL,
        UuidRepresentation = 'standard'
        # UuidRepresentation = 'unspecified'
        # UuidRepresentation = 'pythonLegacy'
    )
    db_main = db_client[settings.DB_NAME]
    db_provider = DbProvider(
                db_client = db_client,
                db_main = db_main,
                users_db = db_main["users"],
                users_addresses_db = db_main["users_addresses"],
                products_db = db_main["products"],
                categories_db = db_main["categories"],
                carts_db = db_main["carts"],
                coupons_db = db_main["coupons"],
                orders_db = db_main["orders"],
                payment_methods_db = db_main["payment_methods"],
                delivery_methods_db = db_main["delivery_methods"],
                pickup_addresses_db = db_main["pickup_addresses"],
                order_statuses_db = db_main["order_statuses"],
                stocks_db = db_main["stocks"],
                app_clients_db = db_main["app_clients"],
                menu_links_db = db_main["menu_links"],
                main_sliders_db = db_main["main_sliders"],
                bonuses_levels_db = db_main["bonuses_levels"],
                # bots_db = db_main["bots"],
                bots_db = db_main.get_collection( 
                    "bots", codec_options=codecs
                ),
                # bots_tasks_db = db_main["bots_tasks"],
                bots_tasks_db = db_main.get_collection( 
                    "bots_tasks", codec_options=codecs
                ),
                bots_events_db = db_main["bots_events"],
                tasks_types_db = db_main["tasks_types"]
            )
    return db_provider

db_provider = setup_db_main()




# db_client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://{}:{}@{}".format(db_username, db_password, db_host))
"""
def setup_db_main(app: FastAPI) -> None:
	db_client = MongoClient(settings.DB_URL)
	app.mongodb_client = db_client
	app.mongodb = db_client[settings.DB_NAME]
"""




