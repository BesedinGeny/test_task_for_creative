from fastapi import APIRouter

from .v1.auth import auth
from .v1.users import users
from .v1.company import company

api_router = APIRouter()

api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(users.router, tags=["User"], prefix='/users')
api_router.include_router(company.router, tags=["Task"], prefix='/company')
