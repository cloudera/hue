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

import json
import logging
import posixpath
import threading

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from hadoop import cluster


LOG = logging.getLogger(__name__)
DEFAULT_USER = 'hue'

_API_VERSION = 'v1'
_JSON_CONTENT_TYPE = 'application/json'

_api_cache = None
_api_cache_lock = threading.Lock()


def get_resource_manager():
  global _api_cache
  if _api_cache is None:
    _api_cache_lock.acquire()
    try:
      if _api_cache is None:
        yarn_cluster = cluster.get_cluster_conf_for_job_submission()
        if yarn_cluster is None:
          raise PopupException(_('No Resource Manager are available.'))
        _api_cache = ResourceManagerApi(yarn_cluster.RESOURCE_MANAGER_API_URL.get(), yarn_cluster.SECURITY_ENABLED.get(), yarn_cluster.SSL_CERT_CA_VERIFY.get())
    finally:
      _api_cache_lock.release()
  return _api_cache


class YarnFailoverOccurred(Exception):
  pass


class ResourceManagerApi(object):

  def __init__(self, oozie_url, security_enabled=False, ssl_cert_ca_verify=False):
    self._url = posixpath.join(oozie_url, 'ws', _API_VERSION)
    self._client = HttpClient(self._url, logger=LOG)
    self._root = Resource(self._client)
    self._security_enabled = security_enabled

    if self._security_enabled:
      self._client.set_kerberos_auth()

    self._client.set_verify(ssl_cert_ca_verify)

  def __str__(self):
    return "ResourceManagerApi at %s" % (self._url,)

  @property
  def url(self):
    return self._url

  @property
  def security_enabled(self):
    return self._security_enabled

  def cluster(self, **kwargs):
    return self._execute(self._root.get, 'cluster', params=kwargs, headers={'Accept': _JSON_CONTENT_TYPE})

  def apps(self, **kwargs):
    return self._execute(self._root.get, 'cluster/apps', params=kwargs, headers={'Accept': _JSON_CONTENT_TYPE})

  def app(self, app_id):
    return self._execute(self._root.get, 'cluster/apps/%(app_id)s' % {'app_id': app_id}, headers={'Accept': _JSON_CONTENT_TYPE})

  def kill(self, app_id):
    return self._execute(self._root.put, 'cluster/apps/%(app_id)s/state' % {'app_id': app_id}, data=json.dumps({'state': 'KILLED'}), contenttype=_JSON_CONTENT_TYPE)

  def _execute(self, function, *args, **kwargs):
    response = function(*args, **kwargs)

    # YARN-2605: Yarn does not use proper HTTP redirects when the standby RM has
    # failed back to the master RM.
    if isinstance(response, str) and response.startswith('This is standby RM. Redirecting to the current active RM'):
      raise YarnFailoverOccurred(response)

    return response
