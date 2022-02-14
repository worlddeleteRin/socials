from fastapi import FastAPI 
import uuid
from pymongo import ReturnDocument
from enum import Enum

from typing import Optional, List

from pydantic import UUID4, BaseModel, Field, validator
from datetime import datetime, date

from apps.products.models import BaseProduct
from apps.products.products import get_product_by_id

from .order_exceptions import OrderNotExist

# import line items from cart app
from apps.cart.models import BaseCart, LineItem, LineItemUpdate
# import UserDeliveryAddress from users app
from apps.users.models import UserDeliveryAddress, RecipientTypeEnum, RecipientPerson
from apps.users.user import get_user_by_id

from apps.payments.models import PaymentMethod, PaymentMethodEnum
from apps.delivery.models import DeliveryMethod, DeliveryMethodEnum
from apps.site.models import ColorARGB, PickupAddress
from apps.site.utils import get_time_now

from database.main_db import db_provider


class OrderStatus(BaseModel):
    id: str
    name: str
    name_display: str
    color: ColorARGB = ColorARGB()

class OrderStatusColors():
    awaiting_confirmation = ColorARGB(
        a=255,r=252,g=44,b=3
    )

awaiting_confirmation = OrderStatus(
    id = "awaiting_confirmation",
    name = "На подтверждении",
    name_display = "На подтверждении",
    color = OrderStatusColors.awaiting_confirmation,
)
awaiting_cooking = OrderStatus(
    id = "awaiting_cooking",
    name = "Заказ готовится",
    name_display = "Заказ готовится",
    color = OrderStatusColors.awaiting_confirmation,
)
awaiting_payment = OrderStatus(
    id = "awaiting_payment",
    name = "Ожидание оплаты",
    name_display = "Ожидание оплаты",
)
awaiting_shipment = OrderStatus(
    id = "awaiting_shipment",
    name = "Ожидание доставки",
    name_display = "Ожидание доставки",
)
in_progress = OrderStatus(
    id = "in_progress",
    name = "В процессе",
    name_display = "В процессе",
)
completed = OrderStatus(
    id = "completed",
    name = "Завершен",
    name_display = "Завершен",
    color = OrderStatusColors.awaiting_confirmation,
)
cancelled = OrderStatus(
    id = "cancelled",
    name = "Отменен",
    name_display = "Отменен",
    color = OrderStatusColors.awaiting_confirmation,
)

order_statuses = {
    "awaiting_confirmation": awaiting_confirmation,
    "awaiting_cooking": awaiting_cooking,
    "awaiting_payment": awaiting_payment,
    "awaiting_shipment": awaiting_shipment,
    "in_progress": in_progress,
    "completed": completed,
    "cancelled": cancelled,
}

class OrderStatusEnum(str, Enum):
    awaiting_confirmation = "awaiting_confirmation"
    awaiting_cooking = "awaiting_cooking"
    awaiting_payment = "awaiting_payment"
    awaiting_shipment = "awaiting_shipment"
    in_progress = "in_progress"
    incomplete = "incomplete"
    completed = "completed"
    cancelled = "cancelled"

class BaseOrderCreate(BaseModel):
    line_items: Optional[List[LineItem]] = []
    customer_id: Optional[UUID4] = None
    customer_ip_address: Optional[str] = None
    # associated session_id
    customer_session_id: Optional[UUID4] = None
    # associated cart_id
    cart_id: Optional[UUID4] = None
    # payment method id 
    payment_method: PaymentMethodEnum
    # delivery_method id
    delivery_method: DeliveryMethodEnum
    # user_delivery_address id, if delivery method is 'delivery'
    delivery_address: Optional[UUID4] = None
    # guest delivery address
    guest_delivery_address: Optional[str] = None
    # guest phone number
    guest_phone_number: Optional[str] = None
    # pickup_address id, if delivery_method is 'pickup'
    pickup_address: Optional[UUID4] = None
    # custom customer message, provided for order
    custom_message: str = ""
    postcard_text: str = ""
    recipient_type: RecipientTypeEnum = RecipientTypeEnum.user
    recipient_person: Optional[RecipientPerson] = None
    # delivery datetime
    delivery_datetime: Optional[datetime] = Field(default_factory=None, default=None)

class BaseOrderUpdate(BaseModel):
    status_id: OrderStatusEnum
    status: Optional[OrderStatus] = None

    def set_status(self):
        self.status = order_statuses[self.status_id]

class BaseOrder(BaseModel):
    """ Base Order Model """

    id: UUID4 = Field(default_factory=uuid.uuid4, alias="_id")
    # id of cart, that was converted to order
    cart_id: Optional[UUID4] = None
    # attached cart to order
    cart: BaseCart
    # id of the customer, that makes order, or, that is assigned to the order by admin
    customer_id: Optional[UUID4] = None
    # customer username
    customer_username: Optional[str] = None
    customer_ip_address: Optional[str] = None

    status: OrderStatus = order_statuses["awaiting_confirmation"]
    #   status: OrderStatusEnum = OrderStatusEnum.awaiting_confirmation

    # dates data
    date_created: datetime = Field(default_factory=get_time_now)
    date_modified: datetime = Field(default_factory=get_time_now)
    # delivery_datetime: Optional[datetime] = None
    delivery_datetime: Optional[datetime] = Field(default_factory=None, default=None)
    # payment method id 
    payment_method: PaymentMethod
    # delivery_method id
    delivery_method: DeliveryMethod

    # user_delivery_address object, if delivery method is 'delivery'
    delivery_address: Optional[UserDeliveryAddress] = None
    # guest delivery adderss
    guest_delivery_address: Optional[str] = None
    # guest phone number
    guest_phone_number: Optional[str] = None
    # pickup_address id, if delivery_method is 'pickup'
    pickup_address: Optional[PickupAddress] = None
    # custom customer message, provided for order
    custom_message: str = "" 
    # postcard text
    postcard_text: str = ""
    recipient_type: RecipientTypeEnum = RecipientTypeEnum.user
    recipient_person: Optional[RecipientPerson] = None
    
    def check_can_edit(self):
        can_not_edit_statusses = ['completed', 'cancelled']
        if self.status.id in can_not_edit_statusses:
            return False
        return True

    def check_set_user(self):
        if not self.customer_id:
            return
        user = get_user_by_id(self.customer_id)
        if not user:
            return
        self.customer_username = user.username

    def save_db(self):
        db_provider.orders_db.insert_one(
            self.dict(by_alias=True)
        )
    def delete_db(self):
        db_provider.orders_db.delete_one(
            {"_id": self.id}
        )
    def update_db(self):
        # maybe need improvement to recast object with updated_order return info
        updated_order_dict = db_provider.orders_db.find_one_and_update(
            {"_id": self.id},
            {"$set": self.dict(by_alias=True)},
            return_document=ReturnDocument.AFTER
        )
        updated_order = BaseOrder(**updated_order_dict)
        return updated_order

    def set_modified(self):
        self.date_modified = datetime.utcnow()

