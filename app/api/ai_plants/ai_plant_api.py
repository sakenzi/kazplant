from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from app.api.ai_plants.commands.ai_plant_crud import get_all_ai_plants, get_all_ai_types, create_ai_plant
from app.api.ai_plants.schemas.response import AIPlantsResponse, AITypesResponse
from app.api.ai_plants.schemas.create import AiPlantCreate
import logging


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
async def create_ai_plant_endpoint(plant: AiPlantCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Received request to create plant with name: {plant.name}")
    try:
        db_plant = await create_ai_plant(db, plant.name)
        return AiPlantCreate(name=db_plant.name)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while creating plant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")