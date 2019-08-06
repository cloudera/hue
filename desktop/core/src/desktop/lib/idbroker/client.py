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
from __future__ import absolute_import

from builtins import object
import logging

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.idbroker import conf
from desktop.lib.rest import http_client, resource
from hadoop.core_site import is_kerberos_enabled

LOG = logging.getLogger(__name__)

_KNOX_TOKEN_API = '/knoxtoken/api/v1/token'
_CAB_API_CREDENTIALS_GLOBAL = '/cab/api/v1/credentials'


class IDBroker(object):
  @classmethod
  def from_core_site(cls, fs=None, user=None):
    security = {'type': None}
    if is_kerberos_enabled():
      security['type'] = 'kerberos'
    elif conf.get_cab_username(fs):
      security['type'] = 'basic'
      security['params'] = {'username': conf.get_cab_username(fs), 'password': conf.get_cab_password(fs)}
    return cls(
      user,
      conf.get_cab_address(fs),
      conf.get_cab_dt_path(fs),
      conf.get_cab_path(fs),
      security
    )


  def __init__(self, user=None, address=None, dt_path=None, path=None, security=None):
    self.user=user
    self.address=address
    self.dt_path = dt_path
    self.path = path
    self.security = security
    self._client = http_client.HttpClient(self.address, logger=LOG)
    self._root = resource.Resource(self._client)


  def _knox_token_params(self):
    if self.user:
      if self.security['type'] == 'kerberos':
        return { 'doAs': self.user }
      else:
        return { 'user.name': self.user }
    else:
      return None


  def get_auth_token(self):
    if self.security['type'] == 'kerberos':
      self._client.set_kerberos_auth()
    elif self.security['type'] == 'basic':
      self._client.set_basic_auth(self.security['params']['username'], self.security['params']['password'])
    try:
      res = self._root.invoke("GET", self.dt_path + _KNOX_TOKEN_API, self._knox_token_params(), allow_redirects=True, log_response=False) # Can't log response because returns credentials
      return res.get('access_token')
    except Exception as e:
      raise PopupException('Failed to authenticate to IDBroker with error: %s' % e.message)


  def get_cab(self):
    self._client.set_bearer_auth(self.get_auth_token())
    try:
      return self._root.invoke("GET", self.path + _CAB_API_CREDENTIALS_GLOBAL, allow_redirects=True, log_response=False) # Can't log response because returns credentials
    except Exception as e:
      raise PopupException('Failed to obtain storage credentials from IDBroker with error: %s' % e.message)
