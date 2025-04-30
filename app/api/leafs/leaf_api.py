from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter, File, UploadFile, Request, HTTPException
from database.db import get_db
from app.api.leafs.commands.leaf_crud import create_leaf
from app.api.leafs.schemas.response import LeafDiseaseResponse
from utils.context_utils import get_access_token, validate_access_token


router = APIRouter()

@router.post(
    "/create-leaf",
    summary="Получить о заболеваний",
    response_model=LeafDiseaseResponse
)
async def upload_leaf(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        access_token = await get_access_token(request)
        user_id_str = await validate_access_token(access_token)
        user_id = int(user_id_str)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return await create_leaf(file=file, db=db, user_id=user_id)