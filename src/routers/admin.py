from fastapi import APIRouter, HTTPException, Depends
from src.database.models import async_session, User
from sqlalchemy import select
import hashlib
from datetime import timedelta
from dotenv import load_dotenv
from src.routers.sheme.AdminModels import *
from src.routers.utils.jwt_utils import create_jwt_token, get_current_user, get_token_from_header


load_dotenv()
router = APIRouter()
TOKEN_EXPIRE_MINUTES = 60

async def admin_required(token: str = Depends(get_token_from_header)):
    payload = await get_current_user(token)

    if not payload.get("admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


@router.post("/auth/")
async def auth_admin(request: AdminModel):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.login == request.login))
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        hashed_password = hashlib.sha256(request.password.encode()).hexdigest()
        if user.password != hashed_password:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.admin:
            raise HTTPException(status_code=403, detail="Access denied")

        token = create_jwt_token({"sub": user.login, "admin": True}, timedelta(minutes=TOKEN_EXPIRE_MINUTES))
        return {"access_token": token, "token_type": "bearer"}


@router.get("/protected/")
async def protected_route(token: str = Depends(admin_required)):
    return {"message": "Access granted", "user": token}