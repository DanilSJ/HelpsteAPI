from fastapi import APIRouter, HTTPException, Depends
from src.database.requests import get_articles, create_article, get_article_by_id, update_article, delete_article
from .admin import admin_required
from src.routers.sheme.ArticleModels import *

router = APIRouter()
    
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
        title=request.title,
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

@router.put("/{article_id}")
async def update_blog_by_id(article_id: int, request: ArticleModel, token: str = Depends(admin_required)):
    """Обновляет блог по ID."""
    updated_blog = await update_article(
        article_id=article_id,
        title=request.title,
        text=request.text,
        img=request.img,
        link=request.link
    )
    if not updated_blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return updated_blog

@router.delete("/{article_id}")
async def delete_article_by_id(article_id: int, token: str = Depends(admin_required)):
    result = await delete_article(article_id)
    return result