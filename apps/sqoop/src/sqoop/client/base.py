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
import posixpath
import threading
import time
try:
  import json
except ImportError:
  import simplejson as json

from django.utils.translation import ugettext as _

from desktop.conf import TIME_ZONE
from desktop.lib.rest.http_client import HttpClient

from connection import Connection, SqoopConnectionException
from connector import Connector
from framework import Framework
from job import Job, SqoopJobException
from submission import Submission, SqoopSubmissionException
from resource import SqoopResource


LOG = logging.getLogger(__name__)
DEFAULT_USER = 'hue'
API_VERSION = 'v1'

_JSON_CONTENT_TYPE = 'application/json'


class SqoopClient(object):
  """
  Sqoop client
  """
  STATUS_GOOD = ('FINE', 'ACCEPTABLE')
  STATUS_BAD = ('UNACCEPTABLE', 'FAILURE_ON_SUBMIT')

  def __init__(self, url, username, language='en'):
    self._url = url
    self._client = HttpClient(self._url, logger=LOG)
    self._root = SqoopResource(self._client)
    self._language = language
    self._username = username

  def __str__(self):
    return "SqoopClient at %s" % self._url

  @property
  def url(self):
    return self._url

  @property
  def headers(self):
    return {
      'Accept': 'application/json',
      'Accept-Language': self._language,
      'sqoop-user-name': self._username
    }

  def get_version(self):
    return self._root.get('version', headers=self.headers)

  def get_framework(self):
    resp_dict = self._root.get('%s/framework/all' % API_VERSION, headers=self.headers)
    framework = Framework.from_dict(resp_dict)
    return framework

  def get_connectors(self):
    resp_dict = self._root.get('%s/connector/all' % API_VERSION, headers=self.headers)
    connectors = [ Connector.from_dict(connector_dict, resp_dict['resources-connector']) for connector_dict in resp_dict['all'] ]
    return connectors

  def get_connector(self, connector_id):
    resp_dict = self._root.get('%s/connector/%d/' % (API_VERSION, connector_id), headers=self.headers)
    if resp_dict['all']:
      return Connector.from_dict(resp_dict['all'][0], resp_dict['resources-connector'])
    return None

  def get_connections(self):
    resp_dict = self._root.get('%s/connection/all' % API_VERSION, headers=self.headers)
    connections = [Connection.from_dict(conn_dict) for conn_dict in resp_dict['all']]
    return connections

  def get_connection(self, connection_id):
    resp_dict = self._root.get('%s/connection/%d/' % (API_VERSION, connection_id), headers=self.headers)
    if resp_dict['all']:
      return Connection.from_dict(resp_dict['all'][0])
    return None

  def create_connection(self, connection):
    if not connection.connector:
      connection.connector = self.get_connectors()[0].con_forms
    if not connection.framework:
      connection.framework = self.get_framework().con_forms
    connection.creation_date = int( round(time.time() * 1000) )
    connection.update_date = connection.creation_date
    connection_dict = connection.to_dict()
    request_dict = {
      'all': [connection_dict]
    }
    resp = self._root.post('%s/connection/' % API_VERSION, data=json.dumps(request_dict), headers=self.headers)
    if 'id' not in resp:
      raise SqoopConnectionException.from_dict(resp)
    connection.id = resp['id']
    return connection

  def update_connection(self, connection):
    """ Update a connection """
    if not connection.connector:
      connection.connector = self.get_connectors()[0].con_forms
    if not connection.framework:
      connection.framework = self.get_framework().con_forms
    connection.updated = int( round(time.time() * 1000) )
    connection_dict = connection.to_dict()
    request_dict = {
      'all': [connection_dict]
    }
    resp = self._root.put('%s/connection/%d/' % (API_VERSION, connection.id), data=json.dumps(request_dict), headers=self.headers)
    if resp['connector']['status'] in SqoopClient.STATUS_BAD or resp['framework']['status'] in SqoopClient.STATUS_BAD:
      raise SqoopConnectionException.from_dict(resp)
    return connection

  def delete_connection(self, connection):
    resp = self._root.delete('%s/connection/%d/' % (API_VERSION, connection.id), headers=self.headers)
    return None

  def get_jobs(self):
    resp_dict = self._root.get('%s/job/all' % API_VERSION, headers=self.headers)
    jobs = [Job.from_dict(job_dict) for job_dict in resp_dict['all']]
    return jobs

  def get_job(self, job_id):
    resp_dict = self._root.get('%s/job/%d/' % (API_VERSION, job_id), headers=self.headers)
    if resp_dict['all']:
      return Job.from_dict(resp_dict['all'][0])
    return None

  def create_job(self, job):
    if not job.connector:
      job.connector = self.get_connectors()[0].job_forms[job.type.upper()]
    if not job.framework:
      job.framework = self.get_framework().job_forms[job.type.upper()]
    job.creation_date = int( round(time.time() * 1000) )
    job.update_date = job.creation_date
    job_dict = job.to_dict()
    request_dict = {
      'all': [job_dict]
    }
    resp = self._root.post('%s/job/' % API_VERSION, data=json.dumps(request_dict), headers=self.headers)
    if 'id' not in resp:
      raise SqoopJobException.from_dict(resp)
    job.id = resp['id']
    return job

  def update_job(self, job):
    if not job.connector:
      job.connector = self.get_connectors()[0].job_forms[job.type.upper()]
    if not job.framework:
      job.framework = self.get_framework().job_forms[job.type.upper()]
    job.updated = int( round(time.time() * 1000) )
    job_dict = job.to_dict()
    request_dict = {
      'all': [job_dict]
    }
    resp = self._root.put('%s/job/%d/' % (API_VERSION, job.id), data=json.dumps(request_dict), headers=self.headers)
    if resp['connector']['status'] in SqoopClient.STATUS_BAD or resp['framework']['status'] in SqoopClient.STATUS_BAD:
      raise SqoopJobException.from_dict(resp)
    return job

  def delete_job(self, job):
    resp_dict = self._root.delete('%s/job/%d/' % (API_VERSION, job.id), headers=self.headers)
    return None

  def get_job_status(self, job):
    resp_dict = self._root.get('%s/submission/action/%d/' % (API_VERSION, job.id), headers=self.headers)
    return Submission.from_dict(resp_dict['all'][0])

  def start_job(self, job):
    resp_dict = self._root.post('%s/submission/action/%d/' % (API_VERSION, job.id), headers=self.headers)
    if resp_dict['all'][0]['status'] in SqoopClient.STATUS_BAD:
      raise SqoopSubmissionException.from_dict(resp_dict['all'][0])
    return Submission.from_dict(resp_dict['all'][0])

  def stop_job(self, job):
    resp_dict = self._root.delete('%s/submission/action/%d/' % (API_VERSION, job.id), headers=self.headers)
    return Submission.from_dict(resp_dict['all'][0])

  def get_submissions(self):
    resp_dict = self._root.get('%s/submission/history/all' % API_VERSION, headers=self.headers)
    submissions = [Submission.from_dict(submission_dict) for submission_dict in resp_dict['all']]
    return submissions

  def set_user(self, user):
    self._user = user

  def set_language(self, language):
    self._language = language
