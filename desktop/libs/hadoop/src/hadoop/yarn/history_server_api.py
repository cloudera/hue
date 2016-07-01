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
import posixpath
import threading

from desktop.conf import DEFAULT_USER
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource
from hadoop import cluster


LOG = logging.getLogger(__name__)

_API_VERSION = 'v1'
_JSON_CONTENT_TYPE = 'application/json'

API_CACHE = None
API_CACHE_LOCK = threading.Lock()


def get_history_server_api(username):
  global API_CACHE
  if API_CACHE is None:
    API_CACHE_LOCK.acquire()
    try:
      if API_CACHE is None:
        yarn_cluster = cluster.get_cluster_conf_for_job_submission()
        if yarn_cluster is None:
          raise PopupException(_('YARN cluster is not available.'))
        API_CACHE = HistoryServerApi(yarn_cluster.HISTORY_SERVER_API_URL.get(), yarn_cluster.SECURITY_ENABLED.get(), yarn_cluster.SSL_CERT_CA_VERIFY.get())
    finally:
      API_CACHE_LOCK.release()

  API_CACHE.setuser(username)  # Set the correct user

  return API_CACHE


class HistoryServerApi(object):

  def __init__(self, oozie_url, security_enabled=False, ssl_cert_ca_verify=False):
    self._url = posixpath.join(oozie_url, 'ws/%s/history' % _API_VERSION)
    self._client = HttpClient(self._url, logger=LOG)
    self._root = Resource(self._client)
    self._security_enabled = security_enabled
    self._thread_local = threading.local()  # To store user info

    if self._security_enabled:
      self._client.set_kerberos_auth()

    self._client.set_verify(ssl_cert_ca_verify)

  def __str__(self):
    return "HistoryServerApi at %s" % (self._url,)

  def _get_params(self):
    params = {}

    if self.username != DEFAULT_USER.get():  # We impersonate if needed
      params['doAs'] = self.username
      if not self._security_enabled:
        params['user.name'] = DEFAULT_USER.get()

    return params

  @property
  def url(self):
    return self._url

  @property
  def user(self):
    return self.username  # Backward compatibility

  @property
  def username(self):
    try:
      return self._thread_local.user
    except AttributeError:
      return DEFAULT_USER.get()

  def setuser(self, user):
    curr = self.user
    self._thread_local.user = user
    return curr

  def job(self, user, job_id):
    return self._root.get('mapreduce/jobs/%(job_id)s' % {'job_id': job_id}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def counters(self, job_id):
    return self._root.get('mapreduce/jobs/%(job_id)s/counters' % {'job_id': job_id}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def conf(self, job_id):
    return self._root.get('mapreduce/jobs/%(job_id)s/conf' % {'job_id': job_id}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def job_attempts(self, job_id):
    return self._root.get('mapreduce/jobs/%(job_id)s/jobattempts' % {'job_id': job_id}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def tasks(self, job_id):
    return self._root.get('mapreduce/jobs/%(job_id)s/tasks' % {'job_id': job_id}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def task(self, job_id, task_id):
    return self._root.get('mapreduce/jobs/%(job_id)s/tasks/%(task_id)s' % {'job_id': job_id, 'task_id': task_id}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def task_attempts(self, job_id, task_id):
    return self._root.get('mapreduce/jobs/%(job_id)s/tasks/%(task_id)s/attempts' % {'job_id': job_id, 'task_id': task_id}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def task_counters(self, job_id, task_id):
    job_id = job_id.replace('application', 'job')
    return self._root.get('mapreduce/jobs/%(job_id)s/tasks/%(task_id)s/counters' % {'job_id': job_id, 'task_id': task_id}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def task_attempt(self, job_id, task_id, attempt_id):
    return self._root.get('mapreduce/jobs/%(job_id)s/tasks/%(task_id)s/attempts/%(attempt_id)s' % {'job_id': job_id, 'task_id': task_id, 'attempt_id': attempt_id}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def task_attempt_counters(self, job_id, task_id, attempt_id):
    return self._root.get('mapreduce/jobs/%(job_id)s/tasks/%(task_id)s/attempts/%(attempt_id)s/counters' % {'job_id': job_id, 'task_id': task_id, 'attempt_id': attempt_id}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})
