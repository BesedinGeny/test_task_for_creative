from uuid import UUID

from pydantic import BaseModel
from typing import Optional


class GroupBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class GroupCreate(GroupBase):
    company_sid: UUID
    group_sid: Optional[UUID]


class GroupUpdate(BaseModel):
    name: Optional[str]


class Group(GroupCreate):
    sid: UUID
