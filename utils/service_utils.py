import hashlib

from datetime import datetime, timedelta

from fastapi import HTTPException
from typing import Optional
from fastapi import HTTPException, Request
from jose import JWTError, jwt

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from database.db import async_session_factory
from model.model import User
from utils.context_utils import get_user_by_id


async def hash_password(plain_password: str) -> str:
    return hashlib.sha256(plain_password.encode('utf-8')).hexdigest()

async def verify_password(plain_password: str, hashed_password: str) -> str:
    return await hash_password(plain_password=plain_password) == hashed_password

async def get_access_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    return parts[1]


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> tuple:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({'exp': expire, 'sub': str(data.get('sub'))})
    encoded_jwt = jwt.encode(to_encode, settings.TOKEN_SECRET_KEY, algorithm=settings.TOKEN_ALGORITHM)
    return encoded_jwt, expire.isoformat()


async def validate_token(access_token: str):
    try:
        payload = jwt.decode(
            access_token,
            settings.TOKEN_SECRET_KEY,
            algorithms=[settings.TOKEN_ALGORITHM]
        )

        data = payload.get("sub")
        if data is None:
            raise HTTPException(status_code=401, detail="Invalid token: 'sub' is missing")

        is_admin = payload.get("admin")
        if is_admin is None:
            raise HTTPException(status_code=401, detail="Invalid token: 'admin' is missing")

        exp = payload.get("exp")
        if exp and exp < datetime.utcnow().timestamp():
            raise HTTPException(status_code=401, detail="Token has expired")

        return data, is_admin

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# async def get_client_by_token(access_token: str):
#     ip_address, is_admin = await validate_token(access_token=access_token)
#     async with async_session_factory() as session:
#         if is_admin == True:
#             db_client = await session.execute(
#                 select(User)
#                 .filter(User.id == int(ip_address)) # hard code
#             )
#             client = db_client.scalar_one_or_none()
#         else:
#             db_client = await session.execute(
#                 select(Client)
#                 .filter(Client.ip_address == ip_address)
#             )
#             client = db_client.scalar_one_or_none()

#         if not client:
#             raise HTTPException(
#                 status_code=401,
#                 detail="Client not found"
#             )
#         return client

async def get_user_by_token(access_token: str, db: AsyncSession) -> User:
    user_id = await validate_token(access_token=access_token)
    user = await get_user_by_id(user_id=int(user_id), db=db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    return user