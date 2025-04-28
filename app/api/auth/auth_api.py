from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter
import logging
from database.db import get_db
from app.api.auth.commands.auth_crud import user_register, user_login
from app.api.auth.schemas.create import UserBase, UserCreate
from app.api.auth.schemas.response import TokenResponse


router = APIRouter()

@router.post(
    '/register-user',
    summary="Регистрация пользователя",
    response_model=TokenResponse
)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_register(user=user, db=db)

@router.post(
    'login-user',
    summary="Login пользователя",
    response_model=TokenResponse
)
async def login(login_data: UserBase, db: AsyncSession = Depends(get_db)):
    return await user_login(username=login_data.username, password=login_data.password, db=db)