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

import boto
import boto.s3
import boto.s3.connection
import boto.utils

from aws.conf import get_default_region, has_iam_metadata, DEFAULT_CALLING_FORMAT, AWS_ACCOUNT_REGION_DEFAULT
from aws.s3.s3fs import S3FileSystemException


LOG = logging.getLogger(__name__)


HTTP_SOCKET_TIMEOUT_S = 60


class Client(object):
  def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, aws_security_token=None, region=AWS_ACCOUNT_REGION_DEFAULT,
               timeout=HTTP_SOCKET_TIMEOUT_S, host=None, proxy_address=None, proxy_port=None, proxy_user=None,
               proxy_pass=None, calling_format=None, is_secure=True):
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
    self._calling_format = DEFAULT_CALLING_FORMAT if calling_format is None else calling_format
    self._is_secure = is_secure

    if not boto.config.has_section('Boto'):
      boto.config.add_section('Boto')

    if not boto.config.get('Boto', 'http_socket_timeout'):
      boto.config.set('Boto', 'http_socket_timeout', str(self._timeout))

  @classmethod
  def from_config(cls, conf):
    access_key_id = conf.ACCESS_KEY_ID.get()
    secret_access_key = conf.SECRET_ACCESS_KEY.get()
    security_token = conf.SECURITY_TOKEN.get()
    env_cred_allowed = conf.ALLOW_ENVIRONMENT_CREDENTIALS.get()

    if None in (access_key_id, secret_access_key) and not env_cred_allowed and not has_iam_metadata():
      raise ValueError('Can\'t create AWS client, credential is not configured')

    return cls(
      aws_access_key_id=access_key_id,
      aws_secret_access_key=secret_access_key,
      aws_security_token=security_token,
      region=get_default_region(),
      host=conf.HOST.get(),
      proxy_address=conf.PROXY_ADDRESS.get(),
      proxy_port=conf.PROXY_PORT.get(),
      proxy_user=conf.PROXY_USER.get(),
      proxy_pass=conf.PROXY_PASS.get(),
      calling_format=conf.CALLING_FORMAT.get(),
      is_secure=conf.IS_SECURE.get()
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
    except Exception, e:
      LOG.exception(e)
      raise S3FileSystemException('Failed to construct S3 Connection, check configurations for aws.')

    if connection is None:
      # If no connection, attemt to fallback to IAM instance metadata
      connection = boto.connect_s3()

      if connection is None:
        raise S3FileSystemException('Can not construct S3 Connection for region %s' % self._region)

    return connection
