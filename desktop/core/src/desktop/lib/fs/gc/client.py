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
LOG = logging.getLogger()

try:
  import gcs_oauth2_boto_plugin
except ImportError:
  LOG.warning('gcs_oauth2_boto_plugin module not found')
import json

from boto.auth_handler import AuthHandler, NotReadyToAuthenticate
from boto.gs.bucket import Bucket
from boto.gs.connection import GSConnection
from boto.provider import Provider
from boto.s3.connection import SubdomainCallingFormat

from desktop import conf
from desktop.lib.idbroker import conf as conf_idbroker
from desktop.lib.idbroker.client import IDBroker
from desktop.lib.fs.gc.gs import GSFileSystem


def get_credential_provider(config, user):
  return CredentialProviderIDBroker(IDBroker.from_core_site('gs', user)) if conf_idbroker.is_idbroker_enabled('gs') else \
      CredentialProviderConf(config)


def _make_client(identifier, user):
  config = conf.GC_ACCOUNTS[identifier] if identifier in list(conf.GC_ACCOUNTS.keys()) else None
  client = Client.from_config(config, get_credential_provider(config, user))

  return GSFileSystem(
    client.get_s3_connection(),
    client.expiration,
    headers={"x-goog-project-id": client.project},
  )  # It would be nice if the connection was lazy loaded


class Client(object):

  def __init__(self, json_credentials=None, expiration=None):
    self.project = json_credentials.get('project_id') if json_credentials else None
    self.json_credentials = json_credentials
    self.expiration = expiration

  @classmethod
  def from_config(cls, config, credential_provider):
    credentials = credential_provider.get_credentials()
    return Client(json_credentials=credentials.get('JsonCredentials'), expiration=credentials.get('Expiration', 0))

  def get_s3_connection(self):
    return HueGSConnection(provider=HueProvider('google', json_credentials=self.json_credentials))


# Boto looks at subclasses of boto.auth_handler.AuthHandler and checks if they can authenticate.
# The subclasses provided by gcs_oauth2_boto_plugin.oauth2_plugin are designed to work with files, but we want to programmatically
# configure the auth.
class OAuth2JsonServiceAccountClientAuth(AuthHandler):
  """AuthHandler for working with OAuth2 service account credentials."""

  capability = ['google-oauth2', 's3']

  def __init__(self, path, config, provider):
    if provider.name == 'google':
      self.oauth2_client = gcs_oauth2_boto_plugin.oauth2_client.OAuth2JsonServiceAccountClient(provider.get_json_credentials())
      global IS_SERVICE_ACCOUNT
      IS_SERVICE_ACCOUNT = True
    else:
      raise NotReadyToAuthenticate()

  def add_auth(self, http_request):
    http_request.headers['Authorization'] = (self.oauth2_client.GetAuthorizationHeader())


class HueProvider(Provider):
  def __init__(self, name, json_credentials=None, access_key=None, secret_key=None,
      security_token=None, profile_name=None):
    self.json_credentials = json_credentials
    super(HueProvider, self).__init__(
        name, access_key=access_key, secret_key=secret_key,
        security_token=security_token, profile_name=profile_name
    )

  def get_json_credentials(self):
    return self.json_credentials


# Custom GSConnection to be able to add our own credential provider. This is missing on GSConnection, but not S3Connection
class HueGSConnection(GSConnection):

  def __init__(self, gs_access_key_id=None, gs_secret_access_key=None,
      is_secure=True, port=None, proxy=None, proxy_port=None,
      proxy_user=None, proxy_pass=None,
      host=GSConnection.DefaultHost, debug=0, https_connection_factory=None,
      calling_format=SubdomainCallingFormat(), path='/',
      suppress_consec_slashes=True, provider="google"):

    super(GSConnection, self).__init__(
        gs_access_key_id, gs_secret_access_key,
        is_secure, port, proxy, proxy_port, proxy_user, proxy_pass,
        host, debug, https_connection_factory, calling_format, path,
        provider, Bucket,
        suppress_consec_slashes=suppress_consec_slashes
    )


class CredentialProviderConf(object):

  def __init__(self, conf):
    self._conf=conf

  def validate(self):
    credentials = self.get_credentials()
    if credentials.get('JsonCredentials') and not credentials.get('AllowEnvironmentCredentials') and not credentials.get('HasIamMetadata'):
      raise ValueError('Can\'t create GS client, credential is not configured')
    return True

  def get_credentials(self):
    if self._conf:
      return {
        'JsonCredentials': json.loads(self._conf.JSON_CREDENTIALS.get()),
        'AllowEnvironmentCredentials': False,
        'HasIamMetadata': False
      }
    else:
      return {
        'JsonCredentials': None,
        'AllowEnvironmentCredentials': False,
        'HasIamMetadata': False
      }


class CredentialProviderIDBroker(object):

  def __init__(self, idbroker):
    self.idbroker=idbroker
    self.credentials = None

  def validate(self):
    return True # Already been validated in config

  def get_credentials(self):
    return self.idbroker.get_cab().get('Credentials')
