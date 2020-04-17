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

from notebook.models import make_notebook, MockRequest

from desktop.lib.scheduler.lib.api import Api
from desktop.models import Document2


class HiveSchedulerApi(Api):
  """
  * create
  create scheduled query sc1 cron '0 */10 * * * ? *' as select 1

  * change schedule
  alter scheduled query Q1 cron '2 2 * * *'

  * change query
  alter scheduled query Q1 defined as select 2

  * disable
  alter scheduled query Q1 set disabled

  * enable
  alter scheduled query Q1 set enabled

  * list status
  select * from information_schema.scheduled_queries;

  * drop
  drop scheduled query Q1
  """

  def submit_schedule(self, request, coordinator, mapping):
    """
    coordinator
      Document2.objects.get(uuid=coordinator.get_data_for_json()['properties']['document'])

    mapping
      {u'oozie.use.system.libpath': u'True', 'dryrun': False, u'start_date': u'2019-08-10T17:02', u'end_date': u'2019-08-17T17:02'}
    """

    document = Document2.objects.get(uuid=coordinator.get_data_for_json()['properties']['document'])  # Assumes Hive SQL queries

    # (schedule_name,cluster_namespace) is unique
    #_get_snippet_name(notebook) --> name

    properties = {
      'name': 'query-%(uuid)s' % {
        'uuid': document.uuid
      },
      'username': request.user.username
    }

    sql_query = """
    CREATE SCHEDULED QUERY %(name)s
    CRON '1 1 * * *' AS
    SELECT 1
    """ % properties

    job = make_notebook(
        name=properties['name'],
        editor_type='hive',
        statement=sql_query,
        status='ready',
        database='default',
        is_task=False,
    )
    handle = job.execute_and_wait(request)

    return handle['history_uuid']


  def list_tasks(self, user):
    sql_query = "SELECT * FROM information_schema.scheduled_queries"

    job = make_notebook(
        name='List Hive schedules',
        editor_type='hive',
        statement=sql_query,
        status='ready',
        database='default',
        is_task=False,
    )
    request = MockRequest(user)

    handle = job.execute_and_wait(request, include_results=True)

    return [
      self._get_task(row) for row in handle['result']['data']
    ]


  def list_executed_tasks(self, app_id):
    sql_query = """
SELECT scheduled_executions.*
FROM information_schema.scheduled_executions
JOIN information_schema.scheduled_queries ON scheduled_queries.schedule_name = scheduled_executions.schedule_name
where scheduled_query_id = %(scheduled_query_id)s
LIMIT 100""" % {
      'scheduled_query_id': app_id
    }

    job = make_notebook(
        name='List Hive scheduled execution',
        editor_type='hive',
        statement=sql_query,
        status='ready',
        database='default',
        is_task=False,
    )
    request = MockRequest(self.user)

    handle = job.execute_and_wait(request, include_results=True)

    return [
        {
        'scheduled_execution_id': row[0],
        'schedule_name': row[1],
        'executor_query_id': row[2],
        'state': row[3],
        'start_time': row[4],
        'end_time': row[5],
        'elapsed': row[6],
        'error_message': row[7],
        'last_update_time': row[8],
      } for row in handle['result']['data']
    ]

  def list_task(self, task_id):
    task_id = task_id.replace('schedule-hive-', '')

    sql_query = """
    SELECT * FROM information_schema.scheduled_queries
    WHERE scheduled_query_id = %(scheduled_query_id)s
    """ % {
      'scheduled_query_id': task_id
    }

    job = make_notebook(
        name='List Hive schedule id',
        editor_type='hive',
        statement=sql_query,
        status='ready',
        database='default',
        is_task=False,
    )
    request = MockRequest(self.user)

    handle = job.execute_and_wait(request, include_results=True)

    return self._get_task(handle['result']['data'][0])


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


  def _get_task(self, row):
    return {
      'scheduled_query_id': row[0],
      'schedule_name': row[1],
      'enabled': row[2],
      'cluster_namespace': row[3],
      'schedule': row[4],
      'user': row[5],
      'query': row[6],
      'next_execution': row[7],
      'active_execution_id': row[8],
    }
