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
import json
import re
import subprocess
import time

from datetime import datetime,  timedelta

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from metadata.workload_analytics_client import WorkfloadAnalyticsClient

from notebook.connectors.base import Api, QueryError


LOG = logging.getLogger(__name__)


def _exec(args):
  try:
    data = subprocess.check_output([
        'altus',
        'dataeng',
       ] +
       args
    )    
  except Exception, e:
    raise PopupException(e, title=_('Error accessing'))

  response = json.loads(data)

  return response

DATE_FORMAT = "%Y-%m-%d"
RUNNING_STATES = ('queued', 'running', 'submitting', 'QUEUED', 'RUNNING', 'SUBMITTING')


class DataEngApi(Api):

  def __init__(self, user, cluster_name, interpreter=None, request=None):
    Api.__init__(self, user, interpreter=interpreter, request=request)
    self.cluster_name = cluster_name


  def execute(self, notebook, snippet):
    statement = snippet['statement']

    handle = DataEng(self.user).submit_hive_job(self.cluster_name, statement, params=None, job_xml=None)
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

    handle = DataEng(self.user).list_jobs(job_ids=[job_id])

    job = handle['jobs'][-1]
    job['status'] = job['status'].lower()

    print '================'
    print job['status']
    print handle

    if job['status'] in RUNNING_STATES:
      return response
    elif job['status'] in ('failed', 'terminated'):
      raise QueryError(_('Job was %s') % job['status'])
    else:
      response['status'] = 'available'

    return response


  def fetch_result(self, notebook, snippet, rows, start_over):
    n = 20
    result_rows = None

    while n > 0 and not result_rows:
      operation_execution_id = snippet['result']['handle']['id']
      logs = _get_main_task_id(self.user, operation_execution_id=operation_execution_id)
  #     logs = WorkfloadAnalyticsClient(self.user).get_mr_task_attempt_log(
  #         operation_execution_id='cedb71ae-0956-42e1-8578-87b9261d4a37',
  #         attempt_id='attempt_1499705340501_0045_m_000000_0'
  #     )
      result_rows = re.findall('(?<=>>> Invoking Beeline command line now >>>)(.*?)(?=<<< Invocation of Beeline command completed <<<)', logs['stdout'], re.DOTALL)
      if result_rows: 
        result_rows = [[row] for row in result_rows[0].splitlines()]
      else:
        n -= 1
        time.sleep(3)
    
    if not result_rows:
      result_rows = [[_('Job successfully completed.')]]

    return {
        'data': result_rows,
        'meta': [{'name': 'Header', 'type': 'STRING_TYPE', 'comment': ''}],
        'type': 'table',
        'has_more': False,
    }


  def cancel(self, notebook, snippet):
    if snippet['result']['handle'].get('id'):
      job_id = snippet['result']['handle']['id']
      DataEng(self.user).terminate_job(job_id=job_id)
      response = {'status': 0}
    else:
      response = {'status': -1, 'message': _('Could not cancel because of unsuccessful submittion.')}

    return response


  def get_log(self, notebook, snippet, startFrom=0, size=None):
    operation_execution_id = snippet['result']['handle']['id']
    logs = _get_main_task_id(self.user, operation_execution_id=operation_execution_id)

    return ''.join(re.findall('(?<=Oozie Launcher starts)(.*?)(?=Oozie Launcher ends)', logs['stdout'], re.DOTALL))


  def progress(self, snippet, logs):
    return 50


  def get_jobs(self, notebook, snippet, logs):
    job_id = snippet['result']['handle']['id']
    return [{
        'name': job_id,
        'url': reverse('jobbrowser.views.apps') + '#!' + job_id,
        'started': True,
        'finished': False # Would need call to check_status
      }
    ]


  def close_statement(self, snippet):
    pass


  def close_session(self, session):
    pass


