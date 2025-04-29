import uuid
import os
import aiofiles
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from model.model import Plant, PlantPhoto, PlantPhotoID
import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def create_plant(
    user_id: int,
    name: str,
    description: str | None,
    probability: float,
    family: str | None,
    kingdom: str | None,
    photo: UploadFile,
    db: AsyncSession
) -> Plant:
    logger.debug(f"Creating plant with name={name}, probability={probability}")

    photo_path = None
    try:
        sanitized_filename = "".join(c if c.isalnum() or c in ('.', '_') else '_' for c in photo.filename)
        photo_filename = f"uploads/photos/plants/{uuid.uuid4()}_{sanitized_filename}"
        os.makedirs(os.path.dirname(photo_filename), exist_ok=True)
        async with aiofiles.open(photo_filename, "wb") as f:
            await f.write(await photo.read())
        photo_path = photo_filename
    except Exception as e:
        logger.error(f"Failed to save photo: {e}")
        raise HTTPException(status_code=500, detail="Failed to save photo")
    
    plant_photo = PlantPhoto(photo=photo_path)
    db.add(plant_photo)
    await db.flush()

    plant = Plant(
        user_id=user_id,
        name=name,
        description=description,
        probability=probability,
        family=family,
        kingdom=kingdom
    )
    db.add(plant)
    await db.flush()

    plant_photo_id = PlantPhotoID(
        plant_id=plant.id,
        photo_id=plant_photo.id
    )
    db.add(plant_photo_id)

    try:
        await db.commit()
        await db.refresh(plant)
    except Exception as e:
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)  
        logger.error(f"Error creating plant: {e}")
        raise HTTPException(status_code=500, detail="Failed to create plant")

    logger.info(f"Plant created with id={plant.id}")
    return plant


async def get_all_plants(user_id: int, db: AsyncSession):
    stmt = await db.execute(
        select(Plant)
        .filter(Plant.user_id == user_id)
        .options(
            selectinload(Plant.plant_photo_ids).selectinload(PlantPhotoID.photo)
        )
    )
    plants = stmt.scalars().unique().all()

    if not plants:
        return []
    
    return plants


async def get_plant(plant_id: int, db: AsyncSession):
    stmt = select(Plant).options(
        selectinload(Plant.plant_photo_ids).selectinload(PlantPhotoID.photo)
    ).filter(Plant.id == plant_id)

    result = await db.execute(stmt)
    plant = result.scalars().first()

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    photos = [photo_id.photo for photo_id in plant.plant_photo_ids if photo_id.photo]

    plant.photos = photos
    return plant