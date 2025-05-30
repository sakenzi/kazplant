import base64
import httpx
from fastapi import APIRouter, Depends, UploadFile, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from app.api.plants.schemas.response import PlantResponse, PlantIDResponse
from app.api.plants.commands.plant_crud import create_plant, get_all_plants, get_plant, get_plants_from_db
from app.api.plants.commands.g4f_plant import process_plant_data_with_g4f
import logging
import os
from dotenv import load_dotenv
from utils.context_utils import validate_access_token, get_access_token
from sqlalchemy import select
from model.model import Plant, PlantPhoto, PlantPhotoID


load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

PLANT_ID_API_KEY = os.getenv('PLANT_ID_API_KEY')

@router.post(
    "/identify-plant",
    summary="Идентифицировать растение по фото",
    response_model=PlantResponse
)
async def identify_plant(
    request: Request,
    photo: UploadFile,
    db: AsyncSession = Depends(get_db)
):
    logger.debug(f"Received plant identification request with photo: {photo.filename}")

    try:
        access_token = await get_access_token(request)
        user_id_str = await validate_access_token(access_token)
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user_id format in token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    photo_content = await photo.read()
    base64_image = base64.b64encode(photo_content).decode('utf-8')
    base64_image_with_prefix = f"data:image/jpeg;base64,{base64_image}"

    async with httpx.AsyncClient() as client:
        plant_id_response = await client.post(
            "https://plant.id/api/v3/identification",
            headers={"Api-Key": PLANT_ID_API_KEY},
            json={
                "images": [base64_image_with_prefix],
                "latitude": 49.207,
                "longitude": 16.608,
                "similar_images": True
            }
        )

    if plant_id_response.status_code not in (200, 201):
        logger.error(f"Plant.id API error: {plant_id_response.status_code} - {plant_id_response.text}")
        raise HTTPException(status_code=500, detail=f"Plant.id API error: {plant_id_response.status_code}")

    plant_id_data = plant_id_response.json()

    suggestions = plant_id_data.get("result", {}).get("classification", {}).get("suggestions", [])
    if not suggestions:
        logger.warning("No plant suggestions found")
        raise HTTPException(status_code=404, detail="No plant identified")

    plant_name = suggestions[0]["name"]
    probability = suggestions[0]["probability"]

    g4f_data = await process_plant_data_with_g4f(plant_name, probability)

    photo.file.seek(0)

    plant = await create_plant(
        user_id=user_id,
        name=g4f_data["name"],
        description=g4f_data["description"],
        probability=probability,
        family=g4f_data["family"],
        kingdom=g4f_data["kingdom"],
        photo=photo,
        db=db
    )

    stmt = (
        select(PlantPhoto)
        .join(PlantPhotoID, PlantPhoto.id == PlantPhotoID.photo_id)
        .where(PlantPhotoID.plant_id == plant.id)
    )
    result = await db.execute(stmt)
    photos = result.scalars().all()

    return PlantResponse(
        id=plant.id,
        name=plant.name,
        description=plant.description,
        probability=plant.probability,
        family=plant.family,
        kingdom=plant.kingdom,
        photos=photos
    )

@router.get(
    "/plants",
    summary="Получить все растения пользователя",
    response_model=list[PlantResponse]
)
async def get_plants(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        access_token = await get_access_token(request)
        user_id_str = await validate_access_token(access_token)
        user_id = int(user_id_str)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    plants = await get_all_plants(user_id=user_id, db=db)

    return [
        {
            "id": plant.id,
            "name": plant.name,
            "description": plant.description,
            "probability": plant.probability,
            "family": plant.family,
            "kingdom": plant.kingdom,
            "photos": [
                {
                    "id": rel.photo.id,
                    "photo": rel.photo.photo
                }
                for rel in plant.plant_photo_ids if rel.photo is not None
            ]
        }
        for plant in plants
    ]


@router.get(
    "/plant/{plant_id}", 
    response_model=PlantResponse, 
    summary="Получить растение по ID"
)
async def get_plant_by_id(plant_id: int, db: AsyncSession = Depends(get_db)):
    return await get_plant(plant_id, db)


@router.get(
    "/all-plants",
    summary="Получить все растения",
    response_model=list[PlantResponse]
)
async def get_plants(
    db: AsyncSession = Depends(get_db)
):  
    plants = await get_plants_from_db(db=db)  

    return [
        {
            "id": plant.id,
            "name": plant.name,
            "description": plant.description,
            "probability": plant.probability,
            "family": plant.family,
            "kingdom": plant.kingdom,
            "photos": [
                {
                    "id": rel.photo.id,
                    "photo": rel.photo.photo
                }
                for rel in plant.plant_photo_ids if rel.photo is not None
            ]
        }
        for plant in plants
    ]