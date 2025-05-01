from app.api.training.celery.celery_app import celery
from app.api.training.train.train_utils import train_model_script
from database.db import SessionLocal

@celery.task
def start_training_task(batch: int, epoch: int, name_model: str):
    db = SessionLocal()
    try:
        print(f"Starting training with batch {batch} and epoch {epoch}, model {name_model}")
        train_model_script(batch_size=batch, num_epochs=epoch, db=db, name_model=name_model)
    finally:
        db.close()