from pydantic import BaseModel
from typing import Optional


class PlantResponse(BaseModel):
    name: str
    description: Optional[str] = None
    family: Optional[str] = None
    kingdom: Optional[str] = None

    class Config:
        from_attributes = True