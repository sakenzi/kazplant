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
    batch: int,
    name_model: str
):
    saved_paths = []

    if type_id == 1:
        base_dir = TRAIN_DIR
    elif type_id == 2:
        base_dir = VALID_DIR
    else:
        raise ValueError(f"Invalid type_id: {type_id}. Expected 1 (train) or 2 (valid)")

    plant = await db.get(AIPlant, plant_id)
    if not plant:
        raise ValueError(f"Plant with ID {plant_id} not found")

    ai_type = await db.get(AIType, type_id)
    if not ai_type:
        raise ValueError(f"Type with ID {type_id} not found")

    folder_path = os.path.join(base_dir, plant.name)
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

    task = start_training_task.delay(batch=batch, epoch=epoch, name_model=name_model)

    return {"message": "Photos saved and training started", "files": saved_paths, "task_id": task.id}