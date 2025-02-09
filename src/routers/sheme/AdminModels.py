from pydantic import BaseModel


class AdminModel(BaseModel):
    login: str
    password: str