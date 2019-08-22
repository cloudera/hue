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

import logging
import os

import boto.gs.connection

from googleCS import conf
from googleCS.oAuth2 import GoogleOAuth2
from googleCS.gs.gsfs import GSFileSystem

LOG = logging.getLogger(__name__)

HTTP_SOCKET_TIMEOUT_S = 60

CLIENT_CACHE = None

def get_client(identifier='default', user=None):
  global CLIENT_CACHE
  _init_clients()
  if identifier not in CLIENT_CACHE["google"]:
    raise ValueError('Unknown google client: %s, check your configuration' % identifier)
  return CLIENT_CACHE["google"][identifier]

def _init_clients():
  global CLIENT_CACHE
  if CLIENT_CACHE is not None:
    return
  CLIENT_CACHE = {}
  CLIENT_CACHE["google"] = {}
  for identifier in list(conf.GOOGLE_ACCOUNTS.keys()):
    CLIENT_CACHE["google"][identifier] = _make_google_client(identifier)

def _make_google_client(identifier):
  client_conf = conf.GOOGLE_ACCOUNTS[identifier]
  
  client = Client(GoogleOAuth2.from_config(client_conf))
  return GSFileSystem(client.get_google_connection())

class Client(object):
  def __init__(self, authentication_provider = None, timeout = None, host = None, proxy_address=None, proxy_port=None, proxy_user=None,
               proxy_pass=None,  is_secure = True, expiration = None):
    self._authentication_provider = authentication_provider
    self._timeout = timeout
    self._host = host
    self._proxy_address = proxy_address
    self._proxy_port = proxy_port
    self._proxy_user = proxy_user
    self._proxy_pass = proxy_pass
    self._proxy_address = proxy_address
    self._is_secure = is_secure
    self.expiration = expiration

    if not boto.config.has_section('Boto'):
      boto.config.add_section('Boto')

    if not boto.config.get('Boto', 'http_socket_timeout'):
      boto.config.set('Boto', 'http_socket_timeout', str(self._timeout))
      
  
  def get_google_connection(self):
    if self._authentication_provider._token is None:
      self._authentication_provider.get_token()
    
    kwargs = {
      'gs_access_key_id': self._authentication_provider._access_key_id,
      'gs_secret_access_key': self._authentication_provider._secret_access_key,
      'security_token': self._authentication_provider._token,
      'is_secure': self._is_secure,
    }
      
    # Add proxy if configured
    if self._proxy_address is not None:
      kwargs.update({'proxy': self._proxy_address})
      if self._proxy_port is not None:
        kwargs.update({'proxy_port': self._proxy_port})
      if self._proxy_user is not None:
        kwargs.update({'proxy_user': self._proxy_user})
      if self._proxy_pass is not None:
        kwargs.update({'proxy_pass': self._proxy_pass})
      
    # Attempt to create S3 connection based on configured credentials and host or region first, then fallback to IAM
    try:
      if self._host is not None:
        # Use V4 signature support by default
        kwargs.update({'host': self._host})
        connection = boto.gs.connection.GSConnection(**kwargs)
      else:
        kwargs.update({'host': 'storage.googleapis.com'})
        connection = boto.gs.connection.GSConnection(**kwargs)
    except Exception as e:
      LOG.exception(e)
      raise e

    if connection is None:
      # If no connection, attemt to fallback to IAM instance metadata
      connection = boto.connect_gs()

      if connection is None:
        raise RuntimeError

    return connection
    