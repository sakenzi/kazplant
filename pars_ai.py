import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from model.model import AIType, AIPlant, AIPhoto
from database.db import async_session_factory  
import asyncio

BASE_DIR = "new_plant/New Plant Diseases Dataset(Augmented)"  

async def insert_dataset(session: AsyncSession):
    for dataset_type in ["train", "valid"]:
        dataset_path = os.path.join(BASE_DIR, dataset_type)

        result = await session.execute(select(AIType).where(AIType.type_name == dataset_type))
        ai_type = result.scalar_one_or_none()
        if not ai_type:
            ai_type = AIType(type_name=dataset_type)
            session.add(ai_type)
            await session.flush()

        for plant_folder in os.listdir(dataset_path):
            plant_path = os.path.join(dataset_path, plant_folder)
            if not os.path.isdir(plant_path):
                continue

            result = await session.execute(select(AIPlant).where(AIPlant.name == plant_folder))
            ai_plant = result.scalar_one_or_none()
            if not ai_plant:
                ai_plant = AIPlant(name=plant_folder)
                session.add(ai_plant)
                await session.flush()

            for photo_name in os.listdir(plant_path):
                photo_path = os.path.join(plant_path, photo_name)
                relative_path = os.path.relpath(photo_path, BASE_DIR)  

                photo = AIPhoto(
                    photo=relative_path.replace("\\", "/"),  
                    ai_plant_id=ai_plant.id,
                    ai_type_id=ai_type.id
                )
                session.add(photo)

        await session.commit()
    print("Загрузка завершена.")

async def main():
    async with async_session_factory() as session:
        await insert_dataset(session)

if __name__ == "__main__":
    asyncio.run(main())
