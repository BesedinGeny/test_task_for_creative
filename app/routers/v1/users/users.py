from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud as crud
from app import models, schemas
from app.routers import deps

router = APIRouter()


@router.put("/me", response_model=schemas.UserProfileUpdate)
async def update_user_me(
        *,
        db: Session = Depends(deps.get_db),
        name: str = Body(None),
        lastname: str = Body(None),
        email: EmailStr = Body(None),
        phone: str = Body(None),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update personal profile
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserProfileUpdate(**current_user_data)

    if name is not None:
        user_in.name = name
    if lastname is not None:
        user_in.lastname = lastname
    if email is not None:
        user_in.email = email
    if phone is not None:
        user_in.phone = phone
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me")
async def get_user_me(
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get current user info.
    """
    return current_user
