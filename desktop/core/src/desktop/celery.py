#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, unicode_literals
from __future__ import print_function

import imp
import os

from celery import Celery
from celery.schedules import crontab

from desktop.conf import TASK_SERVER
from desktop.settings import TIME_ZONE, INSTALLED_APPS


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


if 'django_celery_beat' in INSTALLED_APPS and False: # Config not available yet
  app.conf.beat_schedule = {}

  if TASK_SERVER.BEAT_SCHEDULES_FILE.get():
    schedules = imp.load_source('schedules', TASK_SERVER.BEAT_SCHEDULES_FILE.get())

    for schedule in schedules.periodic_tasks:
      app.conf.beat_schedule.update(schedule)
