from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from model.model import AIPlant, AIType
import logging
from fastapi import HTTPException
from sqlalchemy.sql import text


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

TRAIN_DIR = "C:/projects/FASTAPI/kazplant/kazplant/new_plant/New Plant Diseases Dataset(Augmented)/train"
VALID_DIR = "C:/projects/FASTAPI/kazplant/kazplant/new_plant/New Plant Diseases Dataset(Augmented)/valid"

async def get_all_ai_plants(db: AsyncSession):
    stmt = await db.execute(select(AIPlant))
    ai_plants = stmt.scalars().unique().all()

    if not ai_plants:
        return []
    
    return ai_plants

async def get_all_ai_types(db: AsyncSession):
    stmt = await db.execute(select(AIType))
    ai_types = stmt.scalars().unique().all()

    if not ai_types:
        return []
    
    return ai_types

async def create_ai_plant(db: AsyncSession, name: str) -> AIPlant:
    if not name or not name.strip():
        logger.error("Название растения не может быть пустым")
        raise HTTPException(status_code=400, detail="Название класса не может быть пустым")
    
    folder_name = name.strip().replace(" ", "_").replace("/", "_").replace("\\", "_")

    result = await db.execute(
        text("SELECT * FROM ai_plants WHERE name = :name"),
        {"name": folder_name}
    )
    if result.scalar():
        logger.warning(f"Plant with name '{folder_name}' already exists")
        raise HTTPException(status_code=400, detail=f"Plant with name '{folder_name}' already exists")
    
    train_folder_path = os.path.join(TRAIN_DIR, folder_name)
    valid_folder_path = os.path.join(VALID_DIR, folder_name)
    
    try:
        os.makedirs(train_folder_path, exist_ok=True)
        os.makedirs(valid_folder_path, exist_ok=True)
        logger.info(f"Created folders: {train_folder_path}, {valid_folder_path}")
    except OSError as e:
        logger.error(f"Failed to create folders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create folders: {str(e)}")

    db_plant = AIPlant(name=folder_name)
    db.add(db_plant)
    await db.commit()
    await db.refresh(db_plant)
    logger.info(f"Plant saved with ID: {db_plant.id}")

    return db_plant