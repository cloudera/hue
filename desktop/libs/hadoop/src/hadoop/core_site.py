#!/usr/bin/env python
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
import errno
import logging
import re
import sys

from hadoop import conf
from hadoop import confparse

from desktop.lib.paths import get_config_root_hadoop

if sys.version_info[0] > 2:
  open_file = open
else:
  open_file = file

__all = ['get_conf', 'get_trash_interval', 'get_s3a_access_key', 'get_s3a_secret_key']

LOG = logging.getLogger(__name__)

_CORE_SITE_PATH = None                  # Path to core-site.xml
_CORE_SITE_DICT = None                  # A dictionary of name/value config options

_CNF_TRASH_INTERVAL = 'fs.trash.interval'
_CNF_S3A_ACCESS_KEY = 'fs.s3a.access.key'
_CNF_S3A_SECRET_KEY = 'fs.s3a.secret.key'
_CNF_S3A_SESSION_TOKEN = 'fs.s3a.session.token'

_CNF_S3A_RAZ_API_URL = 'fs.s3a.ext.raz.rest.host.url'
_CNF_S3A_RAZ_CLUSTER_NAME = 'fs.s3a.ext.raz.s3.access.cluster.name'
_CNF_S3A_RAZ_BUCKET_ENDPOINT = 'fs.s3a.bucket.(?P<bucket>[^.]+).endpoint'

_CNF_ADLS_RAZ_API_URL = 'fs.azure.ext.raz.rest.host.url'
_CNF_ADLS_RAZ_CLUSTER_NAME = 'fs.azure.ext.raz.adls.access.cluster.name'

_CNF_DEFAULT_FS = 'fs.defaultFS'

_CNF_ADLS_CLIENT_ID = 'dfs.adls.oauth2.client.id'
_CNF_ADLS_AUTHENTICATION_CODE = 'dfs.adls.oauth2.credential'
_CNF_ADLS_REFRESH_URL = 'dfs.adls.oauth2.refresh.url'
_CNF_ADLS_GRANT_TYPE = 'dfs.adls.oauth2.access.token.provider.type'

_CNF_AZURE_CLIENT_ID = 'fs.azure.account.oauth2.client.id'
_CNF_AZURE_CLIENT_SECRET = 'fs.azure.account.oauth2.client.secret'
_CNF_AZURE_CLIENT_ENDPOINT = 'fs.azure.account.oauth2.client.endpoint'

_CNF_SECURITY = 'hadoop.security.authentication'

def reset():
  """Reset the cached conf"""
  global _CORE_SITE_DICT
  _CORE_SITE_DICT = None


def get_conf():
  """get_conf() ->  ConfParse object for core-site.xml"""
  if _CORE_SITE_DICT is None:
    _parse_core_site()
  return _CORE_SITE_DICT


def _parse_core_site():
  """
  Parse core-site.xml and store in _CORE_SITE_DICT
  """
  global _CORE_SITE_DICT
  global _CORE_SITE_PATH

  try:
    _CORE_SITE_PATH = get_config_root_hadoop('core-site.xml')
    data = open_file(_CORE_SITE_PATH, 'r').read()
  except IOError as err:
    if err.errno != errno.ENOENT:
      LOG.error('Cannot read from "%s": %s' % (_CORE_SITE_PATH, err))
      return
    # Keep going and make an empty ConfParse
    data = ""

  _CORE_SITE_DICT = confparse.ConfParse(data)


def get_trash_interval():
  """
  Get trash interval

  Also indicates whether trash is enabled or not.
  """
  return get_conf().get(_CNF_TRASH_INTERVAL, 0)

def get_s3a_access_key():
  """
  Get S3A AWS access key ID
  https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html
  """
  return get_conf().get(_CNF_S3A_ACCESS_KEY)

def get_s3a_secret_key():
  """
  Get S3A AWS secret key
  https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html
  """
  return get_conf().get(_CNF_S3A_SECRET_KEY)

def get_s3a_session_token():
  return get_conf().get(_CNF_S3A_SESSION_TOKEN)


def get_raz_api_url():
  """
  Get Raz API.
  """
  s3a_raz_url = get_conf().get(_CNF_S3A_RAZ_API_URL)
  adls_raz_url = get_conf().get(_CNF_ADLS_RAZ_API_URL)

  if s3a_raz_url != adls_raz_url:
    LOG.warning('Raz API: S3A and ADLS URLs are different')

  return s3a_raz_url or adls_raz_url

def get_raz_cluster_name():
  """
  Get the name of the Cluster where Raz is running.
  """
  return get_conf().get(_CNF_S3A_RAZ_CLUSTER_NAME, '') or get_conf().get(_CNF_ADLS_RAZ_CLUSTER_NAME, '')

def get_raz_s3_default_bucket():
  """
  Get the name of the default S3 bucket of Raz
  """

  for key, val in get_conf().items():
    match = re.search(_CNF_S3A_RAZ_BUCKET_ENDPOINT, key)
    if match:
      return {
        'host': val,
        'bucket': match.group('bucket')
      }

def get_default_fs():
  return get_conf().get(_CNF_DEFAULT_FS)

def get_adls_client_id():
  """
  Get ADLS client id
  https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html
  """
  return get_conf().get(_CNF_ADLS_CLIENT_ID)

def get_adls_authentication_code():
  """
  Get ADLS secret key
  https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html
  """
  return get_conf().get(_CNF_ADLS_AUTHENTICATION_CODE)

def get_adls_refresh_url():
  """
  Get ADLS secret key
  https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html
  """
  return get_conf().get(_CNF_ADLS_REFRESH_URL)

def get_adls_grant_type():
  """
  Get ADLS provider type
  https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html
  """
  return get_conf().get(_CNF_ADLS_GRANT_TYPE)

def is_kerberos_enabled():
  return get_conf().get(_CNF_SECURITY) == 'kerberos'

def get_azure_client_id():
  return get_conf().get(_CNF_AZURE_CLIENT_ID)

def get_azure_client_secret():
  return get_conf().get(_CNF_AZURE_CLIENT_SECRET)

def get_azure_client_endpoint():
  return get_conf().get(_CNF_AZURE_CLIENT_ENDPOINT)
