from fastapi import Depends, APIRouter, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from app.api.segmentations.schemas.response import SegmentationPhotoInfo
from app.api.segmentations.commands.segmentation_crud import get_segmentations_by_type_id
from typing import List


router = APIRouter()

@router.get(
    "/segmentations_by_type/{type_id}",
    response_model=List[SegmentationPhotoInfo],
    summary="Получить наборы данных сегментации по ID типа"
)
async def get_segmentations_by_type(
    type_id: int,
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество возвращаемых наборов"),
    db: AsyncSession = Depends(get_db)
):
    try:
        segmentations_info = await get_segmentations_by_type_id(db, type_id=type_id, limit=limit)
        return segmentations_info
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")