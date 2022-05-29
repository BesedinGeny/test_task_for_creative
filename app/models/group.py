from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.config.db.base_tablename_class import Base


class Group(Base):
    name = Column(String, nullable=True)

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
        nullable=True
    )

    # relationships
    company = relationship("Company", foreign_keys=[company_sid], lazy='subquery')
    parent_group = relationship("Group", foreign_keys=[group_sid], lazy='select')
    users = relationship("User", back_populates="group", uselist=True)

    def __repr__(self):
        return str(self.name)
