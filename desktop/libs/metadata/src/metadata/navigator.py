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

from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest import resource

from metadata.conf import NAVIGATOR


LOG = logging.getLogger(__name__)


class NavigatorApiException(Exception):
  pass


class NavigatorApi(object):
  """
  http://cloudera.github.io/navigator/apidocs/v2/index.html
  """

  def __init__(self, api_url=None, user=None, password=None):
    self._api_url = (api_url or NAVIGATOR.API_URL.get()).strip('/')
    self._username = user or NAVIGATOR.AUTH_USERNAME.get()
    self._password = password or NAVIGATOR.AUTH_PASSWORD.get()

    self._client = HttpClient(self._api_url, logger=LOG)
    self._client.set_basic_auth(self._username, self._password)
    self._root = resource.Resource(self._client)

    self.__headers = {}
    self.__params = ()


  def find_entity(self, type, name):
    """
    GET /api/v2/interactive/entities?query=((originalName:<name>)AND(type:<type>))
    http://cloudera.github.io/navigator/apidocs/v2/path__v2_interactive_entities.html
    """
    try:
      params = self.__params
      filter_query = '((originalName:%(name)s)AND(type:%(type)s))' % {'name': name, 'type': type}
      params += (
        ('query', filter_query),
        ('offset', 0),
      )

      response = self._root.get('interactive/entities', headers=self.__headers, params=params)
      if response['totalMatched'] == 0:
        raise NavigatorApiException('Could not find entity with type %s and name %s') % (type, name)
      elif response['totalMatched'] > 1:
        raise NavigatorApiException('Found more than 1 entity with type %s and name %s') % (type, name)
      else:
        return response['results'][0]

    except RestException, e:
      raise NavigatorApiException('Failed to find entity with type %s and name %s: %s' % (type, name, str(e)))
