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

from datetime import datetime,  timedelta

from django.urls import reverse
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
RUNNING_STATES = ('QUEUED', 'RUNNING', 'SUBMITTING')


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
      DataEng(self.user).terminate_job(job_id=job_id)
      response = {'status': 0}
    else:
      response = {'status': -1, 'message': _('Could not cancel because of unsuccessful submition.')}

    return response


  def get_log(self, notebook, snippet, startFrom=0, size=None):
    logs = WorkfloadAnalyticsClient(self.user).get_mr_task_attempt_log(
        operation_execution_id='cedb71ae-0956-42e1-8578-87b9261d4a37',
        attempt_id='attempt_1499705340501_0045_m_000000_0'
    )

    return ''.join(re.findall('(?<=>>> Invoking Beeline command line now >>>)(.*?)(?=<<< Invocation of Beeline command completed <<<)', logs['stdout'], re.DOTALL))


  def progress(self, snippet, logs):
    return 50


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


  def close_statement(self, snippet):
    pass


  def close_session(self, session):
    pass


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
