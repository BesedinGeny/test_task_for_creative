import datetime
from typing import Any, Dict, Optional, Union

from app import models
from app.common.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

from sqlalchemy.orm import Session


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def create(self, db: Session, *, obj_in: UserCreate, with_commit: bool = True) -> User:
        db_obj = User(
            hashed_password=get_password_hash(obj_in.password),
            name=obj_in.name,
            last_name=obj_in.last_name,
            company_sid=obj_in.company_sid,
            group_sid=obj_in.group_sid,
            is_admin=obj_in.is_admin
        )

        db.add(db_obj)
        if with_commit:  # перед токенами, чтобы получить sid
            db.commit()
            db.refresh(db_obj)

        return db_obj

    def update(
            self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> UserUpdate:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *,
                     name: str, last_name: str, company: str,
                     password: str) -> Optional[User]:
        company_obj = db.query(models.Company).where(models.Company.name == company).first()
        user = db.query(User).where(
            User.name == name,
            User.last_name == last_name,
            User.company_sid == company_obj.sid
        ).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user



user = CRUDUser(User)
