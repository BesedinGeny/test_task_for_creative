from fastapi import Request, HTTPException
from starlette import status
from user_agents import parse

from app import models


def user_agent_parser(user_agent: str, request: Request):
    """
    Вспомогательная функция для получения устройства, ос пользователя и ip.
    :param user_agent: данные из user-agent
    :param request: данные из запроса
    """
    ip_address = request.scope.get('root_path')
    agent_from_user = f'{request.headers.get("Agent", "")}/ '
    platform_from_user = f'{request.headers.get("platform", "")}/ '
    user_agent_data = parse(user_agent)
    agent = (f'{agent_from_user}{user_agent_data.browser[0]}'
             f'{user_agent_data.browser[2]}')
    platform = (f'{platform_from_user}{user_agent_data.device[0]}',
                f' {user_agent_data.os[0]}{user_agent_data.os[2]}')
    return agent, platform, ip_address


def check_permission(user: models.User):
    if not user.is_admin:
        raise HTTPException(detail="Not enough rights",
                            status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
