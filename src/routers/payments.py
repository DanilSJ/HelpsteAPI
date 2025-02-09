from fastapi import APIRouter, HTTPException
from src.database.requests import create_user_payment, get_user_payments
from src.routers.sheme.PaymentsModels import *

router = APIRouter()


@router.post("/{identifier}")
async def create_payment(identifier: int, payment: PaymentModel):
    """Создает запись о платеже для пользователя."""
    payment_created = await create_user_payment(
        user_id=identifier,
        payment_id=payment.payment_id,
        subscribe=payment.subscribe,
        time=payment.time,
        price=payment.price
    )
    if not payment_created:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Payment created successfully"}

@router.get("/{identifier}")
async def fetch_user_payments(identifier: int):
    """Возвращает последний платеж пользователя."""
    payment = await get_user_payments(identifier)
    if not payment:
        raise HTTPException(status_code=404, detail="No payments found")
    return payment
