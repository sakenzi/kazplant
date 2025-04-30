from pydantic import BaseModel


class PlantQuestionCreate(BaseModel):
    plant_id: int
    question: str

