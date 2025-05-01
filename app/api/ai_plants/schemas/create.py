from pydantic import BaseModel
from typing import Optional


class AiPlantCreate(BaseModel):
    name: str