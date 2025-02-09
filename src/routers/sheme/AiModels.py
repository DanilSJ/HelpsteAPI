from pydantic import BaseModel


class GPTRequest(BaseModel):
    model: str
    prompt: str
    history: list

class DalleRequest(BaseModel):
    prompt: str
    n: int