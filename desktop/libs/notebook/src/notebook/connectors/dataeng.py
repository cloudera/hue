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

import logging
import re

from django.urls import reverse
from django.utils.translation import ugettext as _

from metadata.workload_analytics_client import WorkfloadAnalyticsClient

from notebook.connectors.altus import DataEngApi as AltusDataEngApi
from notebook.connectors.base import Api, QueryError
from jobbrowser.apis.data_eng_api import RUNNING_STATES


LOG = logging.getLogger(__name__)


class DataEngApi(Api):

  def __init__(self, user, cluster_name, interpreter=None, request=None):
    Api.__init__(self, user, interpreter=interpreter, request=request)
    self.cluster_name = cluster_name


  def execute(self, notebook, snippet):

    if snippet['type'] == 'spark2':
      handle = AltusDataEngApi(self.user).submit_spark_job(
          cluster_name=self.cluster_name,
          jars=snippet['properties']['jars'],
          main_class=snippet['properties']['class'],
          arguments=snippet['properties']['spark_arguments'],
          spark_arguments=snippet['properties']['spark_opts'],
#           properties_file
      )
    else:
      statement = snippet['statement']
      handle = AltusDataEngApi(self.user).submit_hive_job(self.cluster_name, statement, params=None, job_xml=None)

    if 'jobs' not in handle:
      raise QueryError('Submission failure: %s' % handle)

    job = handle['jobs'][0]

    if job['status'] not in RUNNING_STATES:
      raise QueryError('Submission failure', handle=job['status'])

    return {
      'id': job['jobId'],
      'crn': job['crn'],
      'has_result_set': False,
    }


  def check_status(self, notebook, snippet):
    response = {'status': 'running'}

    job_id = snippet['result']['handle']['id']

    handle = AltusDataEngApi(self.user).list_jobs(job_ids=[job_id])
    job = handle['jobs'][0]

    if job['status'] in RUNNING_STATES:
      return response
    elif job['status'] in ('failed', 'terminated'):
      raise QueryError(_('Job was %s') % job['status'])
    else:
      response['status'] = 'available'

    return response


  def fetch_result(self, notebook, snippet, rows, start_over):
    return {
        'data':  [[_('Job successfully completed.')]],
        'meta': [{'name': 'Header', 'type': 'STRING_TYPE', 'comment': ''}],
        'type': 'table',
        'has_more': False,
    }


  def cancel(self, notebook, snippet):
    if snippet['result']['handle'].get('id'):
      job_id = snippet['result']['handle']['id']
      AltusDataEngApi(self.user).terminate_job(job_id=job_id)
      response = {'status': 0}
    else:
      response = {'status': -1, 'message': _('Could not cancel because of unsuccessful submission.')}

    return response


  def get_log(self, notebook, snippet, startFrom=0, size=None):
    # Currently no way to get the logs properly easily

    # logs = WorkfloadAnalyticsClient(self.user).get_mr_task_attempt_log(
    #    operation_execution_id='cedb71ae-0956-42e1-8578-87b9261d4a37',
    #    attempt_id='attempt_1499705340501_0045_m_000000_0'
    # )
    # return ''.join(re.findall('(?<=>>> Invoking Beeline command line now >>>)(.*?)(?=<<< Invocation of Beeline command completed <<<)', logs['stdout'], re.DOTALL))
    return ''


  def get_jobs(self, notebook, snippet, logs):
    ## 50cf0e00-746b-4d86-b8e3-f2722296df71
    job_id = snippet['result']['handle']['id']
    return [{
        'name': job_id,
        'url': reverse('jobbrowser.views.apps') + '#!' + job_id,
        'started': True,
        'finished': False # Would need call to check_status
      }
    ]


  def close_statement(self, notebook, snippet):
    pass


  def close_session(self, session):
    pass
