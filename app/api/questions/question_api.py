from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from database.db import get_db
from app.api.questions.commands.question_crud import ask_about_plant
from app.api.questions.schemas.create import PlantQuestionCreate
from app.api.questions.schemas.response import PlantQuestionResponse


router = APIRouter()

@router.post(
    "/plant/ask",
    summary="Задать вопрос о растении",
    response_model=PlantQuestionResponse
)
async def ask_plant_info(request: PlantQuestionCreate, db: AsyncSession = Depends(get_db)):
    answer = await ask_about_plant(request.plant_id, request.question, db)
    return PlantQuestionResponse(answer=answer)