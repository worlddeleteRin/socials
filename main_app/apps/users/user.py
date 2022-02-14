from fastapi import Depends, Request, FastAPI
from pydantic import UUID4
from jose import JWTError, jwt
from starlette.exceptions import HTTPException

from .models import *
from config import settings
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .jwt import decode_token, create_access_token

from .password import verify_password, get_password_hash

from .user_exceptions import InvalidAuthenticationCredentials, IncorrectVerificationCode, InactiveUser, UserAlreadyExist, UserNotExist, UserDeliveryAddressNotExist, UserNotAdmin, UsernameNotValid

from database.main_db import db_provider


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token", auto_error = False)


def create_user(
    username: str,
    password: str = "",
) -> BaseUserDB:
    hashed_password = ""
    password = password.strip()
    if password.__len__() > 6:
        hashed_password = get_password_hash(password)
    username = format_validate_username(username)
    new_user = BaseUserDB(
        username = username,
        hashed_password = hashed_password,
    )
    db_provider.users_db.insert_one(new_user.dict(by_alias=True))
    user: BaseUserDB = BaseUserDB(**new_user.dict())
    return user

def format_validate_username(
    username: str 
) -> str:
    username = username.replace(" ", "")
    if len(username) != 11: 
        raise UsernameNotValid
    return username

def get_user_by_username(
    username: str
) -> BaseUserDB | None:
    userRaw = db_provider.users_db.find_one(
        {"username": username}
    )
    if not userRaw:
        return None
    user = BaseUserDB(**userRaw)
    return user

def authenticate_user_password(
user: BaseUserDB, 
password: str) -> bool:
    """
        Authenticate user by username and password
    """
    if not verify_password(password, user.hashed_password):
        return False
    return True

def authenticate_user_call_otp(
user: BaseUserDB, 
otp: str) -> bool:
    """
        Authenticate user by username and call otp code 
    """
    if (not user.otp or 
        not user.otp.__len__() == 4 or
        not user.otp == otp
        ):
        return False
    user.otp = ""
    user.is_verified = True
    user.is_active = True
    user.update_db()
    return True

def get_user(username: str) -> BaseUserDB:
    print('run get user')
    user_dict = db_provider.users_db.find_one({"username": username})
    #print('user dict is', user_dict)
    if not user_dict:
        raise UserNotExist
    return BaseUserDB(**user_dict)


def get_user_by_id(
    user_id: UUID4, 
    silent: bool = False,
    ):
    user_dict = db_provider.users_db.find_one(
        {"_id": user_id}
    )
    if not user_dict:
        if silent:
            return None
        raise
    return BaseUser(**user_dict)

async def get_current_user_silent(token: str = Depends(oauth2_scheme)):
    print('get current user silent, token is', token)
    try:
        payload = decode_token(token, settings.JWT_SECRET_KEY, [settings.JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
        #    raise InvalidAuthenticationCredentials
        token_data = TokenData(username = username)
    except JWTError:
        return None
        # raise InvalidAuthenticationCredentials
    except Exception as e:
        return None
    if not token_data.username:
        return None
        # raise InvalidAuthenticationCredentials
    user = get_user(username = token_data.username)
    if user is None:
        return None
        # raise InvalidAuthenticationCredentials
    return user

def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = decode_token(token, settings.JWT_SECRET_KEY, [settings.JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise InvalidAuthenticationCredentials
        token_data = TokenData(username = username)
    except JWTError:
        raise InvalidAuthenticationCredentials
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Authentication error"
        )
    if not token_data.username:
        raise InvalidAuthenticationCredentials
    user = get_user(username = token_data.username)
    if user is None:
        raise InvalidAuthenticationCredentials
    return user


def get_current_active_user(current_user: BaseUser = Depends(get_current_user)):
    if not current_user.is_active:
        raise InactiveUser
    return current_user

def get_current_admin_user(current_user: BaseUser = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise UserNotAdmin
    return current_user


def get_user_register(user_info: BaseUserCreate):
    user = db_provider.users_db.find_one({"username": user_info.username})
    # if user exist and verified, we raise exist exception
    if user:
        user = BaseUser(**user)
        if user.is_verified:
            raise UserAlreadyExist
        # if user exist, but not verified - we delete it,
        # to recreate in future
        else:
            #print('found user when register, but it is not verified, so, delete it')
            db_provider.users_db.delete_one({"_id": user.id})

    hashed_password = get_password_hash(user_info.password)
    user_to_register = BaseUserDB(**user_info.dict(), hashed_password = hashed_password)
    return user_to_register

def get_user_restore(user_info: BaseUserRestore) -> BaseUserDB:
    #user_info = user_info.dict()
    user = db_provider.users_db.find_one({"username": user_info.username})
    # if user not exist we raise not exist exception
    if not user:
        raise UserNotExist

    user_to_verify = BaseUserDB(**user)
    return user_to_verify

def get_user_verify(user_info: BaseUserVerify):
    #user_info = user_info.dict()
    user = db_provider.users_db.find_one({"username": user_info.username})
    if not user:
        raise UserNotExist
    user = BaseUserDB(**user)
    if not user_info.otp == user.otp:
        raise IncorrectVerificationCode
    # set user to verified
    user.is_verified = True
    user.is_active = True
    user.otp = None
    db_provider.users_db.update_one({"_id": user.id}, {"$set": user.dict(by_alias=True)})

    return BaseUser(**user.dict())
#   if user.is_verified:
#       raise UserAlreadyVerified
def get_user_restore_verify(user_info: BaseUserRestoreVerify) -> BaseUser:
    user = db_provider.users_db.find_one({"username": user_info.username})
    if not user:
        raise UserNotExist
    user = BaseUserDB(**user)
    if not user_info.otp == user.otp:
        raise IncorrectVerificationCode
    # set user otp code to None 
    user.otp = None
    db_provider.users_db.update_one({"_id": user.id}, {"$set": user.dict(by_alias=True)})
    return BaseUser(**user.dict())

def get_user_delivery_addresses(user_id: UUID4):
    addresses_dict = db_provider.users_addresses_db.find(
        {"user_id": user_id}
    )
    addresses = [UserDeliveryAddress(**address).dict() for address in addresses_dict]
    return addresses

def get_user_delivery_address_by_id(delivery_address_id) -> UserDeliveryAddress:
    address_dict = db_provider.users_addresses_db.find_one(
        { "_id": delivery_address_id }
    )
    if not address_dict:
        raise UserDeliveryAddressNotExist
    address = UserDeliveryAddress(**address_dict)
    return address

# search users by username
def search_users_by_username(search_string: str):
    users_dict = db_provider.users_db.find(
        {
            "username": {
                "$regex": search_string
            }
        }
    ).limit(10)
    users = [BaseUser(**user).dict() for user in users_dict]
    return users

def check_user_delivery_address(
    address: UserDeliveryAddress
):
    if address.recipient_type == RecipientTypeEnum.other_person:
        if not address.recipient_person:
            return False
    return True

