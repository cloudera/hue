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

from azure import conf
from azure.adls.webhdfs import WebHdfs
from azure.abfs.abfs import ABFS
from azure.active_directory import ActiveDirectory

from desktop.lib.idbroker import conf as conf_idbroker
from desktop.lib.idbroker.client import IDBroker


LOG = logging.getLogger(__name__)


def _make_adls_client(identifier, user):
  auth_provider = get_credential_provider(identifier, user)
  client_conf = conf.ADLS_CLUSTERS[identifier]

  return WebHdfs.from_config(client_conf, auth_provider)

def _make_abfs_client(identifier, user):
  auth_provider = get_credential_provider(identifier, user, version='v2.0')
  client_conf = conf.ABFS_CLUSTERS[identifier]

  return ABFS.from_config(client_conf, auth_provider)

def get_credential_provider(identifier, user, version=None):
  from desktop.conf import RAZ
  if RAZ.IS_ENABLED.get():
    return RazCredentialProvider(username=user)
  else:
    client_conf = conf.AZURE_ACCOUNTS[identifier] if identifier in conf.AZURE_ACCOUNTS else None
    return CredentialProviderIDBroker(IDBroker.from_core_site('azure', user)) if conf_idbroker.is_idbroker_enabled('azure') \
        else CredentialProviderAD(ActiveDirectory.from_config(client_conf, version=version))


class CredentialProviderAD(object):
  def __init__(self, ad):
    self.ad = ad

  def get_credentials(self):
    return self.ad.get_token()

class CredentialProviderIDBroker(object):
  def __init__(self, idbroker):
    self.idbroker = idbroker

  def get_credentials(self):
    return self.idbroker.get_cab()

class RazCredentialProvider(object):
  def __init__(self, username):
    self.username = username

  def get_credentials(self):
    # No credentials are required
    return {'username': self.username}
