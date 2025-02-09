from fastapi import APIRouter, HTTPException, status, Depends
from src.database.requests import get_user, get_user_login, set_user, update_user, set_user_id
from datetime import timedelta
import hashlib
from dotenv import load_dotenv
from src.routers.sheme.UserModels import *
from src.routers.utils.jwt_utils import create_jwt_token, get_current_user

load_dotenv()
router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


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
    access_token = create_jwt_token(
        data={"login": login_data.login, "user_id": user["id"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user["id"]}

@router.get("/protected/")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "Access granted", "user": current_user}
