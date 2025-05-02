from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from app.api.ai_plants.commands.ai_plant_crud import get_all_ai_plants, get_all_ai_types, get_all_plants_with_photo_info
from app.api.ai_plants.schemas.response import AIPlantsResponse, AITypesResponse, PlantPhotoInfo
from app.api.ai_plants.schemas.create import AiPlantCreate
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

@router.get("/plants-info", response_model=List[PlantPhotoInfo])
async def get_plants_info(limit: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    return await get_all_plants_with_photo_info(db, limit=limit)
    