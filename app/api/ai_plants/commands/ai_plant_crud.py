from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from model.model import AIPlant, AIType, AIPhoto, TypeDataset
import logging
from fastapi import HTTPException
from sqlalchemy.sql import text, func
from typing import List
from fastapi import UploadFile
import uuid
import random
from app.api.ai_plants.schemas.response import PlantPhotoInfo
from sqlalchemy.orm import selectinload


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

TRAIN_DIR = "C:/projects/FASTAPI/kazplant/kazplant/new_plant/classification/New Plant Diseases Dataset(Augmented)/train"
VALID_DIR = "C:/projects/FASTAPI/kazplant/kazplant/new_plant/classification/New Plant Diseases Dataset(Augmented)/valid"

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

async def create_ai_plant(
    db: AsyncSession,
    name: str,
    files: List[UploadFile] | None = None
) -> AIPlant:
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

    if files:
        saved_paths = []
        folder_path = train_folder_path  
        for file in files:
            filename = f"{uuid.uuid4()}.jpg"
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, "wb") as buffer:
                    buffer.write(await file.read())
                photo = AIPhoto(
                    photo=file_path.replace("\\", "/"),
                    ai_plant_id=db_plant.id,
                    ai_type_id=None,  
                    type_dataset_id=None  
                )
                db.add(photo)
                saved_paths.append(file_path)
            except Exception as e:
                logger.error(f"Failed to save photo {filename}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to save photo: {str(e)}")
        
        await db.commit()
        logger.info(f"Saved {len(saved_paths)} photos for plant '{folder_name}' (ID: {db_plant.id}) in {folder_path}")

    return db_plant

async def get_all_plants_with_photo_info(db: AsyncSession, limit: int = 10) -> list[PlantPhotoInfo]:
    result = await db.execute(
        select(AIPlant).options(selectinload(AIPlant.ai_photos)).limit(limit)
    )
    plants = result.scalars().all()

    plant_data = []

    for plant in plants:
        photos = plant.ai_photos
        total_photos = len(photos)
        random_photo = random.choice(photos).photo if total_photos > 0 else None

        if total_photos > 0:
            random_photo_obj = random.choice(photos)
            random_photo = random_photo_obj.photo
            type_id = random_photo_obj.ai_type_id

        plant_data.append(PlantPhotoInfo(
            plant_id=plant.id,
            type_id=type_id,
            plant_name=plant.name,
            random_photo=random_photo,
            total_photos=total_photos
        ))

    return plant_data

async def upload_photos(
    db: AsyncSession,
    ai_plant_id: int,
    ai_type_id: int,
    files: List[UploadFile]
) -> dict:
    plant = await db.get(AIPlant, ai_plant_id)
    if not plant:
        logger.error(f"Plant with ID {ai_plant_id} not found")
        raise HTTPException(status_code=404, detail=f"Plant with ID {ai_plant_id} not found")
    
    ai_type = await db.get(AIType, ai_type_id)
    if not ai_type:
        logger.error(f"Type with ID {ai_type_id} not found")
        raise HTTPException(status_code=404, detail=f"Type with ID {ai_type_id} not found")
    
    folder_path = TRAIN_DIR if ai_type.type_name.lower() == "train" else VALID_DIR
    plant_folder = os.path.join(folder_path, plant.name)

    try:
        os.makedirs(plant_folder, exist_ok=True)
        logger.info(f"Ensured folder exists: {plant_folder}")
    except OSError as e:
        logger.error(f"Failed to create folder {plant_folder}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create folder: {str(e)}")
    
    saved_paths = []
    for file in files:
        filename = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join(plant_folder, filename)
        try:
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            photo = AIPhoto(
                photo=file_path.replace("\\", "/"),
                ai_plant_id=ai_plant_id,
                ai_type_id=ai_type_id,
            )
            db.add(photo)
            saved_paths.append(file_path)
        except Exception as e:
            logger.error(f"Failed to save photo {filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save photo: {str(e)}")

    await db.commit()
    logger.info(f"Saved {len(saved_paths)} photos for plant ID {ai_plant_id} in {plant_folder}")

    return {
        "photo_count": len(saved_paths),
        "saved_paths": saved_paths
    }

async def get_plants_by_type_id(db: AsyncSession, type_id: int, limit: int = 10) -> List[PlantPhotoInfo]:
    type_exists = await db.execute(select(AIType).where(AIType.id == type_id))
    if not type_exists.scalars().first():
        logger.error(f"Type with ID {type_id} not found")
        raise HTTPException(status_code=404, detail=f"Type with ID {type_id} not found")

    result = await db.execute(
        select(AIPlant)
        .join(AIPhoto, AIPhoto.ai_plant_id == AIPlant.id)
        .where(AIPhoto.ai_type_id == type_id)
        .options(selectinload(AIPlant.ai_photos))
        .group_by(AIPlant.id)
        .limit(limit)
    )
    plants = result.scalars().all()

    plant_data = []

    for plant in plants:
        photos = [photo for photo in plant.ai_photos if photo.ai_type_id == type_id]
        total_photos = len(photos)
        random_photo = None

        if total_photos > 0:
            random_photo_obj = random.choice(photos)
            random_photo = random_photo_obj.photo
        else:
            logger.warning(f"No photos with type_id {type_id} for plant {plant.name}")

        plant_data.append(PlantPhotoInfo(
            plant_id=plant.id,
            type_id=type_id,
            plant_name=plant.name,
            random_photo=random_photo,
            total_photos=total_photos
        ))

    logger.info(f"Retrieved {len(plant_data)} plants with type_id {type_id}")
    return plant_data