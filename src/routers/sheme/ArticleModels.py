from pydantic import BaseModel


class ArticleModel(BaseModel):
    title: str
    text: str
    img: str
    link: str