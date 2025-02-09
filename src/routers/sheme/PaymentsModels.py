from pydantic import BaseModel


class PaymentModel(BaseModel):
    payment_id: str
    subscribe: str
    time: int
    price: float