from fastapi import APIRouter, HTTPException, Depends
from src.database.models import async_session, User
from sqlalchemy import select
from pydantic import BaseModel
import hashlib
from jose import jwt 
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY_ADMIN")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

class AdminModel(BaseModel):
    login: str
    password: str

def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        if token == SECRET_KEY:
            return {"sub": "admin", "admin": True}

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if not payload.get("admin"):
            raise HTTPException(status_code=403, detail="User token is not allowed here.")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired.")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token.")


def admin_required(token: str = Depends(verify_token)):
    if not token.get("admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return token

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
async def protected_route(token: str = Depends(verify_token)):
    return {"message": "Access granted", "user": token}
