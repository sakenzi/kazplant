from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from app.api.ai_plants.commands.ai_plant_crud import (get_all_ai_plants, get_all_ai_types, 
                                                      get_all_plants_with_photo_info, upload_photos, 
                                                      create_ai_plant, get_plants_by_type_id)
from app.api.ai_plants.schemas.response import AIPlantsResponse, AITypesResponse, PlantPhotoInfo
from app.api.ai_plants.schemas.create import AiPlantCreate, UploadPhotosResponse
import logging
from typing import List
from sqlalchemy import select
from model.model import AIPlant


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.get(
    "/get-ai_plants",
    summary="Получить все классы",
    response_model=list[AIPlantsResponse]
)
async def get_ai_plants(db: AsyncSession = Depends(get_db)):
    return await get_all_ai_plants(db=db)


@router.get(
    "/get-ai_types",
    summary="Получит все типы",
    response_model=list[AITypesResponse]
)
async def get_types(db: AsyncSession = Depends(get_db)):
    return await get_all_ai_types(db=db)


@router.post(
    "/create-classes",
    summary="создание класса",
    response_model=AiPlantCreate
)
async def create_ai_plant_endpoint(
    name: str = Form(...),
    files: List[UploadFile] = File(default=None),
    db: AsyncSession = Depends(get_db)
):
    try:
        db_plant = await create_ai_plant(db, name, files)
        return AiPlantCreate(name=db_plant.name)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while creating plant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/plants-info", 
    response_model=List[PlantPhotoInfo],
    summary="Получить все классы с фотографиями"
)
async def get_plants_info(limit: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    return await get_all_plants_with_photo_info(db, limit=limit)
    

@router.post(
    "/upload-photos",
    summary="Загрузить фотографии для растения",
    response_model=UploadPhotosResponse
)
async def upload_photos_endpoint(
    ai_plant_id: int = Form(...),
    ai_type_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await upload_photos(db, ai_plant_id, ai_type_id, files)
        return UploadPhotosResponse(**result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in upload_photos_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    

@router.get(
    "/plants_by_type/{type_id}",
    response_model=List[PlantPhotoInfo],
    summary="Получить растения по ID типа"
)
async def get_plants_by_type(
    type_id: int,
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество возвращаемых растений"),
    db: AsyncSession = Depends(get_db)
):
    try:
        plants_info = await get_plants_by_type_id(db, type_id=type_id, limit=limit)
        logger.info(f"Returning {len(plants_info)} plants with type_id {type_id}")
        return plants_info
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in get_plants_by_type: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")