from sqlalchemy.ext.asyncio import AsyncSession
from model.model import PlantPhoto
from typing import List


async def save_photos_to_db(paths: List[str], db: AsyncSession) -> List[int]:
    saved_ids = []

    for path in paths:
        photo = PlantPhoto(photo=path)
        db.add(photo)
        await db.flush()
        saved_ids.append(photo.id)

    await db.commit()
    return saved_ids