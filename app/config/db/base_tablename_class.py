import uuid
from typing import Any
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    @declared_attr
    def sid(cls):
        return Column(
            UUID(as_uuid=True), unique=True,
            nullable=False, primary_key=True, index=True,
            default=lambda: uuid.uuid4().hex)
