from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserRegisterForm(BaseModel):
    company: str
    name: str
    middle_name: Optional[str]
    last_name: str
    password: str


class UserAddForm(BaseModel):
    name: str
    middle_name: Optional[str]
    last_name: str
    password: str
    group_sid: UUID


class LoginForm(BaseModel):
    name: str
    last_name: str
    company_name: str
    password: str

