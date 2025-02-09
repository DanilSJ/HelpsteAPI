from pydantic import BaseModel


class SubscribeModel(BaseModel):
    name: str
    price: int

class SubscribeUpdateModel(BaseModel):
    subscribe_id: int
    name: str
    price: int
