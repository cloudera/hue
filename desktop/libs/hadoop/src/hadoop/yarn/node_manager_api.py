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

from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from hadoop import cluster


LOG = logging.getLogger(__name__)
DEFAULT_USER = 'hue'

_API_VERSION = 'v1'
_JSON_CONTENT_TYPE = 'application/json'



def get_node_manager_api(api_url):
  yarn_cluster = cluster.get_cluster_conf_for_job_submission()
  return NodeManagerApi(api_url, yarn_cluster.SECURITY_ENABLED.get(), yarn_cluster.SSL_CERT_CA_VERIFY.get())


class NodeManagerApi(object):
  def __init__(self, oozie_url, security_enabled=False, ssl_cert_ca_verify=True):
    self._url = posixpath.join(oozie_url, 'ws', _API_VERSION)
    self._client = HttpClient(self._url, logger=LOG)
    self._root = Resource(self._client)
    self._security_enabled = security_enabled

    if self._security_enabled:
      self._client.set_kerberos_auth()

    self._client.set_verify(ssl_cert_ca_verify)

  def __str__(self):
    return "NodeManagerApi at %s" % (self._url,)

  @property
  def url(self):
    return self._url

  @property
  def security_enabled(self):
    return self._security_enabled

  def containers(self):
    return self._root.get('node/containers', headers={'Accept': _JSON_CONTENT_TYPE})

  def container(self, container_id):
    return self._root.get('node/containers/%(container_id)s' % {'container_id': container_id}, headers={'Accept': _JSON_CONTENT_TYPE})
