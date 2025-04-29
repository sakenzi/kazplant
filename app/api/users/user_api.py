from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter, Request
from app.api.users.commands.user_crud import get_user
from app.api.users.schemas.response import UserResponse
from database.db import get_db
from utils.context_utils import validate_access_token, get_access_token


router = APIRouter()

@router.get(
    "/get-user",
    summary="Получить данные пользователя",
    response_model=UserResponse
)
async def get_user_by_id(request: Request, db: AsyncSession = Depends(get_db)):
    token = await get_access_token(request)
    user_id = await validate_access_token(token)
    user = await get_user(user_id, db)
    return user