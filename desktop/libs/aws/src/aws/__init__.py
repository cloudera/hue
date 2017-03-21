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

from aws import conf
from aws.client import Client
from aws.s3.s3fs import S3FileSystem

CLIENT_CACHE = None


def get_client(identifier='default'):
  global CLIENT_CACHE
  _init_clients()
  if identifier not in CLIENT_CACHE:
    raise ValueError('Unknown AWS client: %s, check your configuration' % identifier)
  return CLIENT_CACHE[identifier]


def _init_clients():
  global CLIENT_CACHE
  if CLIENT_CACHE is not None:
    return
  CLIENT_CACHE = {}
  for identifier in conf.AWS_ACCOUNTS.keys():
    CLIENT_CACHE[identifier] = _make_client(identifier)
  # If default configuration not initialized, initialize client connection with IAM metadata
  if 'default' not in CLIENT_CACHE and conf.has_iam_metadata():
    CLIENT_CACHE['default'] = Client()


def _make_client(identifier):
  client_conf = conf.AWS_ACCOUNTS[identifier]
  return Client.from_config(client_conf)


def get_s3fs(identifier='default'):
  connection = get_client(identifier).get_s3_connection()
  return S3FileSystem(connection)
