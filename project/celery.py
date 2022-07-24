from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('proj')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))



app.conf.beat_schedule = {
    'check-if-new-visit': {
        'task': 'check-if-new-visit',
        'schedule': crontab(hour=7, minute=30),
        'args': ()
    },
    'check-if-visit_finished': {
        'task': 'check-if-visit_finished',
        'schedule': 300.0,
        'args': ()
    },
}