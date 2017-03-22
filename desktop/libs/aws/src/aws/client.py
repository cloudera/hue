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

import boto
import boto.s3
import boto.s3.connection
import boto.utils

from aws.conf import get_default_region, has_iam_metadata, DEFAULT_CALLING_FORMAT


HTTP_SOCKET_TIMEOUT_S = 60


class Client(object):
  def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, aws_security_token=None, region=None,
               timeout=HTTP_SOCKET_TIMEOUT_S, proxy_address=None,
               proxy_port=None, calling_format=None, is_secure=True):
    self._access_key_id = aws_access_key_id
    self._secret_access_key = aws_secret_access_key
    self._security_token = aws_security_token
    self._region = region.lower() if region else get_default_region()
    self._timeout = timeout
    self._proxy_address = proxy_address
    self._proxy_port = proxy_port
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
      region=conf.REGION.get(),
      proxy_address=conf.PROXY_ADDRESS.get(),
      proxy_port=conf.PROXY_PORT.get(),
      calling_format=conf.CALLING_FORMAT.get(),
      is_secure=conf.IS_SECURE.get()
    )

  def get_s3_connection(self):
    # First attempt to connect via specified credentials
    if self._proxy_address is not None and self._proxy_port is not None:
      connection = boto.s3.connection.S3Connection(aws_access_key_id=self._access_key_id,
        aws_secret_access_key=self._secret_access_key,
        security_token=self._security_token,
        is_secure=self._is_secure,
        calling_format=self._calling_format,
        proxy=self._proxy_address,
        proxy_port=self._proxy_port)
    elif self._region:
      connection = boto.s3.connect_to_region(self._region,
        aws_access_key_id=self._access_key_id,
        aws_secret_access_key=self._secret_access_key,
        security_token=self._security_token)
    else:
      connection = boto.s3.connection.S3Connection(aws_access_key_id=self._access_key_id,
        aws_secret_access_key=self._secret_access_key,
        security_token=self._security_token)

    if connection is None:
      # If no connection, attemt to fallback to IAM instance metadata
      connection = boto.connect_s3()

      if connection is None:
        raise ValueError('Can not construct S3 Connection for region %s' % self._region)

    return connection
