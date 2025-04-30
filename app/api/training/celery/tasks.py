from .worker import celery_app


@celery_app.task
def hello_world():
    return 'Hello from Celery!'