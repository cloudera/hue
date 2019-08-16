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

from googleCS import conf
from googleCS.oAuth2 import GoogleOAuth2

LOG = logging.getLogger(__name__)

CLIENT_CACHE = None

def get_client(identifier='default', user=None):
  global CLIENT_CACHE
  _init_clients()
  if identifier not in CLIENT_CACHE["googlefs"]:
    raise ValueError('Unknown google client: %s, check your configuration' % identifier)
  return CLIENT_CACHE["google"][identifier]

def _init_clients():
  global CLIENT_CACHE
  if CLIENT_CACHE is not None:
    return
  CLIENT_CACHE = {}
  CLIENT_CACHE["google"] = {}
  for identifier in list(conf.GOOGLE_ACCOUNTS.keys()):
    CLIENT_CACHE["google"][identifier] = _make_azure_client(identifier)

def _make_google_client(identifier):
  client_conf = conf.GOOGLE_ACCOUNTS[identifier]
  return GoogleOAuth2.from_config(client_conf)