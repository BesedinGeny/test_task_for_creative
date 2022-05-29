import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.config.db.base_tablename_class import Base


class Company(Base):
    name = Column(String, nullable=False)
