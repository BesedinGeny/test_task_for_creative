import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi_pagination import add_pagination
from starlette.middleware.sessions import SessionMiddleware

from app.config.settigns import settings, cookies_settings

from app.routers.api import api_router
from app.routers.exceptions_handlers import authjwt_exception_handler


app = FastAPI(
    debug=True,
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    exception_handlers={AuthJWTException: authjwt_exception_handler},
)

origins = [

    "http://localhost",
    "http://0.0.0.0",

    "http://localhost:8080",
    "http://0.0.0.0:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@AuthJWT.load_config
def get_config():
    return cookies_settings


app.include_router(api_router, prefix=settings.API_V1_STR)
add_pagination(app)


def run():
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True, use_colors=True)


if __name__ == '__main__':
    run()
