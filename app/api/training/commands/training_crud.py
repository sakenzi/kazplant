import os
from sqlalchemy.ext.asyncio import AsyncSession
from model.model import AIPlant, TrainingSession, TrainingEpoch
from app.api.training.celery.tasks import start_training_task
from typing import List, Optional
from sqlalchemy import select, func


TRAIN_DIR = "C:/projects/FASTAPI/kazplant/kazplant/new_plant/classification/New Plant Diseases Dataset(Augmented)/train"
VALID_DIR = "C:/projects/FASTAPI/kazplant/kazplant/new_plant/classification/New Plant Diseases Dataset(Augmented)/valid"

async def trigger_training(
    db: AsyncSession,
    epoch: int,
    batch: int,
    name_model: str
) -> dict:
    if epoch <= 0:
        raise ValueError("Number of epochs must be positive")
    if batch <= 0:
        raise ValueError("Batch size must be positive")

    plants_query = select(AIPlant.name)
    plants_result = await db.execute(plants_query)
    db_classes = {row.name for row in plants_result}
    if not db_classes:
        raise ValueError("No classes found in database")

    if not os.path.exists(TRAIN_DIR):
        raise ValueError(f"Training directory {TRAIN_DIR} does not exist")
    
    train_classes = [d for d in os.listdir(TRAIN_DIR) if os.path.isdir(os.path.join(TRAIN_DIR, d))]
    if not train_classes:
        raise ValueError(f"No class directories found in {TRAIN_DIR}")
    
    for class_dir in train_classes:
        class_path = os.path.join(TRAIN_DIR, class_dir)
        images = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif', '.tiff', '.webp'))]
        if not images:
            raise ValueError(f"No valid images found in {class_path}")

    if not os.path.exists(VALID_DIR):
        raise ValueError(f"Validation directory {VALID_DIR} does not exist")
    
    valid_classes = [d for d in os.listdir(VALID_DIR) if os.path.isdir(os.path.join(VALID_DIR, d))]
    if not valid_classes:
        raise ValueError(f"No class directories found in {VALID_DIR}")
    
    for class_dir in valid_classes:
        class_path = os.path.join(VALID_DIR, class_dir)
        images = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif', '.tiff', '.webp'))]
        if not images:
            raise ValueError(f"No valid images found in {class_path}")

    if set(train_classes) != set(valid_classes):
        raise ValueError(f"Classes in {TRAIN_DIR} ({train_classes}) do not match classes in {VALID_DIR} ({valid_classes})")
    if set(train_classes) != db_classes:
        raise ValueError(f"Classes in {TRAIN_DIR} ({train_classes}) do not match classes in database ({db_classes})")

    task = start_training_task.delay(batch=batch, epoch=epoch, name_model=name_model)

    return {
        "message": "Training started",
        "task_id": task.id
    }

async def get_training_sessions(db: AsyncSession) -> List[dict]:
    num_classes_query = select(func.count(func.distinct(AIPlant.name)))
    num_classes_result = await db.execute(num_classes_query)
    num_classes = num_classes_result.scalar() or 0

    sessions_query = select(TrainingSession)
    sessions_result = await db.execute(sessions_query)
    sessions = sessions_result.scalars().all()

    response = []
    for session in sessions:
        last_epoch_query = (
            select(TrainingEpoch)
            .where(TrainingEpoch.training_session_id == session.id)
            .order_by(TrainingEpoch.epoch_num.desc())
            .limit(1)
        )
        last_epoch_result = await db.execute(last_epoch_query)
        last_epoch = last_epoch_result.scalar()

        response.append({
            "id": session.id,
            "model_name": session.model_name,
            "epochs": session.epochs,
            "num_classes": num_classes,
            "parameters": 20_000_000,  
            "train_accuracy": last_epoch.train_accuracy if last_epoch else 0.0,
            "created_at": session.created_at.isoformat()
        })

    return response

async def get_training_session_by_id(db: AsyncSession, session_id: int) -> Optional[dict]:
    num_classes_query = select(func.count(func.distinct(AIPlant.name)))
    num_classes_result = await db.execute(num_classes_query)
    num_classes = num_classes_result.scalar() or 0

    session_query = select(TrainingSession).where(TrainingSession.id == session_id)
    session_result = await db.execute(session_query)
    session = session_result.scalar()

    if not session:
        return None
    
    epochs_query = (
        select(TrainingEpoch)
        .where(TrainingEpoch.training_session_id == session.id)
        .order_by(TrainingEpoch.epoch_num.asc())
    )
    epochs_result = await db.execute(epochs_query)
    epochs = epochs_result.scalars().all()

    epochs_data = [
        {
            "epoch_num": epoch.epoch_num,
            "train_loss": epoch.train_loss,
            "train_accuracy": epoch.train_accuracy,
            "val_accuracy": epoch.val_accuracy
        }
        for epoch in epochs
    ]

    response = {
        "id": session.id,
        "model_name": session.model_name,
        "epochs": session.epochs,
        "batch_size": session.batch_size,
        "best_val_accuracy": session.best_val_accuracy,
        "num_classes": num_classes,
        "parameters": 20_000_000,
        "created_at": session.created_at.isoformat(),
        "epochs_data": epochs_data
    }

    return response