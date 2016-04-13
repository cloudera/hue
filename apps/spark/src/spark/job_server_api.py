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
import posixpath
import threading

from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from spark.conf import get_livy_server_url


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
        _api_cache = JobServerApi(get_livy_server_url())
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

  def get_status(self):
    return self._root.get('sessions')

  def get_log(self, uuid, startFrom=None, size=None):
    params = {}

    if startFrom is not None:
      params['from'] = startFrom

    if size is not None:
      params['size'] = size

    response = self._root.get('sessions/%s/log' % uuid, params=params)

    return '\n'.join(response['log'])

  def create_session(self, **properties):
    properties['proxyUser'] = self.user
    return self._root.post('sessions', data=json.dumps(properties), contenttype=_JSON_CONTENT_TYPE)

  def get_session(self, uuid):
    return self._root.get('sessions/%s' % uuid)

  def submit_statement(self, uuid, statement):
    data = {'code': statement}
    return self._root.post('sessions/%s/statements' % uuid, data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)

  def inspect(self, uuid, statement):
    data = {'code': statement}
    return self._root.post('sessions/%s/inspect' % uuid, data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)

  def fetch_data(self, session, statement):
    return self._root.get('sessions/%s/statements/%s' % (session, statement))

  def cancel(self, session):
    return self._root.post('sessions/%s/interrupt' % session)

  def close(self, uuid):
    return self._root.delete('sessions/%s' % uuid)

  def get_batches(self):
    return self._root.get('batches')

  def submit_batch(self, properties):
    properties['proxyUser'] = self.user
    return self._root.post('batches', data=json.dumps(properties), contenttype=_JSON_CONTENT_TYPE)

  def get_batch(self, uuid):
    return self._root.get('batches/%s' % uuid)

  def get_batch_status(self, uuid):
    response = self._root.get('batches/%s/state' % uuid)
    return response['state']

  def get_batch_log(self, uuid, startFrom=None, size=None):
    params = {}

    if startFrom is not None:
      params['from'] = startFrom

    if size is not None:
      params['size'] = size

    response = self._root.get('batches/%s/log' % uuid, params=params)

    return '\n'.join(response['log'])

  def close_batch(self, uuid):
    return self._root.delete('batches/%s' % uuid)
