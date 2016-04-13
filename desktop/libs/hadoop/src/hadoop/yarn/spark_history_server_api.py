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


LOG = logging.getLogger(__name__)
DEFAULT_USER = 'hue'

_API_VERSION = 'v1'
_JSON_CONTENT_TYPE = 'application/json'

_api_cache = None
_api_cache_lock = threading.Lock()


def get_history_server_api():
  global _api_cache
  if _api_cache is None:
    _api_cache_lock.acquire()
    try:
      if _api_cache is None:
        yarn_cluster = cluster.get_cluster_conf_for_job_submission()
        _api_cache = SparkHistoryServerApi(yarn_cluster.SPARK_HISTORY_SERVER_URL.get(), yarn_cluster.SECURITY_ENABLED.get(), yarn_cluster.SSL_CERT_CA_VERIFY.get())
    finally:
      _api_cache_lock.release()
  return _api_cache


class SparkHistoryServerApi(object):

  def __init__(self, spark_hs_url, security_enabled=False, ssl_cert_ca_verify=False):
    self._ui_url = spark_hs_url
    self._url = posixpath.join(spark_hs_url, 'api/%s/' % _API_VERSION)
    self._client = HttpClient(self._url, logger=LOG)
    self._root = Resource(self._client)
    self._security_enabled = security_enabled

    if self._security_enabled:
      self._client.set_kerberos_auth()

    self._client.set_verify(ssl_cert_ca_verify)

  def __str__(self):
    return "Spark History Server API at %s" % (self._url,)

  @property
  def url(self):
    return self._url

  @property
  def ui_url(self):
    return self._ui_url

  @property
  def headers(self):
    return {'Accept': _JSON_CONTENT_TYPE}

  def applications(self):
    return self._root.get('applications', headers=self.headers)

  def application(self, app_id):
    return self._root.get('applications/%(app_id)s' % {'app_id': app_id}, headers=self.headers)

  def jobs(self, app_id, attempt_id):
    return self._root.get('applications/%(app_id)s/%(attempt_id)s/jobs' % {'app_id': app_id, 'attempt_id': attempt_id}, headers=self.headers)

  def stages(self, app_id, attempt_id):
    return self._root.get('applications/%(app_id)s/%(attempt_id)s/stages' % {'app_id': app_id, 'attempt_id': attempt_id}, headers=self.headers)

  def executors(self, app_id, attempt_id):
    return self._root.get('applications/%(app_id)s/%(attempt_id)s/executors' % {'app_id': app_id, 'attempt_id': attempt_id}, headers=self.headers)

  # TODO: stage attempts, task summaries, task list, storage, download logs
  # http://spark.apache.org/docs/latest/monitoring.html#rest-api
