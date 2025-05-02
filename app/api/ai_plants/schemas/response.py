from pydantic import BaseModel
from typing import Optional


class AIPlantsResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class AITypesResponse(BaseModel):
    id: int
    type_name: str

    class Config:
        from_attributes = True

class PlantPhotoInfo(BaseModel):
    plant_id: int
    plant_name: str
    random_photo: Optional[str] = None
    total_photos: int