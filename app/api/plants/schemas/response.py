from pydantic import BaseModel
from typing import Optional, List


class Photo(BaseModel):
    id: int
    photo: str

    class Config:
        from_attributes = True

class PlantResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    family: Optional[str] = None
    kingdom: Optional[str] = None
    photos: List[Photo]

    class Config:
        from_attributes = True