from sqlalchemy import Boolean, Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.config.db.base_tablename_class import Base


class User(Base):
    """
    Table with User Data
    """
    __tablename__ = "user"

    name = Column(String, nullable=False, index=True, comment='имя')  # Имя
    middle_name = Column(String, nullable=True, comment='отчество')  # Отчество
    last_name = Column(String, nullable=False, index=True, comment='last name of user')  # Фамилия

    hashed_password = Column(String, nullable=False, comment='passwd')

    is_active = Column(Boolean(), default=True, comment='locked or unlocked')
    is_admin = Column(Boolean(), default=False)

    company_sid = Column(
        UUID(as_uuid=True),
        ForeignKey("company.sid"),
        index=True,
        nullable=False
    )

    group_sid = Column(
        UUID(as_uuid=True),
        ForeignKey("group.sid"),
        index=True,
        nullable=False
    )

    # relationships
    company = relationship("Company", foreign_keys=[company_sid], lazy='subquery')
    group = relationship("Group", back_populates="users", foreign_keys=[group_sid], lazy='subquery')

    def __repr__(self):
        return str(self.name) + " " + str(self.last_name)
