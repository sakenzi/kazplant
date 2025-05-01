from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from typing import List
from app.api.training.commands.training_crud import save_photos_and_trigger_training

router = APIRouter()

@router.post(
    "/train-model",
    summary="Обучение AI",
)
async def train_model_api(
    type_id: int = Form(...),
    plant_id: int = Form(...),
    epoch: int = Form(...),
    batch: int = Form(...),
    name_model: str = Form("resnet50"),
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    supported_models = ["resnet50", "resnet18", "vgg16"]  
    if name_model not in supported_models:
        raise HTTPException(status_code=400, detail=f"Unsupported model: {name_model}. Supported models: {supported_models}")
    
    return await save_photos_and_trigger_training(
        db=db,
        files=files,
        plant_id=plant_id,
        type_id=type_id,
        epoch=epoch,
        batch=batch,
        name_model=name_model
    )