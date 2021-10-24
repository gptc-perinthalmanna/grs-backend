import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, HttpUrl, validator, EmailStr, UUID4
from enum import Enum
import re


class Token(BaseModel):
    access_token: str
    token_type: str


class Gender(str, Enum):
    male = 'male'
    female = 'female'


class Designation(str, Enum):
    tradesman = 'tradesman'
    tradeInstructor = 'tradeInstructor'
    demonstrator = 'demonstrator'
    workshopInstructor = 'workshopInstructor'
    workshopSuperintendent = 'workshopSuperintendent'
    lecturer = 'lecturer'
    headOfDepartment = 'headOfDepartment'
    principal = 'principal'
    student = 'student'
    officeStaff = 'officeStaff'


class AccountType(str, Enum):
    student = 'student'
    staff = 'staff'
    parent = 'parent'
    other = 'other'

class BasicUser(BaseModel):
    key: UUID4
    username: str
    first_name: str
    last_name: str
    avatar: Optional[HttpUrl] = None
    designation: Optional[Designation] = None
    type: AccountType
    gender: Optional[Gender]

class User(BaseModel):
    key: UUID4
    username: str
    email: EmailStr
    disabled: Optional[bool] = False
    first_name: str
    last_name: str
    contact_number: int
    type: AccountType
    address: Optional[str] = None
    state: Optional[str] = 'Kerala'
    pin: Optional[int] = None
    gender: Optional[Gender] = 'male'
    avatar: Optional[HttpUrl] = None
    designation: Optional[Designation] = None
    createdAt: Optional[datetime.datetime] = None
    updatedAt: Optional[datetime.datetime] = None

    @validator('designation')
    def check_user_is_staff(cls, v, values, **kwargs):
        if values['type'] != 'staff':
            if v is not None:
                raise ValueError('Cannot Select Designation if you are not Staff of the college.')
        return v

    @validator('contact_number')
    def validate_mobile_number(cls, v):
        pattern = re.compile('^[6-9]\d{9}$')
        assert pattern.match(str(v)), 'Contact Number is Invalid'
        return v

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v


class UserInDB(User):
    hashed_password: str


class UserCreate(User):
    key: Optional[UUID4]
    password: str
    repeat_password: Optional[str]

    @validator('repeat_password')
    def password_match(cls, v, values, **kwargs):
        if 'password' in values and values['password'] == v:
            return v
        raise ValueError('Passwords doesnot match')


class UserEdit(User):
    username: str
    password: str


class ChangePassword(BaseModel):
    username: str
    password: str
    new_password: str
    repeat_password: str


class UserSerialized(UserInDB):
    key: Optional[Any]
    createdAt: Optional[Any]
    updatedAt: Optional[Any]
    hashed_password: Optional[str]

    @validator('key')
    def serialize_uuid(cls, v):
        if type(v) == str:
            return v
        return v.hex

    @validator('createdAt', 'updatedAt')
    def serialize_date(cls, v):
        return v.isoformat()

