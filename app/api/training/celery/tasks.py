from app.api.training.celery.celery_app import celery
from app.api.training.train.train_utils import train_model_script

@celery.task
def start_training_task(batch: int, epoch: int):
    print(f"Starting training with batch {batch} and epoch {epoch}")
    train_model_script(batch=batch, num_epochs=epoch)