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
import time
import json


from desktop.lib.rest.http_client import HttpClient

from sqoop.client.link import Link
from sqoop.client.job import Job
from sqoop.client.connector import Connector
from sqoop.client.driver import Driver
from sqoop.client.exception import SqoopException
from sqoop.client.submission import Submission, SqoopSubmissionException
from sqoop.client.resource import SqoopResource
from sqoop.sqoop_properties import has_sqoop_has_security


LOG = logging.getLogger(__name__)
DEFAULT_USER = 'hue'
API_VERSION = 'v1'

_JSON_CONTENT_TYPE = 'application/json'


class SqoopClient(object):

  STATUS_GOOD = ('FINE', 'ACCEPTABLE')
  STATUS_BAD = ('UNACCEPTABLE', 'FAILURE_ON_SUBMIT')

  def __init__(self, url, username, language='en', ssl_cert_ca_verify=False):
    self._url = url
    self._client = HttpClient(self._url, logger=LOG)
    self._root = SqoopResource(self._client)
    self._language = language
    self._username = username

    if has_sqoop_has_security():
      self._client.set_kerberos_auth()
    self._security_enabled = has_sqoop_has_security()

    self._client.set_verify(ssl_cert_ca_verify)

  def __str__(self):
    return "SqoopClient at %s with security %s" % (self._url, self._security_enabled)

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

  def get_driver(self):
    resp_dict = self._root.get('%s/driver' % API_VERSION, headers=self.headers)
    driver = Driver.from_dict(resp_dict)
    return driver

  def get_connectors(self):
    resp_dict = self._root.get('%s/connectors' % API_VERSION, headers=self.headers)
    connectors = [ Connector.from_dict(connector_dict) for connector_dict in resp_dict['connectors'] ]
    return connectors

  def get_connector(self, connector_id):
    resp_dict = self._root.get('%s/connector/%d/' % (API_VERSION, connector_id), headers=self.headers)
    if resp_dict['connector']:
      return Connector.from_dict(resp_dict['connector'])
    return None

  def get_links(self):
    resp_dict = self._root.get('%s/links' % API_VERSION, headers=self.headers)
    links = [Link.from_dict(link_dict) for link_dict in resp_dict['links']]
    return links

  def get_link(self, link_id):
    resp_dict = self._root.get('%s/link/%d/' % (API_VERSION, link_id), headers=self.headers)
    if resp_dict['link']:
      return Link.from_dict(resp_dict['link'])
    return None

  def create_link(self, link):
    link.creation_date = int( round(time.time() * 1000) )
    link.update_date = link.creation_date
    link_dict = link.to_dict()
    request_dict = {
      'link': link_dict
    }
    resp = self._root.post('%s/link/' % API_VERSION, data=json.dumps(request_dict), headers=self.headers)

    # Lame check that iterates to make sure we have an error
    # Server responds with: {'validation-result': [{},{}]} or {'validation-result': [{KEY: ERROR},{KEY: ERROR}]}
    for result in resp['validation-result']:
      if result:
        raise SqoopException.from_dicts(resp['validation-result'])

    link.id = resp['id']
    return link

  def update_link(self, link):
    if not link.link_config_values:
      link.link_config_values = self.get_connectors()[0].link_config
    link.updated = int( round(time.time() * 1000) )
    link_dict = link.to_dict()
    request_dict = {
      'link': link_dict
    }
    resp = self._root.put('%s/link/%d/' % (API_VERSION, link.id), data=json.dumps(request_dict), headers=self.headers)
    
    # Lame check that iterates to make sure we have an error
    # Server responds with: {'validation-result': [{},{}]} or {'validation-result': [{KEY: ERROR},{KEY: ERROR}]}
    for result in resp['validation-result']:
      if result:
        raise SqoopException.from_dicts(resp['validation-result'])

    return link

  def delete_link(self, link):
    resp = self._root.delete('%s/link/%d/' % (API_VERSION, link.id), headers=self.headers)
    return None

  def get_jobs(self):
    resp_dict = self._root.get('%s/jobs' % API_VERSION, headers=self.headers)
    jobs = [Job.from_dict(job_dict) for job_dict in resp_dict['jobs']]
    return jobs

  def get_job(self, job_id):
    resp_dict = self._root.get('%s/job/%d/' % (API_VERSION, job_id), headers=self.headers)
    if resp_dict['job']:
      return Job.from_dict(resp_dict['job'])
    return None

  def create_job(self, job):
    if not job.from_config_values:
      job.from_config_values = self.get_connectors()[0].job_config['FROM']
    if not job.to_config_values:
      job.to_config_values = self.get_connectors()[0].job_config['TO']
    if not job.driver_config_values:
      job.driver_config_values = self.get_driver().job_config
    job.creation_date = int( round(time.time() * 1000) )
    job.update_date = job.creation_date
    job_dict = job.to_dict()
    request_dict = {
      'job': job_dict
    }
    resp = self._root.post('%s/job/' % API_VERSION, data=json.dumps(request_dict), headers=self.headers)
    if 'id' not in resp:
      raise SqoopException.from_dicts(resp['validation-result'])
    job.id = resp['id']
    return job

  def update_job(self, job):
    if not job.from_config_values:
      job.from_config_values = self.get_connectors()[0].job_config['FROM']
    if not job.to_config_values:
      job.to_config_values = self.get_connectors()[0].job_config['TO']
    if not job.driver_config_values:
      job.driver_config_values = self.get_driver().job_config
    job.updated = int( round(time.time() * 1000) )
    job_dict = job.to_dict()
    request_dict = {
      'job': job_dict
    }
    resp = self._root.put('%s/job/%d/' % (API_VERSION, job.id), data=json.dumps(request_dict), headers=self.headers)

    # Lame check that iterates to make sure we have an error
    # Server responds with: {'validation-result': [{},{}]} or {'validation-result': [{KEY: ERROR},{KEY: ERROR}]}
    for result in resp['validation-result']:
      if result:
        raise SqoopException.from_dicts(resp['validation-result'])

    return job

  def delete_job(self, job):
    resp_dict = self._root.delete('%s/job/%s' % (API_VERSION, job.id), headers=self.headers)
    return None

  def get_job_status(self, job):
    resp_dict = self._root.get('%s/job/%d/status' % (API_VERSION, job.id), headers=self.headers)
    return Submission.from_dict(resp_dict['submission'])

  def start_job(self, job):
    resp_dict = self._root.put('%s/job/%d/start' % (API_VERSION, job.id), headers=self.headers)
    if resp_dict['submission']['status'] in SqoopClient.STATUS_BAD:
      raise SqoopSubmissionException.from_dict(resp_dict['submission'])
    return Submission.from_dict(resp_dict['submission'])

  def stop_job(self, job):
    resp_dict = self._root.put('%s/job/%d/stop' % (API_VERSION, job.id), headers=self.headers)
    return Submission.from_dict(resp_dict['submission'])

  def get_submissions(self):
    resp_dict = self._root.get('%s/submissions' % API_VERSION, headers=self.headers)
    submissions = [Submission.from_dict(submission_dict) for submission_dict in resp_dict['submissions']]
    return submissions

  def set_user(self, user):
    self._user = user

  def set_language(self, language):
    self._language = language
