from pydantic import BaseModel


class Msg(BaseModel):
    msg: str


class MsgLogin(BaseModel):
    msg: str
    agent: str
    platform: list
