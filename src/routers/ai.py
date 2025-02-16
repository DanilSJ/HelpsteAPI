from fastapi import APIRouter, HTTPException, Header, Depends
from src.plugin.ai import ChatGPT, Dalle
from src.routers.sheme.AiModels import *
from src.routers.users import get_current_user
from src.database.requests import get_user, update_user_message
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()


async def get_user_from_token(
    authorization: Optional[str] = Header(None),
    user_id_header: Optional[int] = Header(None, alias="user")  # Получаем user_id из заголовка "user"
):
    # Если заголовок Authorization отсутствует или неверного формата, возвращаем None
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")

    # Если токен администратора
    if token == os.getenv("SECRET_KEY_ADMIN"):
        # Если передан заголовок "user", используем его значение для получения пользователя
        if user_id_header is not None:
            return await get_user(user_id_header)
        # Иначе возвращаем администратора по умолчанию
        return await get_user(1)  # Администратор

    # Если токен не администратора, получаем пользователя по токену
    current_user = await get_current_user(token)
    return await get_user(current_user['user_id'])


@router.post("_gpt/")
async def gpt_request(
        request: GPTRequest,
        user: Optional[dict] = Depends(get_user_from_token)
):
    model_using = user['model_using'] if user else "gpt-3.5-turbo"

    if user and (int(user['message_count']) <= 0 or len(str(request.prompt)) > int(user['max_length_sym'])):
        raise HTTPException(status_code=403, detail="No remaining messages or message too long.")

    chat = await ChatGPT(model_using, request.prompt, request.history)
    if not chat:
        raise HTTPException(status_code=500, detail="The response from ChatGPT is empty.")

    if user:
        await update_user_message(user_id=user['id'], message_count=int(user['message_count']) - 1)

    return {"response": chat}


@router.post("_dalle/")
async def dalle_request(
        request: DalleRequest,
        user: Optional[dict] = Depends(get_user_from_token)
):
    if user and int(user['image_count']) <= 0:
        raise HTTPException(status_code=403, detail="You have no remaining image generations.")

    chat = await Dalle(prompt=request.prompt, n=request.n)
    if not chat:
        raise HTTPException(status_code=500, detail="The response from Dalle is empty.")

    if user:
        await update_user_message(user_id=user['id'], image_count=int(user['image_count']) - 1)

    return {"response": chat}
