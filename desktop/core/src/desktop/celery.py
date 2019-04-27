from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

from desktop.settings import TIME_ZONE
from desktop.conf import TASK_SERVER


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desktop.settings')

app = Celery('desktop')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = TIME_ZONE

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
  print('Request: {0!r}'.format(self.request))
  return 'Hello'

#
if TASK_SERVER.BEAT_ENABLED.get():
  app.conf.beat_schedule = {
    'add-every-monday-morning': {
      'task': 'desktop.celery.debug_task',
      'schedule': crontab(minute='*'),
      # 'schedule': crontab(hour=7, minute=30, day_of_week=1),
      #'args': (16, 16),
    },
  }
