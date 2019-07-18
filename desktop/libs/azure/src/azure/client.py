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

from azure import conf
from azure.adls.webhdfs import WebHdfs
from azure.abfs.abfs import ABFS
from azure.active_directory import ActiveDirectory

LOG = logging.getLogger(__name__)

CLIENT_CACHE = None

def get_client(identifier='default', user=None):
  global CLIENT_CACHE
  _init_clients()
  if identifier not in CLIENT_CACHE["adls"]:
    raise ValueError('Unknown azure client: %s, check your configuration' % identifier)
  return CLIENT_CACHE["adls"][identifier]

def get_client_abfs(identifier='default', user=None):
  global CLIENT_CACHE
  _init_clients()
  if identifier not in CLIENT_CACHE["abfs"]:
    raise ValueError('Unknown azure client: %s, check your configuration' % identifier)
  return CLIENT_CACHE["abfs"][identifier]

def _init_clients():
  global CLIENT_CACHE
  if CLIENT_CACHE is not None:
    return
  CLIENT_CACHE = {}
  CLIENT_CACHE["azure"] = {}
  CLIENT_CACHE["adls"] = {}
  CLIENT_CACHE["abfs"] = {}
  for identifier in list(conf.AZURE_ACCOUNTS.keys()):
    CLIENT_CACHE["azure"][identifier] = _make_azure_client(identifier)

  for identifier in list(conf.ADLS_CLUSTERS.keys()):
    CLIENT_CACHE["adls"][identifier] = _make_adls_client(identifier)

  for identifier in list(conf.ABFS_CLUSTERS.keys()):
    CLIENT_CACHE["abfs"][identifier] = _make_abfs_client(identifier)

def _make_adls_client(identifier):
  client_conf = conf.ADLS_CLUSTERS[identifier]
  azure_client = CLIENT_CACHE["azure"][identifier]
  return WebHdfs.from_config(client_conf, azure_client)

def _make_abfs_client(identifier):
  client_conf = conf.ABFS_CLUSTERS[identifier]
  azure_client = CLIENT_CACHE["azure"][identifier]
  return ABFS.from_config(client_conf, azure_client)

def _make_azure_client(identifier):
  client_conf = conf.AZURE_ACCOUNTS[identifier]
  return ActiveDirectory.from_config(client_conf)