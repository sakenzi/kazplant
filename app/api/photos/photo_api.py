from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter, UploadFile, File
from app.api.photos.commands.photo_crud import save_photos_to_db
from database.db import get_db
from typing import List
import os


UPLOAD_DIR = "uploads/photos/plants"


router = APIRouter()

@router.post(
    "/add-photos",
    summary="Добавить несколько фотографий",
)
async def uploads_photos(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    saved_paths = []

    for file in files:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())
        saved_paths.append(file_location)

    saved_ids = await save_photos_to_db(saved_paths, db)
    return {"saved_photo_ids": saved_ids}