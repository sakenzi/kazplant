from pydantic import BaseModel


class PlantQuestionResponse(BaseModel):
    answer: str