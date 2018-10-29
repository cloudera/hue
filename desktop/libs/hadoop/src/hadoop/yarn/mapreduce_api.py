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
from hadoop.yarn.resource_manager_api import get_resource_manager


LOG = logging.getLogger(__name__)

_API_VERSION = 'v1'
_JSON_CONTENT_TYPE = 'application/json'

API_CACHE = None
API_CACHE_LOCK = threading.Lock()


def get_mapreduce_api(username):
  global API_CACHE
  if API_CACHE is None:
    API_CACHE_LOCK.acquire()
    try:
      if API_CACHE is None:
        yarn_cluster = cluster.get_cluster_conf_for_job_submission()
        if yarn_cluster is None:
          raise PopupException(_('No Resource Manager are available.'))
        API_CACHE = MapreduceApi(yarn_cluster.PROXY_API_URL.get(), yarn_cluster.SECURITY_ENABLED.get(), yarn_cluster.SSL_CERT_CA_VERIFY.get())
    finally:
      API_CACHE_LOCK.release()

  API_CACHE.setuser(username)  # Set the correct user

  return API_CACHE


class MapreduceApi(object):

  def __init__(self, mr_url, security_enabled=False, ssl_cert_ca_verify=False):
    self._url = posixpath.join(mr_url, 'proxy')
    self._client = HttpClient(self._url, logger=LOG)
    self._root = Resource(self._client)
    self._security_enabled = security_enabled
    self._thread_local = threading.local()  # To store user info

    if self._security_enabled:
      self._client.set_kerberos_auth()

    self._client.set_verify(ssl_cert_ca_verify)

  def __str__(self):
    return "MapreduceApi at %s" % (self._url,)

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
  def username(self):
    try:
      return self._thread_local.user
    except AttributeError:
      return DEFAULT_USER.get()

  def setuser(self, user):
    curr = self.username
    self._thread_local.user = user
    return curr

  def job(self, user, job_id):
    app_id = job_id.replace('job', 'application')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s' % {'app_id': app_id, 'job_id': job_id, 'version': _API_VERSION}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def counters(self, job_id):
    app_id = job_id.replace('job', 'application')
    response = self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/counters' % {'app_id': app_id, 'job_id': job_id, 'version': _API_VERSION}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})
    # If it hits the job history server, it will return HTML.
    # Simply return None in this case because there isn't much data there.
    if isinstance(response, basestring):
      return None
    else:
      return response

  def tasks(self, job_id):
    app_id = job_id.replace('job', 'application')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/tasks' % {'app_id': app_id, 'job_id': job_id, 'version': _API_VERSION}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def job_attempts(self, job_id):
    app_id = job_id.replace('job', 'application')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/jobattempts' % {'app_id': app_id, 'job_id': job_id, 'version': _API_VERSION}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def conf(self, job_id):
    app_id = job_id.replace('job', 'application')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/conf' % {'app_id': app_id, 'job_id': job_id, 'version': _API_VERSION}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def task(self, job_id, task_id):
    app_id = job_id.replace('job', 'application')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/tasks/%(task_id)s' % {'app_id': app_id, 'job_id': job_id, 'task_id': task_id, 'version': _API_VERSION}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def task_counters(self, job_id, task_id):
    app_id = job_id.replace('job', 'application')
    job_id = job_id.replace('application', 'job')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/tasks/%(task_id)s/counters' % {'app_id': app_id, 'job_id': job_id, 'task_id': task_id, 'version': _API_VERSION}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def task_attempts(self, job_id, task_id):
    app_id = job_id.replace('job', 'application')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/tasks/%(task_id)s/attempts' % {'app_id': app_id, 'job_id': job_id, 'task_id': task_id, 'version': _API_VERSION}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def task_attempt(self, job_id, task_id, attempt_id):
    app_id = job_id.replace('job', 'application')
    job_id = job_id.replace('application', 'job')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/tasks/%(task_id)s/attempts/%(attempt_id)s' % {'app_id': app_id, 'job_id': job_id, 'task_id': task_id, 'attempt_id': attempt_id, 'version': _API_VERSION}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def task_attempt_counters(self, job_id, task_id, attempt_id):
    app_id = job_id.replace('job', 'application')
    job_id = job_id.replace('application', 'job')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/tasks/%(task_id)s/attempts/%(attempt_id)s/counters' % {'app_id': app_id, 'job_id': job_id, 'task_id': task_id, 'attempt_id': attempt_id, 'version': _API_VERSION}, params=self._get_params(), headers={'Accept': _JSON_CONTENT_TYPE})

  def kill(self, job_id):
    app_id = job_id.replace('job', 'application')
    get_resource_manager(self.username).kill(app_id) # We need to call the RM
