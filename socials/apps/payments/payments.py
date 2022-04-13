from fastapi import Depends, Request
from .models import PaymentMethod
from .payment_exceptions import PaymentMethodNotExist
import uuid
from socials.config import settings

from socials.database.main_db import db_provider


def get_payment_methods() -> list:
	payment_methods_dict = db_provider.payment_methods_db.find({})
	if not payment_methods_dict:
		return []
	payment_methods = [PaymentMethod(**p_method).dict() for p_method in payment_methods_dict]
	return payment_methods

def get_payment_method_by_id(payment_method_id) -> PaymentMethod:
	payment_method = None
	payment_method = db_provider.payment_methods_db.find_one(
		{"_id": payment_method_id}
	)
	if not payment_method:
		raise PaymentMethodNotExist
	payment_method = PaymentMethod(**payment_method)
	return payment_method
