import os
import shutil
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from model.model import AIPhoto, AIPlant, AIType, TrainingSession, TrainingEpoch
from fastapi import UploadFile
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

    if not os.path.exists(TRAIN_DIR) or not os.listdir(TRAIN_DIR):
        raise ValueError(f"No training data found in {TRAIN_DIR}")

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