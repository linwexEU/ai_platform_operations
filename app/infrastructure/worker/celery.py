from celery import Celery

from app.domain.core.config import settings

app = Celery("tasks", broker=settings.REDIS_URL)

# Register tasks
app.conf.imports = (
    "app.entrypoints.tasks.auth",
    "app.entrypoints.tasks.document"
)
