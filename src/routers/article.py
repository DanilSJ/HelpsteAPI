from fastapi import APIRouter, HTTPException, Body, Depends
from src.database.requests import get_articles, create_article, get_article_by_id
from pydantic import BaseModel
from .admin import verify_token, admin_required

router = APIRouter()

class ArticleModel(BaseModel):
    text: str
    img: str
    link: str
    
@router.get("/")
async def fetch_articles():
    """Получает список статей."""
    articles = await get_articles()
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found")
    return articles

@router.post("/")
async def add_article(request: ArticleModel, token: str = Depends(admin_required)):
    """Создает новую статью."""
    created_article = await create_article(
        text=request.text,
        img=request.img,
        link=request.link
    )
    return created_article

@router.get("/{article_id}")
async def fetch_article(article_id: int):
    """Получает конкретную статью по ID."""
    article = await get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
