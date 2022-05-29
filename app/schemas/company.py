from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str]


class Company(CompanyBase):
    sid: UUID
