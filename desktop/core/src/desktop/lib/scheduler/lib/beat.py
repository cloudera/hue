
from desktop.lib.scheduler.lib.base import Api


class CeleryBeatApi(Api):

  def __init__(self, user=None):
    pass


from celery.schedules import crontab
from desktop.celery import app

app.conf.beat_schedule = {
  'add-every-monday-morning': {
    'task': 'desktop.celery.debug_task',
    'schedule': crontab(minute='*/15'),
    # 'schedule': crontab(hour=7, minute=30, day_of_week=1),
    #'args': (16, 16),
  },
}
