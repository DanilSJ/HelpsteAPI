from pydantic import BaseModel


class BlogModel(BaseModel):
    title: str
    text: str
    img: str
    link: str