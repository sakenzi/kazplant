from pydantic import BaseModel
from typing import Optional, List


class AiPlantCreate(BaseModel):
    name: str


class UploadPhotosResponse(BaseModel):
    photo_count: int
    saved_paths: List[str]