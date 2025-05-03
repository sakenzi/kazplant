from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DiseaseOut(BaseModel):
    id: int
    name: str
    treatment: str
    prevention: str

    class Config:
        from_attributes = True

class LeafOut(BaseModel):
    id: int
    photo: str
    created_at: datetime
    user_id: Optional[int]

    class Config:
        from_attributes = True

class LeafDiseaseResponse(BaseModel):
    id: int
    leaf: LeafOut
    disease: DiseaseOut

    class Config:
        from_attributes = True

class SegmentationResult(BaseModel):
    infection_ratio: float
    infection_level: str