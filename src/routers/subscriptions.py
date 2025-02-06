from fastapi import APIRouter, HTTPException, Depends
from src.database.requests import get_subscribe, add_subscribe, update_subscribe as update_subscribe_db
from pydantic import BaseModel
from .admin import verify_token, admin_required

router = APIRouter()

class SubscribeModel(BaseModel):
    name: str
    price: int

class SubscribeUpdateModel(BaseModel):
    subscribe_id: int
    name: str
    price: int

@router.get("/")
async def fetch_subscribes():
    """Возвращает список доступных подписок."""
    subscribes = await get_subscribe()
    if not subscribes:
        raise HTTPException(status_code=404, detail="No subscribes found")
    return subscribes

@router.post("/")
async def create_subscribe(request: SubscribeModel, token: str = Depends(admin_required)):
    """Создание подписки"""
    subscribes = await add_subscribe(request.name, request.price)
    if not subscribes:
        raise HTTPException(status_code=404, detail="Error")
    return subscribes

@router.patch("/")
async def update_subscribe(request: SubscribeUpdateModel, token: str = Depends(admin_required)):
    """Обновление подписки"""
    subscribes = await update_subscribe_db(request.subscribe_id, request.name, request.price)
    if not subscribes:
        raise HTTPException(status_code=404, detail="Error")
    return subscribes
