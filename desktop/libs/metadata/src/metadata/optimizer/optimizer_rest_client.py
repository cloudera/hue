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

import json
import logging
import sys

from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from metadata.conf import OPTIMIZER, get_optimizer_url
from metadata.optimizer.optimizer_client import OptimizerClient

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)
_JSON_CONTENT_TYPE = 'application/json'


class OptimizerRestClient(OptimizerClient):

  def __init__(self, user, api_url=None, auth_key=None, auth_key_secret=None, tenant_id='hue'):
    self.user = user
    self._tenant_id = tenant_id

    self._api_url = (api_url or get_optimizer_url()).strip('/')
    self._client = HttpClient(self._api_url, logger=LOG)
    self._root = Resource(self._client)

    self._api = MockApiLib()


  def _call(self, path, data):
    try:
      return self._root.post(path, data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    except:
      LOG.exception('Error calling Optimize service')
      return {}


class MockApiLib():

  def call_api(self, *params):
    LOG.info('Mocking %s' % str(params))
    return '{}'
