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

from spark.conf import JOB_SERVER_URL


LOG = logging.getLogger(__name__)
DEFAULT_USER = 'hue'

_API_VERSION = 'v1'
_JSON_CONTENT_TYPE = 'application/json'
_BINARY_CONTENT_TYPE = 'application/octet-stream'
_TEXT_CONTENT_TYPE = 'text/plain'

_api_cache = None
_api_cache_lock = threading.Lock()


def get_api(user):
  global _api_cache
  if _api_cache is None:
    _api_cache_lock.acquire()
    try:
      if _api_cache is None:
        _api_cache = JobServerApi(JOB_SERVER_URL.get())
    finally:
      _api_cache_lock.release()
  _api_cache.setuser(user)
  return _api_cache


class JobServerApi(object):
  def __init__(self, oozie_url):
    self._url = posixpath.join(oozie_url)
    self._client = HttpClient(self._url, logger=LOG)
    self._root = Resource(self._client)
    self._security_enabled = False
    # To store user info
    self._thread_local = threading.local()

  def __str__(self):
    return "JobServerApi at %s" % (self._url,)

  @property
  def url(self):
    return self._url

  @property
  def security_enabled(self):
    return self._security_enabled

  @property
  def user(self):
    return self._thread_local.user

  def setuser(self, user):
    if hasattr(user, 'username'):
      self._thread_local.user = user.username
    else:
      self._thread_local.user = user

  def get_status(self, **kwargs):
    return self._root.get('healthz', params=kwargs, headers={'Accept': _TEXT_CONTENT_TYPE})

  def submit_job(self, appName, classPath, data, context=None, sync=False):
    params = {'appName': appName, 'classPath': classPath, 'sync': sync}
    if context:
      params['context'] = context
    return self._root.post('jobs' % params, params=params, data=data, contenttype=_BINARY_CONTENT_TYPE)

  def job(self, job_id):
    return self._root.get('jobs/%s' % job_id, headers={'Accept': _JSON_CONTENT_TYPE})

  def jobs(self, **kwargs):
    return self._root.get('jobs', params=kwargs, headers={'Accept': _JSON_CONTENT_TYPE})

  def create_context(self, name, **kwargs):
    return self._root.post('contexts/%s' % name, params=kwargs, contenttype=_BINARY_CONTENT_TYPE)

  def contexts(self, **kwargs):
    return self._root.get('contexts', params=kwargs, headers={'Accept': _JSON_CONTENT_TYPE})

  def delete_context(self, name, **kwargs):
    return self._root.delete('contexts/%s' % name)

  def upload_jar(self, app_name, data):
    return self._root.post('jars/%s' % app_name, data=data, contenttype=_BINARY_CONTENT_TYPE)

  def jars(self, **kwargs):
    return self._root.get('jars', params=kwargs, headers={'Accept': _JSON_CONTENT_TYPE})
