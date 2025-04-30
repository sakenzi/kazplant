from model.model import Plant
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
import g4f
from app.api.questions.commands.prompt_g4f import build_prompt


async def ask_about_plant(plant_id: int, question: str, db: AsyncSession) -> str:
    stmt = select(Plant).where(Plant.id == plant_id)
    result = await db.execute(stmt)
    plant = result.scalars().first()

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    prompt = build_prompt(plant, question)

    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        if isinstance(response, dict):
            return response.get("response", "Ошибка: пустой ответ от G4F")
        return str(response)

    except Exception as e:
        raise HTTPException(status_code=500, detail="G4F request failed")
