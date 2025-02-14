from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from datetime import datetime
from src.routers.users import get_current_user
from src.routers.sheme.TinkoffModels import *
from src.routers.utils.tinkoff_utils import *
from src.database.requests import update_user, update_user_message, subscribe_search
import asyncio


router = APIRouter()


async def check_payment_status_periodically(payment_id: int, identifier: int, subscribe, subscribe_time):
    while True:
        payment_status = await check_payment_status(payment_id)

        if payment_status.get("Status") == "CONFIRMED":
            await update_user(
                user_id=identifier,
                subscribe=subscribe,
                subscribe_time=subscribe_time,
            )
            break

        if payment_status.get("Status") == "CANCELED":
            break

        await asyncio.sleep(10)


@router.post("/")
async def add_tinkoff(
        request: TinkoffAddModel,
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(get_current_user)
):
    order_id = str(datetime.now().timestamp()).replace('.', '')
    description = f"Подписка {request.subscription_type}, время: {request.subscription_time}"
    payment = await make_payment(request.amount, order_id, description, request.id)

    subscribe = await subscribe_search(request.subscription_type)

    if subscribe:
        await update_user_message(
            user_id=request.id,
            message_count=subscribe['message_count'],
            max_length_sym=subscribe['max_length_sym'],
            image_count=subscribe['image_count'],
            voice_count=subscribe['voice_count']
        )

    if not payment:
        raise HTTPException(status_code=404, detail="Error")

    background_tasks.add_task(check_payment_status_periodically, payment["PaymentId"], request.id, request.subscription_type, request.subscription_time)

    return {"message": payment}

@router.get("/{payment_id}/")
async def check_tinkoff_status_payment(payment_id: int, current_user: dict = Depends(get_current_user)):
    payment = await check_payment_status(payment_id)

    if not payment:
        raise HTTPException(status_code=404, detail="Error")
    return {"message": payment}
