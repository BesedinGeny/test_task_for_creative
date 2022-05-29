from app.crud.base import CRUDBase
from app.models import Group
from app.schemas import GroupCreate, GroupUpdate


class CRUDGroup(CRUDBase[Group, GroupCreate, GroupUpdate]):
    pass


group = CRUDGroup(Group)
