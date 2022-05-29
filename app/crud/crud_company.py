from app.crud.base import CRUDBase
from app.models import Company
from app.schemas import CompanyCreate, CompanyUpdate

from sqlalchemy.orm import Session


class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyUpdate]):
    @staticmethod
    def get_by_name(db: Session, name: str):
        return db.query(Company).where(Company.name == name).first()


company = CRUDCompany(Company)
