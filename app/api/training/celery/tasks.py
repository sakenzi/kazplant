from app.api.training.celery.celery_app import celery
from app.api.training.train.train_utils import train_model_script
from database.db import SessionLocal

@celery.task
def start_training_task(batch: int, epoch: int):
    db = SessionLocal()
    try:
        print(f"Starting training with batch {batch} and epoch {epoch}")
        train_model_script(batch_size=batch, num_epochs=epoch, db=db)
    finally:
        db.close()