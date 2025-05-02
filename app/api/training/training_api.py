from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from typing import List
from app.api.training.commands.training_crud import save_photos_and_trigger_training, get_training_sessions, get_training_session_by_id
from app.api.training.schemas.response import TrainingSessionResponse, TrainingSessionIDResponse


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

@router.get(
    "/get-training_sessions",
    summary="Получить информацию о тренировочных сессиях",
    response_model=List[TrainingSessionResponse]
)
async def get_training_sessions_api(db: AsyncSession = Depends(get_db)):
    try:
        sessions = await get_training_sessions(db)
        return [TrainingSessionResponse(**session) for session in sessions]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@router.get(
    "/training-sessions/{id}",
    response_model=TrainingSessionIDResponse,
    summary="Получить информацию о тренировочной сессии по ID",
)
async def get_training_session_by_id_api(id: int, db: AsyncSession = Depends(get_db)):
    try:
        session = await get_training_session_by_id(db, id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Training session with ID {id} not found")
        return TrainingSessionIDResponse(**session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")