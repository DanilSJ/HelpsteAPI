from pydantic import BaseModel


class RegisterModel(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int


class LoginModel(BaseModel):
    login: str
    password: str


class UpdateUserFieldsModel(BaseModel):
    subscribe: str | None = None
    model_using: str | None = None
    subscribe_time: str | None = None
    prefix: str | None = None
    voice_model: str | None = None
    admin: bool | None = None