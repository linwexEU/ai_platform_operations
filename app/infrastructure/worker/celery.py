from celery import Celery

from app.domain.config import settings

app = Celery("tasks", broker=settings.REDIS_URL)
