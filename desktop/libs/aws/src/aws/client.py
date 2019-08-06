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

from builtins import str
from builtins import object
import datetime
import logging
import os

import boto.s3.connection

from aws import conf as aws_conf
from aws.s3.s3fs import S3FileSystemException
from aws.s3.s3fs import S3FileSystem

from desktop.conf import DEFAULT_USER
from desktop.lib.idbroker import conf as conf_idbroker
from desktop.lib.idbroker.client import IDBroker

LOG = logging.getLogger(__name__)

HTTP_SOCKET_TIMEOUT_S = 60

CLIENT_CACHE = None

_DEFAULT_USER = DEFAULT_USER.get()

# FIXME: Should we check hue principal for the default user?
def _get_cache_key(identifier='default', user=_DEFAULT_USER): # FIXME: Caching via username has issues when users get deleted. Need to switch to userid, but bigger change
  return identifier + ':' + user


def clear_cache():
  global CLIENT_CACHE
  CLIENT_CACHE = None


def current_ms_from_utc():
  return (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000


def get_client(identifier='default', user=_DEFAULT_USER):
  global CLIENT_CACHE
  _init_clients()

  cache_key = _get_cache_key(identifier, user) if conf_idbroker.is_idbroker_enabled('s3a') else _get_cache_key(identifier) # We don't want to cache by username when IDBroker not enabled
  client = CLIENT_CACHE.get(cache_key)

  if client and (client.expiration is None or client.expiration > int(current_ms_from_utc())): # expiration from IDBroker returns java timestamp in MS
    return client
  else:
    client = _make_client(identifier, user)
    CLIENT_CACHE[cache_key] = client
    return client

def get_credential_provider(identifier='default', user=_DEFAULT_USER):
  client_conf = aws_conf.AWS_ACCOUNTS[identifier] if identifier in aws_conf.AWS_ACCOUNTS else None
  return CredentialProviderIDBroker(IDBroker.from_core_site('s3a', user)) if conf_idbroker.is_idbroker_enabled('s3a') else CredentialProviderConf(client_conf)


def _init_clients():
  global CLIENT_CACHE
  if CLIENT_CACHE is not None:
    return
  CLIENT_CACHE = {} # Can't convert this to django cache, because S3FileSystem is not pickable
  if conf_idbroker.is_idbroker_enabled('s3a'):
    return # No default initializations when IDBroker is enabled
  for identifier in list(aws_conf.AWS_ACCOUNTS.keys()):
    CLIENT_CACHE[_get_cache_key(identifier)] = _make_client(identifier)
  # If default configuration not initialized, initialize client connection with IAM metadata
  if not CLIENT_CACHE.has_key(_get_cache_key()) and aws_conf.has_iam_metadata():
    CLIENT_CACHE[_get_cache_key()] = _make_client('default')


def _make_client(identifier, user=_DEFAULT_USER):
  client_conf = aws_conf.AWS_ACCOUNTS[identifier] if identifier in aws_conf.AWS_ACCOUNTS else None

  client = Client.from_config(client_conf, get_credential_provider(identifier, user))
  return S3FileSystem(client.get_s3_connection(), client.expiration) # It would be nice if the connection is lazy loaded


class CredentialProviderConf(object):
  def __init__(self, conf):
    self._conf=conf

  def validate(self):
    credentials = self.get_credentials()
    if None in (credentials.get('AccessKeyId'), credentials.get('SecretAccessKey')) and not credentials.get('AllowEnvironmentCredentials') and not aws_conf.has_iam_metadata():
      raise ValueError('Can\'t create AWS client, credential is not configured')
    return True

  def get_credentials(self):
    if self._conf:
      return {
         'AccessKeyId': self._conf.ACCESS_KEY_ID.get(),
         'SecretAccessKey': self._conf.SECRET_ACCESS_KEY.get(),
         'SessionToken': self._conf.SECURITY_TOKEN.get(),
         'AllowEnvironmentCredentials': self._conf.ALLOW_ENVIRONMENT_CREDENTIALS.get()
      }
    else:
      return {
        'AccessKeyId': self._conf.ACCESS_KEY_ID.get(),
        'SecretAccessKey':self._conf.get_default_secret_key(),
        'SessionToken': self._conf.get_default_session_token(),
        'AllowEnvironmentCredentials': True
      }


class CredentialProviderIDBroker(object):
  def __init__(self, idbroker):
    self.idbroker=idbroker
    self.credentials = None

  def validate(self):
    return True # Already been validated in config

  def get_credentials(self):
    return self.idbroker.get_cab().get('Credentials')


class Client(object):
  def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, aws_security_token=None, region=aws_conf.AWS_ACCOUNT_REGION_DEFAULT,
               timeout=HTTP_SOCKET_TIMEOUT_S, host=None, proxy_address=None, proxy_port=None, proxy_user=None,
               proxy_pass=None, calling_format=None, is_secure=True, expiration=None):
    self._access_key_id = aws_access_key_id
    self._secret_access_key = aws_secret_access_key
    self._security_token = aws_security_token
    self._region = region.lower()
    self._timeout = timeout
    self._host = host
    self._proxy_address = proxy_address
    self._proxy_port = proxy_port
    self._proxy_user = proxy_user
    self._proxy_pass = proxy_pass
    self._calling_format = aws_conf.DEFAULT_CALLING_FORMAT if calling_format is None else calling_format
    self._is_secure = is_secure
    self.expiration = expiration

    if not boto.config.has_section('Boto'):
      boto.config.add_section('Boto')

    if not boto.config.get('Boto', 'http_socket_timeout'):
      boto.config.set('Boto', 'http_socket_timeout', str(self._timeout))

  @classmethod
  def from_config(cls, conf, credential_provider):
    credential_provider.validate()
    credentials = credential_provider.get_credentials()

    if conf:
      return cls(
        aws_access_key_id=credentials.get('AccessKeyId'),
        aws_secret_access_key=credentials.get('SecretAccessKey'),
        aws_security_token=credentials.get('SessionToken'),
        region=aws_conf.get_default_region(),
        host=conf.HOST.get(),
        proxy_address=conf.PROXY_ADDRESS.get(),
        proxy_port=conf.PROXY_PORT.get(),
        proxy_user=conf.PROXY_USER.get(),
        proxy_pass=conf.PROXY_PASS.get(),
        calling_format=conf.CALLING_FORMAT.get(),
        is_secure=conf.IS_SECURE.get(),
        expiration=credentials.get('Expiration')
      )
    else:
      return cls(
        aws_access_key_id=credentials.get('AccessKeyId'),
        aws_secret_access_key=credentials.get('SecretAccessKey'),
        aws_security_token=credentials.get('SessionToken')
      )

  def get_s3_connection(self):

    kwargs = {
      'aws_access_key_id': self._access_key_id,
      'aws_secret_access_key': self._secret_access_key,
      'security_token': self._security_token,
      'is_secure': self._is_secure,
      'calling_format': self._calling_format
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
        os.environ['S3_USE_SIGV4'] = 'True'
        kwargs.update({'host': self._host})
        connection = boto.s3.connection.S3Connection(**kwargs)
      elif self._region:
        connection = boto.s3.connect_to_region(self._region,
                                             aws_access_key_id=self._access_key_id,
                                             aws_secret_access_key=self._secret_access_key,
                                             security_token=self._security_token)
      else:
        kwargs.update({'host': 's3.amazonaws.com'})
        connection = boto.s3.connection.S3Connection(**kwargs)
    except Exception as e:
      LOG.exception(e)
      raise S3FileSystemException('Failed to construct S3 Connection, check configurations for aws.')

    if connection is None:
      # If no connection, attemt to fallback to IAM instance metadata
      connection = boto.connect_s3()

      if connection is None:
        raise S3FileSystemException('Can not construct S3 Connection for region %s' % self._region)

    return connection
