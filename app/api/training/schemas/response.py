from pydantic import BaseModel
from typing import List


class TrainingSessionResponse(BaseModel):
    id: int
    model_name: str
    epochs: int
    num_classes: int
    parameters: int
    train_accuracy: float
    created_at: str

class EpochData(BaseModel):
    epoch_num: int
    train_loss: float
    train_accuracy: float
    val_accuracy: float

class TrainingSessionIDResponse(BaseModel):
    id: int
    model_name: str
    epochs: int
    batch_size: int
    best_val_accuracy: float
    num_classes: int
    parameters: int
    created_at: str
    epochs_data: List[EpochData]