import logging
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth.schemas.create import UserCreate
from app.api.auth.schemas.response import TokenResponse
from utils.context_utils import verify_password, create_access_token, hash_password
from model.model import User
from datetime import datetime
from sqlalchemy import select, update


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def user_register(user: UserCreate, db: AsyncSession):
    stmt = await db.execute(select(User).filter(User.username==user.username))
    existing_user = stmt.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким username уже существует"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        password=hashed_password,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)  
    target_user = new_user
    logger.info(f"Created new user with username: {user.username}")

    access_token, expire_time = create_access_token(data={"sub": str(target_user.id)})

    return TokenResponse(
        access_token=access_token,
        access_token_expire_time=expire_time
    )

async def user_login(username: str, password: str, db: AsyncSession):
    stmt = await db.execute(select(User).filter(User.username==username))
    user = stmt.scalar_one_or_none()

    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        ) 
    
    access_token, expire_time  = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(
        access_token=access_token,
        access_token_expire_time=expire_time
    )