def _get_main_task_id(user, operation_execution_id):
  client = WorkfloadAnalyticsClient(user)
  # altus wa get-operation-execution-details --id 8d460694-01af-4aa5-be53-83fbf562019d --include-tree
  # altus wa get-mr-task-attempt-log --operation-execution-id 6bc2b3e4-1a7d-4fb5-9371-df8d2a463b1d  --attempt-id attempt_1500482619800_0011_m_000000_0
  
#  >>> b['tree']['children'][0]['displayName']
# u'job_1500482619800_0011'
# >>> b['tree']['children'][0]['children'][0]['id']
# u'6bc2b3e4-1a7d-4fb5-9371-df8d2a463b1d'
  if operation_execution_id == '80358a87-e5f7-1ae5-c8f2-2f6596b8e268':
    operation_execution_id = '8d460694-01af-4aa5-be53-83fbf562019d'

  try:
    ops = client.get_operation_execution_details(operation_execution_id)
    
    job_id = ops['tree']['children'][0]['displayName']
    task_attempt_id = job_id.replace('job_', 'attempt_') + '_m_000000_0'
    operation_execution_id = ops['tree']['children'][0]['children'][0]['id']
    
    return WorkfloadAnalyticsClient(user).get_mr_task_attempt_log(
        operation_execution_id=operation_execution_id,
        attempt_id=task_attempt_id
    )
  except Exception, e:
    print 'operation id maybe just not available yet'
    print e
    LOG.exception(e)
    return {'stdout': 'Job is running or logs are being uploaded...'}


class DataEng():

  def __init__(self, user): pass

  def list_jobs(self, submitter_crns=None, page_size=None, starting_token=None, job_statuses=None, job_ids=None, job_types=None, creation_date_before=None,
        creation_date_after=None, cluster_crn=None, order=None):
    args = ['list-jobs']

    if creation_date_after is None:
      creation_date_after = (datetime.today() - timedelta(days=7)).strftime(DATE_FORMAT)

    if submitter_crns:
      args.extend(['--submitter-crns', submitter_crns])
    if page_size is not None:
      args.extend(['--page-size', str(page_size)])
    if starting_token:
      args.extend(['--starting-token', starting_token])
    if job_statuses:
      args.extend(['--job-statuses', job_statuses])
    if job_ids:
      args.extend(['--job-ids'] + job_ids)
    if job_types:
      args.extend(['--job-types', job_types])
    if creation_date_before:
      args.extend(['--creation-date-before', creation_date_before])
    if creation_date_after:
      args.extend(['--creation-date-after', creation_date_after])
    if cluster_crn:
      args.extend(['--cluster-crn', cluster_crn])
    if order:
      args.extend(['--order', order])

    return _exec(args)

  def describe_job(self, job_id):
    args = ['describe-job', '--job-id', job_id]

    return _exec(args)

  def submit_hive_job(self, cluster_name, script, params=None, job_xml=None):
    job = {'script': script}

    if params:
      job['params'] =  params
    if job_xml:
      job['jobXml'] =  job_xml

    return self.submit_jobs(cluster_name, [{'hiveJob': job}])

  def submit_spark_job(self):
    return _exec(['submit-jobs'])

  def submit_yarn_job(self):
    return _exec(['submit-jobs'])

  def submit_jobs(self, cluster_name, jobs):
    return _exec(['submit-jobs', '--cluster-name', cluster_name, '--jobs', json.dumps(jobs)])

  def terminate_job(self, job_id):
    return _exec(['terminate-job', '--job-id', job_id])


  def list_clusters(self, names=None, page_size=None, starting_token=None):
    args = ['list-clusters']

    if names:
      args.extend(['--cluster-names', names])
    if page_size is not None:
      args.extend(['--page-size', str(page_size)])
    if starting_token:
      args.extend(['--starting-token', starting_token])

    return _exec(args)

  def create_cluster(self):
    return _exec(['create-cluster'])

  def delete_cluster(self):
    return _exec(['delete-cluster'])

  def describe_clusters(self):
    return _exec(['describe-cluster'])
