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

LOG = logging.getLogger(__name__)

_IMPALA_FLAGS = None

_WEBSERVER_CERTIFICATE_FILE = '-webserver_certificate_file'
_WEBSERVER_REQUIRE_SPNEGO = '-webserver_require_spnego'
_SSL_SERVER_CERTIFICATE = '-ssl_server_certificate'
_MAX_RESULT_CACHE_SIZE = '-max_result_cache_size'
_AUTHORIZED_PROXY_USER_CONFIG = '-authorized_proxy_user_config'
_PRINCIPAL = '-principal'
_DEFAULT_QUERY_OPTIONS = '-default_query_options'
_DEFAULT_TRANSACTIONAL_TYPE = 'default_transactional_type'
_DEFAULT_HS2_HTTP_PORT='-hs2_http_port'


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
  """
    The path to the TLS/SSL file containing the server certificate key used for TLS/SSL. Used when Catalog
    Server Webserver is acting as a TLS/SSL server. The certificate file must be in PEM format.
  """
  return get_conf().get(_SSL_SERVER_CERTIFICATE)

def get_max_result_cache_size():
  """
    Maximum number of query results a client may request to be cached on a per-query basis to support restarting
    fetches. This option guards against unreasonably large result caches requested by clients. Requests exceeding
    this maximum will be rejected.
  """
  result_size = get_conf().get(_MAX_RESULT_CACHE_SIZE)
  return int(result_size) if result_size else 50000

def get_authorized_proxy_user_config():
  """
    Specifies the set of authorized proxy users (users who can impersonate other users during authorization) and whom
    they are allowed to impersonate. Input is a semicolon-separated list of key=value pairs of authorized proxy users
    to the user(s) they can impersonate. These users are specified as a comma separated list of short usernames, or '*'
    to indicate all users. For example: joe=alice,bob;hue=*;admin=*. Only valid when Sentry is enabled.
  """
  return get_conf().get(_AUTHORIZED_PROXY_USER_CONFIG)

def is_impersonation_enabled():
  """
  If hue user is allowed to send the queries as itself with an additiona doas parameter containing the logged-in user username.
  """
  user_config = get_conf().get(_AUTHORIZED_PROXY_USER_CONFIG)
  return user_config and 'hue=' in user_config

def default_query_option(option_name):
  query_options = get_conf().get(_DEFAULT_QUERY_OPTIONS)
  if not query_options:
    return query_options
  options = dict([option.split('=') for option in query_options.split(',')])
  return options.get(option_name)

def default_transactional_type():
  return default_query_option(_DEFAULT_TRANSACTIONAL_TYPE)

def is_transactional():
  return default_transactional_type() is not None

def is_kerberos_enabled():
  return get_conf().get(_PRINCIPAL) is not None

def is_webserver_spnego_enabled():
  """
    Returns True if Enable Kerberos Authentication for HTTP Web-Consoles for Impala service is turned on (default: true)
    -webserver_require_spnego=true  in impalad_flags
   """
  return get_conf().get(_WEBSERVER_REQUIRE_SPNEGO)

def get_hs2_http_port():
  return get_conf().get(_DEFAULT_HS2_HTTP_PORT, 26000)


def _parse_impala_flags():
  from impala import conf # Cyclic dependency
  global _IMPALA_FLAGS

  try:
    impala_flags_path = os.path.join(conf.IMPALA_CONF_DIR.get(), 'impalad_flags')
    _IMPALA_FLAGS = dict(line.strip().split('=', 1) for line in open(impala_flags_path) if '=' in line)
  except IOError as err:
    if err.errno != errno.ENOENT:
      LOG.error('Cannot read from "%s": %s' % (impala_flags_path, err))
    _IMPALA_FLAGS = {}
  except Exception as ex:
    LOG.error('Failed to parse Impala flag file %s' % ex)
    _IMPALA_FLAGS = {}
