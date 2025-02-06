from fastapi import APIRouter, HTTPException, Body, Depends
from src.database.requests import add_message_to_gpt, get_user_messages, get_assistant_messages
from .users import get_current_user

router = APIRouter()

@router.post("/{identifier}")
async def add_gpt_message(identifier: int, message: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """Добавляет сообщение в историю GPT пользователя."""
    added = await add_message_to_gpt(user_id=identifier, message=message)
    if not added:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Message added successfully"}

@router.get("/{identifier}")
async def fetch_user_messages(identifier: int, current_user: dict = Depends(get_current_user)):
    """Возвращает все сообщения пользователя."""
    messages = await get_user_messages(identifier)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found")
    return messages

@router.get("/{identifier}/assistant")
async def fetch_assistant_messages(identifier: int, current_user: dict = Depends(get_current_user)):
    """Возвращает сообщения ассистента для пользователя."""
    messages = await get_assistant_messages(identifier)
    if not messages:
        raise HTTPException(status_code=404, detail="No assistant messages found")
    return messages

# @router.delete("/{message_id}")
# async def delete_message(message_id: int):
#     deleted = await remove_message(message_id)
#     if not deleted:
#         raise HTTPException(status_code=404, detail="Message not found")
#     return {"message": "Message deleted successfully"}