from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Photo(BaseModel):
    id: int
    photo: str

    class Config:
        from_attributes = True

class PlantResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    probability: float
    family: Optional[str] = None
    kingdom: Optional[str] = None
    photos: List[Photo]

    class Config:
        from_attributes = True

class PlantIDResponse(BaseModel):
    id: int
    name: str
    description: str
    probability: float
    family: str
    kingdom: str
    created_at: datetime
    photos: List[Photo] = []

    class Config:
        from_attributes = True