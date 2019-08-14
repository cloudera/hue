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

import json

from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule

from desktop.lib.scheduler.lib.api import Api
from desktop.models import Document2


class CeleryBeatApi(Api):

  def submit_schedule(self, request, coordinator, mapping):
    '''
    coordinator
      Document2.objects.get(uuid=coordinator.get_data_for_json()['properties']['document'])

    mapping
      {u'oozie.use.system.libpath': u'True', 'dryrun': False, u'start_date': u'2019-08-10T17:02', u'end_date': u'2019-08-17T17:02'}
    '''
    is_cron = True # IntervalSchedule is buggy https://github.com/celery/django-celery-beat/issues/279

    # Assumes SQL queries currently
    document = Document2.objects.get(uuid=coordinator.get_data_for_json()['properties']['document'])

    if is_cron:
      schedule, created = CrontabSchedule.objects.get_or_create(
          minute='*',
          hour='*',
          day_of_week='*',
          day_of_month='*',
          month_of_year='*'
      )

      task = PeriodicTask.objects.update_or_create(
        crontab=schedule,
        name='Scheduled document %(user)s %(uuid)s' % {
          'user': request.user.username,
          'uuid': document.uuid
        },
        description=request.user.username, # Owner
        task='notebook.tasks.run_sync_query',
        defaults={"args": json.dumps([document.uuid, request.user.username])},
      )
      task.enabled=True
      task.save()
    else:
      schedule, created = IntervalSchedule.objects.get_or_create(
        every=15,
        period=IntervalSchedule.SECONDS,
      )

      task, created = PeriodicTask.objects.update_or_create(
        interval=schedule,
        name='Scheduled query',
        task='notebook.tasks.run_sync_query',
      )


  def list_schedules(self, user):
    PeriodicTask.objects.filter(description=user.username)


  def action(self, schedule_id, schedule_ids=None, action='pause'):
    if schedule_ids is None:
      schedule_ids = [schedule_id]

    task = PeriodicTask.objects.get(id__in=schedule_ids, description=user.username)

    if action == 'pause':
      task.enabled = False
      task.saved()
    elif action == 'resume':
      task.enabled = False
      task.saved()
    elif action == 'delete':
      task.delete()
