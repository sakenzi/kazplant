from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from model.model import User
from fastapi import HTTPException


async def get_user(user_id: int, db: AsyncSession):
    user_id = int(user_id)
    stmt = await db.execute(select(User).filter(User.id == user_id))
    user = stmt.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user