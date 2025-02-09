from pydantic import BaseModel


class TinkoffAddModel(BaseModel):
    id: int
    amount: int
    subscription_type: str
    subscription_time: str