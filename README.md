# kazplant

celery -A app.api.training.celery.celery_app worker --loglevel=debug --concurrency=1 --pool=solo