from celery import Celery

celery = Celery(
    "kazplant_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.api.training.celery.tasks"]
)
