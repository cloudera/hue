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
import subprocess

from datetime import datetime,  timedelta

from django.urls import reverse
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)

DATE_FORMAT = "%Y-%m-%d"


def _exec(command, args):
  try:
    data = subprocess.check_output([
        'altus',
        command,
       ] +
       args
    )
  except Exception, e:
    raise PopupException(e, title=_('Error accessing'))

  response = json.loads(data)

  return response


class IAMApi(): pass
# altus iam list-user-assigned-roles --user=crn:altus:ia


class SdxApi():

  def __init__(self, user): pass

  def list_namespaces(self):
    """
    e.g. returns
    [{
      u'status': u'CREATED',
      u'namespaceName': u'cca-5150-ns',
      u'creationDate': u'2018-06-03T23:24:46.125000+00:00',
      u'crn': u'crn:altus:sdx:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:namespace:cca-5150-ns/f54461af-b241-4f1d-a521-ab3624e841c4'},
      ...
    ]
    """

    args = ['list-namespaces']
    return _exec('sdx', args)['namespaces']


class DataEngApi():

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

    return _exec('dataeng', args)

  def describe_job(self, job_id):
    args = ['describe-job', '--job-id', job_id]

    return _exec('dataeng', args)

  def submit_hive_job(self, cluster_name, script, params=None, job_xml=None):
    job = {'script': script}

    if params:
      job['params'] =  params
    if job_xml:
      job['jobXml'] =  job_xml

    return self.submit_jobs(cluster_name, [{'hiveJob': job}])

  def submit_spark_job(self):
    return _exec('dataeng', ['submit-jobs'])

  def submit_yarn_job(self):
    return _exec('dataeng', ['submit-jobs'])

  def submit_jobs(self, cluster_name, jobs):
    return _exec('dataeng', ['submit-jobs', '--cluster-name', cluster_name, '--jobs', json.dumps(jobs)])

  def terminate_job(self, job_id):
    return _exec('dataeng', ['terminate-job', '--job-id', job_id])


  def list_clusters(self, names=None, page_size=None, starting_token=None):
    args = ['list-clusters']

    if names:
      args.extend(['--cluster-names', names])
    if page_size is not None:
      args.extend(['--page-size', str(page_size)])
    if starting_token:
      args.extend(['--starting-token', starting_token])

    return _exec('dataeng', args)

  def create_cluster(self):
    return _exec('dataeng', ['create-cluster'])

  def delete_cluster(self):
    return _exec('dataeng', ['delete-cluster'])

  def describe_clusters(self):
    return _exec('dataeng', ['describe-cluster'])


class AnalyticDbApi():

  def __init__(self, user): pass

  def list_clusters(self):
    """
    e.g. returns
    [{
            "status": "CREATED",
            "namespaceCrn": "crn:altus:sdx:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:namespace:spot-ns/7bdb225f-a7a1-408e-8503-1b3a422cc039",
            "workersGroupSize": 4,
            "clusterName": "spot",
            "environmentType": "AWS",
            "secured": false,
            "environmentCrn": "crn:altus:environments:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:environment:Spot-AWS-dev2/5a6d0ced-c8af-4fa3-9b24-8c5a3ea11cf8",
            "securityConfiguration": {
                "enabled": false
            },
            "creationDate": "2018-06-01T13:14:43.530000+00:00",
            "crn": "crn:altus:analyticdb:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:cluster:spot/70595482-6a46-4a9d-b395-56fcabe079e4",
            "instanceType": "r4.4xlarge",
            "cdhVersion": "CDH514"
        },
      ...
    ]
    """

    args = ['list-clusters']
    return _exec('analyticdb', args)
