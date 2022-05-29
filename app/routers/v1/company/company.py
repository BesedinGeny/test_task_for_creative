import json
from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import MissingTokenError
from sqlalchemy.orm import Session
from starlette import status

from app import crud as crud
from app import models
from app import schemas
from app.common.security import get_password_hash
from app.common.services import user_agent_parser, check_permission
from app.config.settigns import cookies_settings
from app.routers import deps

router = APIRouter()


@router.post('/register', response_model=schemas.User)
async def register_user_with_new_company(
        user_form: schemas.UserRegisterForm,
        db: Session = Depends(deps.get_db),
):
    company = crud.company.get_by_name(db, user_form.company)
    if company:
        raise HTTPException(detail="Company is already exist",
                            status_code=status.HTTP_400_BAD_REQUEST)

    company: models.Company = crud.company.create(
        db,
        obj_in=schemas.CompanyCreate(name=user_form.company)
    )

    group_in = schemas.GroupCreate(name="Все пользователи", company_sid=company.sid)
    group: models.Group = crud.group.create(db, obj_in=group_in)

    user_data = user_form.dict()
    user_data['company_sid'] = company.sid
    user_data['group_sid'] = group.sid
    user_data['is_admin'] = True

    user_in = schemas.UserCreate(**user_data)
    user = crud.user.create(db, obj_in=user_in)

    return user


@router.post("/user", response_model=schemas.User)
def add_user_to_existing_company(
        user_form: schemas.UserAddForm,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    group = crud.group.get(db, sid=user_form.group_sid)
    if not group:
        raise HTTPException(detail="Group doesnt found",
                            status_code=status.HTTP_404_NOT_FOUND)

    if group.company_sid != current_user.company_sid:
        raise HTTPException(detail="Group not in admin`s company",
                            status_code=status.HTTP_400_BAD_REQUEST)

    user_data = user_form.dict()
    user_data['company_sid'] = current_user.company_sid

    return crud.user.create(db, obj_in=schemas.UserCreate(**user_data))


@router.get("/user", response_model=List[schemas.User])
def get_users_by_last_name(
        last_name: str,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    users = db.query(models.User).where(
        models.User.last_name == last_name,
        models.User.company_sid == current_user.company_sid
    ).all()
    return users


@router.post("/group", response_model=schemas.Group)
def add_group_to_company(
        group_in: schemas.GroupCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    if group_in.company_sid != current_user.company_sid:
        raise HTTPException(detail="Group not in admin`s company",
                            status_code=status.HTTP_400_BAD_REQUEST)

    parent_group = crud.group.get(db, sid=group_in.group_sid)
    if not parent_group or parent_group.company_sid != current_user.company_sid:
        raise HTTPException(detail="Wrong parent group sid",
                            status_code=status.HTTP_400_BAD_REQUEST)

    return crud.group.create(db, obj_in=group_in)


@router.get("/group", response_model=schemas.Group)
def get_groups_by_name(
        name: str,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    groups = db.query(models.Group).where(
        models.Group.name == name,
        models.Group.company_sid == current_user.company_sid
    ).all()

    return groups


def dfs(all_nodes: List, root: models.Group, answer: List) -> None:
    """Обход в глубину, результат работы в переменной answer"""
    answer.append(str(root))
    sub_groups = list(filter(lambda group: group.group_sid == root.sid, all_nodes))
    for user in root.users:
        answer.append(str(user))

    for sub_group in sub_groups:
        dfs(all_nodes, sub_group, answer)


@router.get("/catalogue")
def get_branch_of_company(
        name: str,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    """Вывод плоского листа названий групп и людей """
    # note: В тз не указано, что делать, если есть группы с одинаковым наименованием
    # поэтому беру любую (первую)

    # note2: К сожалению, в тз не указан метод обхода или пример, когда у группы
    # несколько подгрупп. Выбран вариант обходы в глубину.
    groups_in_company = db.query(models.Group).where(
        models.Group.company_sid == current_user.company_sid
    ).all()
    root_element = list(filter(lambda group: group.name == name, groups_in_company))
    if not root_element:
        raise HTTPException(detail="Wrong group name",
                            status_code=status.HTTP_400_BAD_REQUEST)

    root_element = root_element[0]
    response_list = []

    dfs(groups_in_company, root_element, response_list)
    return response_list

