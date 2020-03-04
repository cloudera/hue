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
    # IntervalSchedule is buggy https://github.com/celery/django-celery-beat/issues/279
    is_cron = True

    # Assumes SQL queries currently
    document = Document2.objects.get(uuid=coordinator.get_data_for_json()['properties']['document'])

    schedule_properties = {
        'name': 'Scheduled document %(user)s %(uuid)s' % {
        'user': request.user.username,
        'uuid': document.uuid
        },
        'description': request.user.username, # Owner
        'task': 'notebook.tasks.run_sync_query',
        'defaults': {"args": json.dumps([document.uuid, request.user.username])},
    }

    if is_cron:
      schedule, created = CrontabSchedule.objects.get_or_create(
          minute='*',
          hour='*',
          day_of_week='*',
          day_of_month='*',
          month_of_year='*'
      )
      schedule_properties['crontab'] = schedule
    else:
      schedule, created = IntervalSchedule.objects.get_or_create(
        every=15,
        period=IntervalSchedule.SECONDS,
      )
      schedule_properties['interval'] = schedule

    task = PeriodicTask.objects.update_or_create(**schedule_properties)
    task.enabled=True
    task.save()

    return task.id


  def list_tasks(self, user):
    return [
      self._get_task(task)
      for task in PeriodicTask.objects.filter(description=user.username)
    ]

  def list_task(self, task_id):
    return self._get_task(PeriodicTask.objects.get(id=task_id))


  def action(self, schedule_id, action='suspend'):
    task = PeriodicTask.objects.get(id=schedule_id, description=self.user.username)

    if action == 'suspend':
      task.enabled = False
      task.save()
    elif action == 'resume':
      task.enabled = True
      task.save()
    elif action == 'kill':
      task.delete()


  def _get_task(self, task):
    return {
        'id': task.id,
        'name': task.name,
        'description': task.description,
        'task_name': task.name,
        'task_id': task.id,
        'args': task.args,
        'kwargs': task.kwargs,
        'queue': task.queue,
        'exchange': task.exchange,
        'routing_key': task.routing_key,
        'priority': task.priority,
        'expires': task.expires,
        'one_off': task.one_off,
        'start_time': task.start_time,
        'enabled': task.enabled,
        'last_run_at': task.last_run_at,
        'total_run_count': task.total_run_count,
        'date_changed': task.date_changed,
        'interval_name': task.interval,
        'crontab': task.crontab,
        'solar': task.solar
    }
