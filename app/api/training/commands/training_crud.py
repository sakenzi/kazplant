import os
import shutil
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from model.model import AIPhoto, AIPlant, AIType
from fastapi import UploadFile
from app.api.training.celery.tasks import start_training_task


TRAIN_DIR = "C:/projects/FASTAPI/kazplant/kazplant/new_plant/New Plant Diseases Dataset(Augmented)/train"
VALID_DIR = "C:/projects/FASTAPI/kazplant/kazplant/new_plant/New Plant Diseases Dataset(Augmented)/valid"

async def save_photos_and_trigger_training(
    db: AsyncSession,
    files: list[UploadFile],
    plant_id: int,
    type_id: int,
    epoch: int,
    batch: int
):
    saved_paths = []

    base_dir = TRAIN_DIR if type_id == 1 else VALID_DIR

    folder_path = os.path.join(base_dir, str(plant_id))
    os.makedirs(folder_path, exist_ok=True)

    for file in files:
        filename = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        photo = AIPhoto(
            photo=file_path.replace("\\", "/"),
            ai_type_id=type_id,
            ai_plant_id=plant_id
        )
        db.add(photo)
        saved_paths.append(file_path)

    await db.commit()

    start_training_task.delay(batch=batch, epoch=epoch)

    return {"message": "Photos saved and training started", "files": saved_paths}