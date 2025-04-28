from sqlalchemy.ext.asyncio import AsyncSession
from model.model import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload


async def get_user_by_id(user_id: int, db: AsyncSession) -> User:
    user = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .filter(User.id == user_id)
    )
    return user.scalars().first()