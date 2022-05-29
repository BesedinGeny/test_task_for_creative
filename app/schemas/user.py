import string
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, BaseModel
from app.schemas.company import Company
from app.schemas.group import Group


class UserBase(BaseModel):
    name: str
    middle_name: Optional[str] = None
    last_name: str

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    company_sid: UUID
    group_sid: UUID
    is_admin: bool = False


class UserUpdate(UserBase):
    password: str


class UserProfileUpdate(UserBase):
    name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class UserInDBBase(UserBase):
    sid: UUID

    company_sid = UUID
    group_sid = UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    company: Company
    group: Group


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


# class Tokens(BaseModel):
#     service: str
#     access_token: str
#     refresh_token: Optional[str]
