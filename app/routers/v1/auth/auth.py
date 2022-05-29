import json
from typing import Any

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
from app.common.services import user_agent_parser
from app.config.settigns import cookies_settings
from app.routers import deps

router = APIRouter()


@router.post('/login', response_model=schemas.MsgLogin)
async def login(
        request: Request,
        form_data: schemas.LoginForm,
        db: Session = Depends(deps.get_db),
        Authorize: AuthJWT = Depends(),
        user_agent: str = Header(None),
) -> Any:
    user = crud.user.authenticate(
        db, name=form_data.name, last_name=form_data.last_name,
        company=form_data.company_name, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Inactive user")

    payload = {'sid': str(user.sid)}

    access_token = Authorize.create_access_token(subject=json.dumps(payload))
    refresh_token = Authorize.create_refresh_token(subject=json.dumps(payload))

    agent, platform, _ = user_agent_parser(user_agent, request)
    res = {"msg": "Success Logins!", 'agent': agent, 'platform': platform}

    response = JSONResponse(res, status_code=status.HTTP_200_OK)

    Authorize.set_access_cookies(access_token, response,
                                 max_age=cookies_settings.auth_access_token_lifetime)
    Authorize.set_refresh_cookies(refresh_token, response,
                                  max_age=cookies_settings.auth_refresh_token_lifetime)

    return response


@router.post("/refresh_token", response_model=schemas.Msg)
async def update_access_token(
        Authorize: AuthJWT = Depends()
) -> Any:
    try:
        Authorize.jwt_refresh_token_required()
    except MissingTokenError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Refresh token not found")

    user_sid = Authorize.get_jwt_subject()

    updated_access_token = Authorize.create_access_token(subject=user_sid)
    updated_refresh_token = Authorize.create_refresh_token(subject=user_sid)

    response = JSONResponse({'msg': "Success tokens renewal"},
                            status_code=status.HTTP_200_OK)
    Authorize.set_access_cookies(updated_access_token, response,
                                 max_age=cookies_settings.auth_access_token_lifetime)
    Authorize.set_refresh_cookies(updated_refresh_token, response,
                                  max_age=cookies_settings.auth_refresh_token_lifetime)

    return response


@router.post("/logout", response_model=schemas.Msg)
def logout(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    res = JSONResponse({"msg": "Successfully logout"}, status_code=status.HTTP_200_OK)

    remove_cookie(Authorize, res, Authorize._access_cookie_key,
                  Authorize._access_cookie_path)
    remove_cookie(Authorize, res, Authorize._refresh_cookie_key,
                  Authorize._refresh_cookie_path)
    return res


@router.post("/reset_password", response_model=schemas.Msg)
async def reset_password(
        new_password: str = Body(..., embed=True),
        current_user: models.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)
) -> Any:
    """
    Reset Password from Personal Account (Use in Admin Panel Only - JWT required)
    """
    hashed_password = get_password_hash(new_password)
    current_user.hashed_password = hashed_password
    db.add(current_user)
    db.commit()

    return JSONResponse({"msg": "Password updated successfully"}, status_code=status.HTTP_200_OK)


def remove_cookie(jwt_service: AuthJWT, response: Response, cookie_key: str,
                  cookie_path: str, http_only: bool = True):
    """
    Additional function for token removal from cookie
    :param jwt_service: (library for cookies settings0
    :param response: response object, when we need to delete cookies
    :param cookie_key: cookie_key
    :param cookie_path: cookie_path
    :param http_only: httpOnly cookies flag
    :return:
    """
    response.set_cookie(cookie_key, '', max_age=0, path=cookie_path,
                        domain=jwt_service._cookie_domain,
                        secure=jwt_service._cookie_secure,
                        httponly=http_only,
                        samesite=jwt_service._cookie_samesite)
    return response
