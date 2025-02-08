import os
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from src.database.requests import get_user, get_user_login, set_user, update_user, set_user_id
from jose import jwt
from datetime import datetime, timedelta
import hashlib
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY_USER")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

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

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Проверяем, передан ли сам SECRET_KEY вместо токена
        if token == SECRET_KEY:
            return {"login": 'dw', "user_id": 1}  # Можно задать фиктивные данные

        # Декодируем JWT-токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Проверяем срок действия токена
        expire = payload.get("exp")
        if expire and datetime.utcnow() > datetime.utcfromtimestamp(expire):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWT токен истёк. Авторизуйтесь заново.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Получаем данные пользователя
        user = payload.get("login")
        user_id = payload.get("user_id")
        if user is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Некорректный токен",
            )

        return {"login": user, "user_id": user_id}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT токен истёк. Авторизуйтесь заново.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка при обработке токена",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("_telegram/{telegram_id}")
async def add_user(telegram_id: int):
    user_created = await set_user(telegram_id)
    if user_created:
        return {"message": "User created successfully"}
    return {"message": "User already exists"}

@router.post("_sait/")
async def add_user_id(request: RegisterModel):
    try:
        user_created = await set_user_id(request.login, request.password)
        if user_created:
            return {"message": "User created successfully"}
        return {"message": "User already exists"}
    except HTTPException as e:
        raise e

@router.get("/{identifier}")
async def fetch_user(identifier: str):
    user = await get_user(identifier)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}")
async def update_user_id(user_id: int, fields: UpdateUserFieldsModel, current_user: dict = Depends(get_current_user)):
    print(current_user)
    updated = await update_user(
        user_id=user_id,
        subscribe=fields.subscribe,
        model_using=fields.model_using,
        subscribe_time=fields.subscribe_time,
        prefix=fields.prefix,
        voice_model=fields.voice_model,
        admin=fields.admin
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User fields updated successfully"}

@router.post("/auth/", response_model=Token)
async def login_for_access_token(login_data: LoginModel):
    user = await get_user_login(login_data.login)
 
    if not user or user["password"] != hashlib.sha256(login_data.password.encode()).hexdigest():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"login": login_data.login, "user_id": user["id"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user["id"]}

@router.get("/protected/")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "Access granted", "user": current_user}
