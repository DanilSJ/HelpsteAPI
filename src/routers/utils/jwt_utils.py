from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Header, Depends, status
from fastapi.security import OAuth2PasswordBearer
import os

ALGORITHM = "HS256"
SECRET_KEY_USER = os.getenv("SECRET_KEY_USER")
SECRET_KEY_ADMIN = os.getenv("SECRET_KEY_ADMIN")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_jwt_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY_USER, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        if token == SECRET_KEY_ADMIN:
            return {"admin": True}

        payload = jwt.decode(token, SECRET_KEY_USER, algorithms=[ALGORITHM])

        expire = payload.get("exp")
        if expire and datetime.utcnow() > datetime.utcfromtimestamp(expire):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = payload.get("login")
        user_id = payload.get("user_id")
        admin = payload.get("admin")

        if user is None and user_id is None and admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
            )

        return {"login": user, "user_id": user_id, "admin": payload.get("admin", False)}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_token_from_header(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        return token
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")