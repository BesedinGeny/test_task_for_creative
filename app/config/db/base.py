from .base_tablename_class import Base

from app.models import *


target_metadata = [User.metadata, Company.metadata, Group.metadata]
