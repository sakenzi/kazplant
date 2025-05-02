from pydantic import BaseModel


class TrainingSessionResponse(BaseModel):
    id: int
    model_name: str
    epochs: int
    num_classes: int
    parameters: int
    train_accuracy: float
    created_at: str