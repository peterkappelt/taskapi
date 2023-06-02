import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskapi_backend.settings")

app = Celery("taskapi_backend")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "notion_schedule": {
        "task": "dispatch_notion_observers",
        "schedule": 30,
    },
    "g_tasks_schedule": {
        "task": "dispatch_g_tasks_observers",
        "schedule": 30,
    },
}
