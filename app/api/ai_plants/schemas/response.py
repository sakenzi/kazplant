from pydantic import BaseModel


class AIPlantsResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class AITypesResponse(BaseModel):
    id: int
    type_name: str