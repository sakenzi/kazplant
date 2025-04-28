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
    hashed_password = hash_password(user.password)

    if existing_user:
        await db.execute(
            update(User)
            .where(User.username==user.username)
            .values(
                username=user.username,
                full_name=user.full_name,
                email=user.email,
                password=hashed_password,
            )
        )
        logger.info(f"Updated user with username: {user.username}")

    else:
        new_user = User(
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            password=hashed_password,
        )
        db.add(new_user)
        logger.info(f"Created new user with username: {user.username}")

    await db.commit()

    access_token, expire_time = create_access_token(data={"sub": user.username})

    return TokenResponse(
        access_token=access_token,
        access_token_expire_time=expire_time
    )

