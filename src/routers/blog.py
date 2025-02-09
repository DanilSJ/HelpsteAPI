from fastapi import APIRouter, HTTPException, Body, Depends
from src.database.requests import get_blogs, create_blog, get_blog_by_id, update_blog, delete_blog
from pydantic import BaseModel
from .admin import verify_token, admin_required


router = APIRouter()

class BlogModel(BaseModel):
    title: str
    text: str
    img: str
    link: str

@router.get("/")
async def fetch_blogs():
    """Получает список блогов."""
    blogs = await get_blogs()
    if not blogs:
        raise HTTPException(status_code=404, detail="No blogs found")
    return blogs

@router.post("/")
async def add_blog(request: BlogModel, token: str = Depends(admin_required)):
    """Создает новый блог."""
    created_blog = await create_blog(
        title=request.title,
        text=request.text,
        img=request.img,
        link=request.link
    )
    return created_blog

@router.get("/{blog_id}")
async def fetch_blog(blog_id: int):
    """Получает конкретный блог по ID."""
    blog = await get_blog_by_id(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

@router.put("/{blog_id}")
async def update_blog_by_id(blog_id: int, request: BlogModel, token: str = Depends(admin_required)):
    """Обновляет блог по ID."""
    updated_blog = await update_blog(
        blog_id=blog_id,
        title=request.title,
        text=request.text,
        img=request.img,
        link=request.link
    )
    if not updated_blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return updated_blog

@router.delete("/{blog_id}")
async def delete_blog_by_id(blog_id: int, token: str = Depends(admin_required)):
    result = await delete_blog(blog_id)
    return result