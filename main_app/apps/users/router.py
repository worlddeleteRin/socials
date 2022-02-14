from fastapi import APIRouter, Depends, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4

from typing import Optional, List

from datetime import datetime, timedelta

from pymongo import ReturnDocument
from apps.users.authentication_provider import AuthenticationProvider

# import config (env variables)
from config import settings

from .models import *
# models 
from .user import *

from .password import get_password_hash

from .jwt import create_access_token

# user exceptions
from .user_exceptions import *

# user password hash and decode methods
from .password import get_password_hash

from apps.orders.orders import get_orders_by_user_id

from .user import get_current_admin_user, get_user_by_id, create_user, check_user_delivery_address

from database.main_db import db_provider

# https://fastapi.tiangolo.com/tutorial/bigger-applications/

router = APIRouter(
    prefix = "/users",
    tags = ["users"],
    # responses ? 
)

authenticationProvider = AuthenticationProvider()

@router.post("/login")
async def login_user(
    login_info: BaseUserLoginInfo,
):
    success = True
    otp_code = None
    username = format_validate_username(login_info.username)
    user: BaseUserDB | None = get_user_by_username(
        username = username
    )
    print('user is', user)
    if not user:
        if login_info.authentication_type == AuthenticationTypeEnum.password:
            raise UserNotExist 
        user = create_user(
            username = login_info.username
        )
    if login_info.authentication_type == AuthenticationTypeEnum.password:
        pass
    elif login_info.authentication_type == AuthenticationTypeEnum.call_otp:
        success,otp_code = authenticationProvider.send_call_otp(
            phone=user.username,
            is_testing=login_info.is_testing,
        )
    elif login_info.authentication_type == AuthenticationTypeEnum.sms_otp:
        pass
    if (success 
        and otp_code 
        and otp_code.__len__() == 4
        #and (not login_info.is_testing)
        ):
        user.otp = otp_code
        user.update_db()

    return {
        "success": success,
        "is_testing": login_info.is_testing,
        "otp_code": otp_code,
        "login_info": login_info.dict(),
        # "user": user.dict(),
    }

@router.post("/token")
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(default=None),
    otp: str = Form(default=None),
    auth_type: AuthenticationTypeEnum  = Form(...)
    # form_data: OAuth2PasswordRequestForm = Depends()
):
    print('get token request')
    is_authenticated: bool = False
    user: BaseUserDB = get_user(username=username)
    if auth_type == AuthenticationTypeEnum.password:
        is_authenticated = authenticate_user_password(
            user = user,
            password = password,
        )
    elif auth_type == AuthenticationTypeEnum.call_otp:
        is_authenticated = authenticate_user_call_otp(
            user = user,
            otp = otp,
        )
    # check if user successfully authenticated
    if not is_authenticated:
        raise IncorrectUserCredentials 
    # generate access_token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data = {"sub": user.username}, expires_delta=access_token_expires,
        JWT_SECRET_KEY = settings.JWT_SECRET_KEY, JWT_ALGORITHM = settings.JWT_ALGORITHM
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post('/exist-verified')
async def check_exist_verified_user(
    user_info: BaseUserExistVerified,
    ):
    """
        Check if user with passed `username` is verified,
        return verified bool status in `exist_verified` key
    """
    exist_verified = False
    print('user info is', user_info)
    user = db_provider.users_db.find_one({"username": user_info.username})
    if user and user["is_verified"]:
        exist_verified = True
    return {
        "status": "success",
        "exist_verified": exist_verified,
    }

@router.get("/me")
async def read_users_me(
    current_user: BaseUserDB = Depends(get_current_active_user)
    ):
    return current_user.dict(exclude={"hashed_password"})



@router.post("/register")
async def register_user(
    user_info: BaseUserCreate,
    user_to_register: BaseUserDB = Depends(get_user_register),
    ):
    """
        Register user
    """
    print('run register method')
    # need to send verification sms code, and, save it to user database field
    is_success, code = authenticationProvider.send_call_otp(
        phone = user_to_register.username
    )
    if not is_success:
        # raise exception, that otp code is not send
        print("не удалось отправить код подтверждения")
        raise NotSendVerificationCode
    # save otp code to user model
    # code = 1234
    user_to_register.otp = str(code)
    # db logic to insert user
    db_provider.users_db.insert_one(user_to_register.dict(by_alias=True))
    # eof db logic to insert user
    return {
        "status": "success",
        "otp": code,
    }

@router.post("/restore")
async def restore_user(
    user_info: BaseUserRestore,
    user_to_restore: BaseUserDB = Depends(get_user_restore),
    ):
    """
        params: username
        Restore account route.
        ----------------------
        Exceptions:
        - Account not exist
    """

    # need to send verification sms code, and, save it to user database field
    is_success, code = authenticationProvider.send_call_otp(
        phone = user_to_restore.username
    )
    if not is_success:
        print('не удалось отправить код подтверждения')
        raise NotSendVerificationCode
    # save otp code to user model
    user_to_restore.otp = code  
    # db logic to insert user
    db_provider.users_db.update_one(
        {"_id": user_to_restore.id},
        {"$set": user_to_restore.dict(by_alias=True)}
    )
    # eof db logic to insert user
    return {
        "status": "success",
        "otp": 123,
    }

