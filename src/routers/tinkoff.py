from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from src.routers.users import get_current_user
from src.routers.sheme.TinkoffModels import *
from src.routers.utils.tinkoff_utils import *

router = APIRouter()


@router.post("/")
async def add_tinkoff(request: TinkoffAddModel, current_user: dict = Depends(get_current_user)):
    order_id = str(datetime.now().timestamp()).replace('.', '')
    description = f"Подписка {request.subscription_type}, время: {request.subscription_time}"
    payment = await make_payment(request.amount, order_id, description, user_id=request.id)

    if not payment:
        raise HTTPException(status_code=404, detail="Error")
    return {"message": payment}

@router.get("/{payment_id}/")
async def check_tinkoff_status_payment(payment_id: int, current_user: dict = Depends(get_current_user)):
    payment = await check_payment_status(payment_id)

    if not payment:
        raise HTTPException(status_code=404, detail="Error")
    return {"message": payment}
