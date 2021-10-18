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


class UserSerialized(User):
    key: Optional[Any]
    createdAt: Optional[Any]
    updatedAt: Optional[Any]

    @validator('key')
    def serialize_key(cls, v):
        return v.hex

    @validator('createdAt')
    def serialize_ca(cls, v):
        return v.isoformat()

    @validator('updatedAt')
    def serialize_ua(cls, v):
        return v.isoformat()