@router.post("/register-verify")
async def verify_register_user(
    user_info: BaseUserVerify,
    verified_user: BaseUser = Depends(get_user_verify)
    ):
    """
        Get user username, password, otp code.
        If user already active and verified - throw exception
        If user not exist in db - throw exception
        If passed otp code not match with user_db.otp - throw exception
        Set is_active = True and is_verified = True, if otp match, update user in db
        return verified_user, that already modified in db.
    """

    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data = {"sub": verified_user.username}, expires_delta=access_token_expires,
        JWT_SECRET_KEY = settings.JWT_SECRET_KEY, JWT_ALGORITHM = settings.JWT_ALGORITHM
    )
    return {
        "user": verified_user,
        "access_token": access_token,
    }

@router.post("/restore-verify")
async def verify_restore_user(
    user_info: BaseUserRestoreVerify,
    verified_user: BaseUser = Depends(get_user_restore_verify)
    ):
    """
        params: username, otp (sms code)
        Get user username, otp code.
        -------------
        Exceptions:
        - User not exist
        - Passed otp code dont match
        -------------
        - set user otp code to None if validate verified_user success
        - generate access_token and return it
    """

    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data = {"sub": verified_user.username}, expires_delta=access_token_expires,
        JWT_SECRET_KEY = settings.JWT_SECRET_KEY, JWT_ALGORITHM = settings.JWT_ALGORITHM
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.patch("/update-password")
async def update_user_password(
    update_user_info: BaseUserUpdatePassword,
    current_user: BaseUser = Depends(get_current_active_user),
    ):
    new_password = get_password_hash(update_user_info.password)
    # update user in db
    updated_user = db_provider.users_db.find_one_and_update({"_id": current_user.id}, {
        "$set": {
            "hashed_password": new_password,
        }
    })
    # check if updated info 'updatedExisting' = true ? 
    return updated_user
# update user info route
@router.patch("/me")
async def update_user(
    update_user_info: BaseUserUpdate,
    current_user: BaseUser = Depends(get_current_active_user),
    ):
    update_data = update_user_info.dict(exclude_unset = True, by_alias=True)
    # update user in db
    updated_user = db_provider.users_db.find_one_and_update({"_id": current_user.id}, {
        "$set": update_data,
    }, return_document=ReturnDocument.AFTER)
    # check if updated info 'updatedExisting' = true ? 
    return BaseUser(**updated_user).dict()

@router.get("/me/delivery-address")
async def user_delivery_addresses(
        request: Request,
        current_user: BaseUserDB = Depends(get_current_active_user)
    ):
    addresses = get_user_delivery_addresses(current_user.id)
    return addresses


@router.post("/me/delivery-address")
async def create_user_delivery_address(
    address: CreateUserDeliveryAddress,
    current_user: BaseUserDB = Depends(get_current_active_user)
    ):
    new_address = UserDeliveryAddress(
        **address.dict(),
        user_id = current_user.id
    )
    is_valid = check_user_delivery_address(
        address = new_address
    )
    if not is_valid:
        raise InvalidDeliveryAddress
    db_provider.users_addresses_db.insert_one(
        new_address.dict(by_alias=True)
    )
    print('added new address')
    return get_user_delivery_addresses(current_user.id)

@router.patch("/me/delivery-address/{address_id}")
async def update_user_delivery_address(
    new_address: CreateUserDeliveryAddress,
    address_id: UUID4,
    current_user: BaseUserDB = Depends(get_current_active_user)
):
    address: UserDeliveryAddress | None = UserDeliveryAddress.find_by_id(address_id)
    if not address:
        raise UserDeliveryAddressNotExist
    address_update = address.copy(update=new_address.dict())
    address_update.update_db()
    return address_update.dict()

@router.delete("/me/delivery-address/{address_id}")
async def delete_user_delivery_address(
    address_id: UUID4,
    current_user: BaseUserDB = Depends(get_current_active_user),
    ):
    db_provider.users_addresses_db.delete_one(
        {"_id": address_id}
    )
    return get_user_delivery_addresses(current_user.id)

@router.get("/me/orders/")
async def user_orders(
    current_user: BaseUserDB = Depends(get_current_active_user),
):
    user_orders = get_orders_by_user_id(current_user.id)
    return {
        "orders": user_orders,
    }

# admin specific section
@router.get("/auth-admin")
async def auth_admin(
    current_admin_user: BaseUserDB = Depends(get_current_admin_user)
):
    return current_admin_user.dict(exclude={"hashed_password"})

# search user by username
@router.get("/search")
async def search_users(
    search: str
):
    if not search:
        return []
    users = search_users_by_username(search)
    return users

# admin get user delivery addresses
@router.get("/{user_id}/delivery-addresses")
async def admin_get_user_delivery_addresses(
        user_id: UUID4,
        admin_user = Depends(get_current_admin_user),
    ):
    addresses = get_user_delivery_addresses(user_id)
    return addresses

@router.post("/{user_id}/delivery-address")
async def admin_create_user_delivery_address(
    user_id: UUID4,
    new_address: CreateUserDeliveryAddress,
    admin_user = Depends(get_current_admin_user)
    ):
    # TODO: need to implement
    current_user = get_user_by_id(user_id)
    if not current_user:
        return None
    new_address.user_id = current_user.id
    db_provider.users_addresses_db.insert_one(
        new_address.dict(by_alias=True)
    )
    delivery_addresses = db_provider.users_addresses_db.find(
        {"user_id": current_user.id}
    )
    addresses = [UserDeliveryAddress(**address).dict() for address in delivery_addresses]
    return addresses

