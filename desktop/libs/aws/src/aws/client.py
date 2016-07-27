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


HTTP_SOCKET_TIMEOUT_S = 60


class Client(object):
  def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region=None, timeout=HTTP_SOCKET_TIMEOUT_S):
    self._access_key_id = aws_access_key_id
    self._secret_access_key = aws_secret_access_key
    self._region = region
    self._timeout = timeout

    boto.config.add_section('Boto')
    boto.config.set('Boto', 'http_socket_timeout', str(self._timeout))

  @classmethod
  def from_config(cls, conf):
    access_key_id = conf.ACCESS_KEY_ID.get()
    secret_access_key = conf.SECRET_ACCESS_KEY.get()
    env_cred_allowed = conf.ALLOW_ENVIRONMENT_CREDENTIALS.get()

    if None in (access_key_id, secret_access_key) and not env_cred_allowed:
      raise ValueError('Can\'t create AWS client, credential is not configured')

    return cls(
      aws_access_key_id=conf.ACCESS_KEY_ID.get(),
      aws_secret_access_key=conf.SECRET_ACCESS_KEY.get(),
      region=conf.REGION.get()
    )

  def get_s3_connection(self):
    connection = boto.s3.connect_to_region(self._region,
                                           aws_access_key_id=self._access_key_id,
                                           aws_secret_access_key=self._secret_access_key)
    if connection is None:
      raise ValueError('Can not construct S3 Connection for region %s' % self._region)
    return connection