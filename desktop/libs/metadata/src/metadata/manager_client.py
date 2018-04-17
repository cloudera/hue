#!/usr/bin/env python
# -- coding: utf-8 --
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

from django.core.cache import cache
from django.utils.translation import ugettext as _

from desktop.lib.rest.http_client import RestException, HttpClient

from metadata.conf import MANAGER
from desktop.lib.rest.resource import Resource
from metadata.manager_api import ManagerApiException


LOG = logging.getLogger(__name__)
VERSION = 'v19'


class ManagerApi(object):
  """
  https://cloudera.github.io/cm_api/
  """

  def __init__(self, user=None, security_enabled=False, ssl_cert_ca_verify=False):
    self._api_url = '%s/%s' % (MANAGER.API_URL.get().strip('/'), VERSION)
    self._username = 'hue' #get_navigator_auth_username()
    self._password = 'hue' #get_navigator_auth_password()

    self.user = user
    self._client = HttpClient(self._api_url, logger=LOG)

    if security_enabled:
      self._client.set_kerberos_auth()
    else:
      self._client.set_basic_auth(self._username, self._password)

    self._client.set_verify(ssl_cert_ca_verify)
    self._root = Resource(self._client)


  def tools_echo(self):
    try:
      params = (
        ('message', 'hello'),
      )

      LOG.info(params)
      return self._root.get('tools/echo', params=params)
    except RestException, e:
      LOG.error('Failed to search for entities with search query')
      raise ManagerApiException(e)
