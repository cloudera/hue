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

import errno
import logging
import os.path

from impala import conf

LOG = logging.getLogger(__name__)

_IMPALA_FLAGS = None

_WEBSERVER_CERTIFICATE_FILE = '-webserver_certificate_file'
_SSL_SERVER_CERTIFICATE = '-ssl_server_certificate'
_MAX_RESULT_CACHE_SIZE = '-max_result_cache_size'
_AUTHORIZED_PROXY_USER_CONFIG = '-authorized_proxy_user_config'


def reset():
  global _IMPALA_FLAGS
  _IMPALA_FLAGS = None


def get_conf():
  if _IMPALA_FLAGS is None:
    _parse_impala_flags()
  return _IMPALA_FLAGS


def get_webserver_certificate_file():
  return get_conf().get(_WEBSERVER_CERTIFICATE_FILE)

def get_ssl_server_certificate():
  return get_conf().get(_SSL_SERVER_CERTIFICATE)

def get_max_result_cache_size():
  result_size = get_conf().get(_MAX_RESULT_CACHE_SIZE)
  return int(result_size) if result_size else None


def get_authorized_proxy_user_config():
  return get_conf().get(_AUTHORIZED_PROXY_USER_CONFIG)


def _parse_impala_flags():
  global _IMPALA_FLAGS

  try:
    impala_flags_path = os.path.join(conf.IMPALA_CONF_DIR.get(), 'impalad_flags')
    _IMPALA_FLAGS = dict(line.strip().split('=', 1) for line in open(impala_flags_path) if '=' in line)
  except IOError, err:
    if err.errno != errno.ENOENT:
      LOG.error('Cannot read from "%s": %s' % (impala_flags_path, err))
    _IMPALA_FLAGS = {}
  except Exception, ex:
    LOG.error('Failed to parse Impala config from "%s": %s' % (impala_flags_path, ex))
    _IMPALA_FLAGS = {}
