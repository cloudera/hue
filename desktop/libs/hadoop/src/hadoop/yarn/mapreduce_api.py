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

from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource
from hadoop import cluster
from hadoop.yarn.resource_manager_api import get_resource_manager


LOG = logging.getLogger(__name__)
DEFAULT_USER = 'hue'

_API_VERSION = 'v1'
_JSON_CONTENT_TYPE = 'application/json'

_api_cache = None
_api_cache_lock = threading.Lock()


def get_mapreduce_api():
  global _api_cache
  if _api_cache is None:
    _api_cache_lock.acquire()
    try:
      if _api_cache is None:
        yarn_cluster = cluster.get_cluster_conf_for_job_submission()
        _api_cache = MapreduceApi(yarn_cluster.PROXY_API_URL.get(), yarn_cluster.SECURITY_ENABLED.get())
    finally:
      _api_cache_lock.release()
  return _api_cache


class MapreduceApi(object):

  def __init__(self, oozie_url, security_enabled=False):
    self._url = posixpath.join(oozie_url, 'proxy')
    self._client = HttpClient(self._url, logger=LOG)
    self._root = Resource(self._client)
    self._security_enabled = security_enabled

    if self._security_enabled:
      self._client.set_kerberos_auth()

  def __str__(self):
    return "MapreduceApi at %s" % (self._url,)

  @property
  def url(self):
    return self._url

  def job(self, user, job_id):
    app_id = job_id.replace('job', 'application')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s' % {'app_id': app_id, 'job_id': job_id, 'version': _API_VERSION}, headers={'Accept': _JSON_CONTENT_TYPE})

  def counters(self, job_id):
    app_id = job_id.replace('job', 'application')
    response = self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/counters' % {'app_id': app_id, 'job_id': job_id, 'version': _API_VERSION}, headers={'Accept': _JSON_CONTENT_TYPE})
    # If it hits the job history server, it will return HTML.
    # Simply return None in this case because there isn't much data there.
    if isinstance(response, basestring):
      return None
    else:
      return response

  def tasks(self, job_id):
    app_id = job_id.replace('job', 'application')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/tasks' % {'app_id': app_id, 'job_id': job_id, 'version': _API_VERSION}, headers={'Accept': _JSON_CONTENT_TYPE})

  def job_attempts(self, job_id):
    app_id = job_id.replace('job', 'application')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/jobattempts' % {'app_id': app_id, 'job_id': job_id, 'version': _API_VERSION}, headers={'Accept': _JSON_CONTENT_TYPE})

  def conf(self, job_id):
    app_id = job_id.replace('job', 'application')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/conf' % {'app_id': app_id, 'job_id': job_id, 'version': _API_VERSION}, headers={'Accept': _JSON_CONTENT_TYPE})

  def task(self, job_id, task_id):
    app_id = job_id.replace('job', 'application')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/tasks/%(task_id)s' % {'app_id': app_id, 'job_id': job_id, 'task_id': task_id, 'version': _API_VERSION}, headers={'Accept': _JSON_CONTENT_TYPE})

  def task_counters(self, job_id, task_id):
    app_id = job_id.replace('job', 'application')
    job_id = job_id.replace('application', 'job')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/tasks/%(task_id)s/counters' % {'app_id': app_id, 'job_id': job_id, 'task_id': task_id, 'version': _API_VERSION}, headers={'Accept': _JSON_CONTENT_TYPE})

  def task_attempts(self, job_id, task_id):
    app_id = job_id.replace('job', 'application')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/tasks/%(task_id)s/attempts' % {'app_id': app_id, 'job_id': job_id, 'task_id': task_id, 'version': _API_VERSION}, headers={'Accept': _JSON_CONTENT_TYPE})

  def task_attempt(self, job_id, task_id, attempt_id):
    app_id = job_id.replace('job', 'application')
    job_id = job_id.replace('application', 'job')
    return self._root.get('%(app_id)s/ws/%(version)s/mapreduce/jobs/%(job_id)s/tasks/%(task_id)s/attempts/%(attempt_id)s' % {'app_id': app_id, 'job_id': job_id, 'task_id': task_id, 'attempt_id': attempt_id, 'version': _API_VERSION}, headers={'Accept': _JSON_CONTENT_TYPE})

  def kill(self, job_id):
    app_id = job_id.replace('job', 'application')
    get_resource_manager().kill(app_id) # We need to call the RM
