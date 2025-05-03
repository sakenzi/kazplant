import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from model.model import Segmentation, SegmentationPhoto, SegmentationType
from app.api.segmentations.schemas.response import SegmentationPhotoInfo
from typing import List


async def get_segmentations_by_type_id(db: AsyncSession, type_id: int, limit: int = 10) -> List[SegmentationPhotoInfo]:
    type_exists = await db.execute(select(SegmentationType).where(SegmentationType.id == type_id))
    if not type_exists.scalars().first():
        raise HTTPException(status_code=404, detail=f"Segmentation type with ID {type_id} not found")
    
    result = await db.execute(
        select(Segmentation)
        .join(SegmentationPhoto, SegmentationPhoto.segmentation_id == Segmentation.id)
        .where(SegmentationPhoto.segmentation_type_id == type_id)
        .options(selectinload(Segmentation.segmentation_photos))
        .group_by(Segmentation.id)
        .limit(limit)
    )
    segmentations = result.scalars().all()

    segmentation_data = []

    for segmentation in segmentations:
        photos = [photo for photo in segmentation.segmentation_photos if photo.segmentation_type_id == type_id]
        total_photos = len(photos)
        random_photo = None
        random_mask = None

        if total_photos > 0:
            random_photo_obj = random.choice(photos)
            random_photo = random_photo_obj.photo
            random_mask = random_photo_obj.mask_path

        segmentation_data.append(SegmentationPhotoInfo(
            segmentation_id=segmentation.id,
            type_id=type_id,
            name_data=segmentation.name_data,
            random_photo=random_photo,
            random_mask=random_mask,
            total_photos=total_photos
        ))

    return segmentation_data