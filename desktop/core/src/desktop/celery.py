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
if hasattr(TASK_SERVER, 'get') and TASK_SERVER.ENABLED.get():
  from desktop.settings import CELERY_RESULT_BACKEND, CELERY_BROKER_URL
from django.utils import timezone

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desktop.settings')

class HueCelery(Celery):
  def gen_task_name(self, name, module):
    if module.endswith('.tasks'):
      module = module[:-6]
    return super().gen_task_name(name, module)

  # Method to configure the beat_schedule
  def setup_beat_schedule(self):
    now = timezone.now()

    self.conf.beat_schedule = {
      'check_disk_usage_and_clean_task': {
      'task': 'filebrowser.check_disk_usage_and_clean_task',
      'schedule': 1000.0,  # Run every 1000 seconds
      'args': (),
      'kwargs': {'cleanup_threshold': 90},  # Provide task arguments if needed
      },
    }

if hasattr(TASK_SERVER, 'get') and TASK_SERVER.ENABLED.get():
  app = HueCelery('desktop', backend=CELERY_RESULT_BACKEND, broker=CELERY_BROKER_URL)
  app.conf.broker_transport_options = {'visibility_timeout': 3600}  # 1 hour.
  app.conf.result_key_prefix = 'desktop_'

  # Call the setup_beat_schedule method
  app.setup_beat_schedule()

  # Using a string here means the worker doesn't have to serialize
  # the configuration object to child processes.
  # - namespace='CELERY' means all celery-related configuration keys
  #   should have a `CELERY_` prefix.
  app.config_from_object('django.conf:settings', namespace='CELERY')
  app.conf.timezone = TIME_ZONE

  # Load task modules from all registered Django app configs.
  app.autodiscover_tasks()

else:
  app = Celery('desktop')
  app.config_from_object('django.conf:settings', namespace='CELERY')
  app.conf.timezone = TIME_ZONE
  app.autodiscover_tasks()
