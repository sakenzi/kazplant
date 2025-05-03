from pydantic import BaseModel
from typing import Optional


class SegmentationPhotoInfo(BaseModel):
    segmentation_id: int
    type_id: Optional[int] = None
    name_data: str
    random_photo: Optional[str] = None
    random_mask: Optional[str] = None
    total_photos: int

class SegmentationsResponse(BaseModel):
    id: int
    name_data: str

class SegmentationTypesResponse(BaseModel):
    id: int
    type_name: str