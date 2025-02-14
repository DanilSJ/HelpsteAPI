from fastapi import APIRouter, HTTPException, Header
from src.plugin.ai import ChatGPT, Dalle
from src.routers.sheme.AiModels import *
from src.routers.users import get_current_user
from src.database.requests import get_user, update_user_message
from typing import Optional

router = APIRouter()

user = None


@router.post("_gpt/")
async def gpt_request(
        request: GPTRequest,
        authorization: Optional[str] = Header(None)  # Получаем необязательный заголовок Authorization
):
    try:

        if authorization:
            # Если заголовок передан, извлекаем токен
            if authorization.startswith("Bearer "):
                token = authorization.replace("Bearer ", "")
                try:
                    current_user = await get_current_user(token)
                    user = await get_user(current_user['user_id'])
                except Exception as e:
                    raise HTTPException(status_code=401, detail="Invalid token or user not found")
            else:
                raise HTTPException(status_code=401, detail="Invalid authorization format")

        # Если пользователь найден, используем его модель, иначе — модель по умолчанию
        model_using = user['model_using'] if user else "gpt-3.5-turbo"

        if user is not None:
            if int(user['message_count']) != 0:
                if len(str(request.prompt)) > int(user['max_length_sym']):
                    raise HTTPException(
                        status_code=403,
                        detail="Long message."
                    )
                else:
                    chat = await ChatGPT(model_using, request.prompt, request.history)
            else:
                raise HTTPException(
                    status_code=403,
                    detail="You have no remaining messages."
                )
        else:
            chat = await ChatGPT(model_using, request.prompt, request.history)

        if user is not None:
            await update_user_message(
                user_id=user['id'],
                message_count=int(user['message_count']) - 1
            )

        if not chat:
            raise HTTPException(status_code=500, detail="The response from ChatGPT is empty.")
        return {"response": chat}

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("_dalle/")
async def dalle_request(
        request: DalleRequest,
        authorization: Optional[str] = Header(None)
):
    try:

        if authorization:
            # Если заголовок передан, извлекаем токен
            if authorization.startswith("Bearer "):
                token = authorization.replace("Bearer ", "")
                try:
                    current_user = await get_current_user(token)
                    user = await get_user(current_user['user_id'])
                except Exception as e:
                    raise HTTPException(status_code=401, detail="Invalid token or user not found")
            else:
                raise HTTPException(status_code=401, detail="Invalid authorization format")

        if user is not None:
            if int(user['image_count']) != 0:
                chat = await Dalle(prompt=request.prompt, n=request.n)
            else:
                raise HTTPException(
                    status_code=403,
                    detail="You have no remaining messages."
                )
        else:
            chat = await Dalle(prompt=request.prompt, n=request.n)

        if user is not None:
            await update_user_message(
                user_id=user['id'],
                image_count=int(user['image_count']) - 1
            )

        if not chat:
            raise HTTPException(status_code=500, detail="The response from Dalle is empty.")
        return {"response": chat}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
