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

from builtins import str, object
import logging
import os
import boto

from aws import conf as aws_conf
from aws.s3.s3connection import url_client_connect_to_region, RazS3Connection
from aws.s3.s3fs import S3FileSystem, S3FileSystemException

from desktop.lib.idbroker import conf as conf_idbroker
from desktop.lib.idbroker.client import IDBroker

from hadoop.core_site import get_raz_s3_default_bucket

LOG = logging.getLogger(__name__)


HTTP_SOCKET_TIMEOUT_S = 60


def get_credential_provider(identifier, user):
  client_conf = aws_conf.AWS_ACCOUNTS[identifier] if identifier in aws_conf.AWS_ACCOUNTS else None
  return CredentialProviderIDBroker(IDBroker.from_core_site('s3a', user)) if conf_idbroker.is_idbroker_enabled('s3a') \
      else CredentialProviderConf(client_conf)


def _make_client(identifier, user):
  client_conf = aws_conf.AWS_ACCOUNTS[identifier] if identifier in aws_conf.AWS_ACCOUNTS else None

  if aws_conf.is_raz_s3():
    host = aws_conf.get_default_host() or client_conf.HOST.get()
    s3_client = RazS3Connection(username=user, host=host)  # Note: Remaining AWS configuration is fully skipped
    s3_client_expiration = None
  else:
    s3_client_builder = Client.from_config(client_conf, get_credential_provider(identifier, user))
    s3_client = s3_client_builder.get_s3_connection()
    s3_client_expiration = s3_client_builder.expiration

  return S3FileSystem(s3_client, s3_client_expiration)


class CredentialProviderConf(object):
  def __init__(self, conf):
    self._conf = conf

  def validate(self):
    credentials = self.get_credentials()
    if None in (credentials.get('AccessKeyId'), credentials.get('SecretAccessKey')) and not credentials.get('AllowEnvironmentCredentials') \
        and not aws_conf.has_iam_metadata():
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
        'SecretAccessKey': self._conf.get_default_secret_key(),
        'SessionToken': self._conf.get_default_session_token(),
        'AllowEnvironmentCredentials': True
      }


class CredentialProviderIDBroker(object):
  def __init__(self, idbroker):
    self.idbroker = idbroker
    self.credentials = None

  def validate(self):
    return True # Already been validated in config

  def get_credentials(self):
    return self.idbroker.get_cab().get('Credentials')


class Client(object):
  def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, aws_security_token=None, region=None,
               timeout=HTTP_SOCKET_TIMEOUT_S, host=None, proxy_address=None, proxy_port=None, proxy_user=None,
               proxy_pass=None, calling_format=None, is_secure=True, expiration=None):
    self._access_key_id = aws_access_key_id
    self._secret_access_key = aws_secret_access_key
    self._security_token = aws_security_token
    self._region = region.lower() if region else region
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
        region=aws_conf.get_region(conf=conf),
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
        aws_security_token=credentials.get('SessionToken'),
        expiration=credentials.get('Expiration'),
        region=aws_conf.get_region()
      )

  def get_s3_connection(self):
    """S3 connection can actually be seen as a S3Client. A true new client would be a Boto3Client."""
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
      # Use V4 signature support by default
      os.environ['S3_USE_SIGV4'] = 'True'
      if self._host is not None and not aws_conf.IS_SELF_SIGNING_ENABLED.get():
        kwargs.update({'host': self._host})
        connection = boto.s3.connection.S3Connection(**kwargs)
      elif self._region:
        if aws_conf.IS_SELF_SIGNING_ENABLED.get():
          connection = url_client_connect_to_region(self._region, **kwargs)
        else:
          connection = boto.s3.connect_to_region(self._region, **kwargs)
      else:
        kwargs.update({'host': 's3.amazonaws.com'})
        connection = boto.s3.connection.S3Connection(**kwargs)
    except Exception as e:
      LOG.exception(e)
      raise S3FileSystemException('Failed to construct S3 Connection, check configurations for aws.')

    if connection is None:
      # If no connection, attempt to fallback to IAM instance metadata
      connection = boto.connect_s3()

      if connection is None:
        raise S3FileSystemException('Can not construct S3 Connection for region %s' % self._region)

    return connection
