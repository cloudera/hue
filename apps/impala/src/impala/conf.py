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

import logging
import sys
import socket

from django.utils.translation import ugettext_lazy as _t, ugettext as _
from desktop.conf import default_ssl_cacerts, default_ssl_validate, AUTH_USERNAME as DEFAULT_AUTH_USERNAME,\
  AUTH_PASSWORD as DEFAULT_AUTH_PASSWORD
from desktop.lib.conf import ConfigSection, Config, coerce_bool, coerce_csv, coerce_password_from_script
from desktop.lib.exceptions import StructuredThriftTransportException

from impala.settings import NICE_NAME

LOG = logging.getLogger(__name__)


SERVER_HOST = Config(
  key="server_host",
  help=_t("Host of the Impala Server."),
  default="localhost")

SERVER_PORT = Config(
  key="server_port",
  help=_t("Port of the Impala Server."),
  default=21050,
  type=int)

IMPALA_PRINCIPAL=Config(
  key='impala_principal',
  help=_t("Kerberos principal name for Impala. Typically 'impala/hostname.foo.com'."),
  type=str,
  default="impala/%s" % socket.getfqdn())

IMPERSONATION_ENABLED=Config(
  key='impersonation_enabled',
  help=_t("Turn on/off impersonation mechanism when talking to Impala."),
  type=coerce_bool,
  default=False)

QUERYCACHE_ROWS=Config(
  key='querycache_rows',
  help=_t("Number of initial rows of a resultset to ask Impala to cache in order to"
          " support re-fetching them for downloading them."
          " Set to 0 for disabling the option and backward compatibility."),
  type=int,
  default=50000)

SERVER_CONN_TIMEOUT = Config(
  key='server_conn_timeout',
  default=120,
  type=int,
  help=_t('Timeout in seconds for Thrift calls.'))

CLOSE_QUERIES = Config(
  key="close_queries",
  help=_t("Hue will try to close the Impala query when the user leaves the editor page. "
          "This will free all the query resources in Impala, but also make its results inaccessible."),
  type=coerce_bool,
  default=True
)

QUERY_TIMEOUT_S = Config(
  key="query_timeout_s",
  help=_t("If QUERY_TIMEOUT_S > 0, the query will be timed out (i.e. cancelled) if Impala does not do any work"
          " (compute or send back results) for that query within QUERY_TIMEOUT_S seconds."),
  type=int,
  default=600
)

SESSION_TIMEOUT_S = Config(
  key="session_timeout_s",
  help=_t("If SESSION_TIMEOUT_S > 0, the session will be timed out (i.e. cancelled) if Impala does not do any work"
          " (compute or send back results) for that session within QUERY_TIMEOUT_S seconds."),
  type=int,
  default=12 * 60 * 60
)

CONFIG_WHITELIST = Config(
  key='config_whitelist',
  default='debug_action,explain_level,mem_limit,optimize_partition_key_scans,query_timeout_s',
  type=coerce_csv,
  help=_t('A comma-separated list of white-listed Impala configuration properties that users are authorized to set.')
)

SSL = ConfigSection(
  key='ssl',
  help=_t('SSL configuration for the server.'),
  members=dict(
    ENABLED = Config(
      key="enabled",
      help=_t("SSL communication enabled for this server."),
      type=coerce_bool,
      default=False
    ),

    CACERTS = Config(
      key="cacerts",
      help=_t("Path to Certificate Authority certificates."),
      type=str,
      dynamic_default=default_ssl_cacerts,
    ),

    KEY = Config(
      key="key",
      help=_t("Path to the private key file, e.g. /etc/hue/key.pem"),
      type=str,
      default=None
    ),

    CERT = Config(
      key="cert",
      help=_t("Path to the public certificate file, e.g. /etc/hue/cert.pem"),
      type=str,
      default=None
    ),

    VALIDATE = Config(
      key="validate",
      help=_t("Choose whether Hue should validate certificates received from the server."),
      type=coerce_bool,
      dynamic_default=default_ssl_validate,
    )
  )
)

def get_auth_username():
  """Get from top level default from desktop"""
  return DEFAULT_AUTH_USERNAME.get()

AUTH_USERNAME = Config(
  key="auth_username",
  help=_t("Auth username of the hue user used for authentications."),
  private=True,
  dynamic_default=get_auth_username)

def get_auth_password():
  """Get from script or backward compatibility"""
  password = AUTH_PASSWORD_SCRIPT.get()
  if password:
    return password

  return DEFAULT_AUTH_PASSWORD.get()

AUTH_PASSWORD = Config(
  key="auth_password",
  help=_t("LDAP/PAM/.. password of the hue user used for authentications."),
  private=True,
  dynamic_default=get_auth_password)

AUTH_PASSWORD_SCRIPT = Config(
  key="auth_password_script",
  help=_t("Execute this script to produce the auth password. This will be used when `auth_password` is not set."),
  private=True,
  type=coerce_password_from_script,
  default=None)


def config_validator(user):
  # dbms is dependent on beeswax.conf (this file)
  # import in method to avoid circular dependency
  from beeswax.server import dbms
  from beeswax.server.dbms import get_query_server_config

  res = []
  try:
    try:
      if not 'test' in sys.argv: # Avoid tests hanging
        query_server = get_query_server_config(name='impala')
        server = dbms.get(user, query_server)
        server.get_databases()
    except StructuredThriftTransportException, ex:
      if 'TSocket read 0 bytes' in str(ex):  # this message appears when authentication fails
        msg = "Failed to authenticate to Impalad, check authentication configurations."
        LOG.exception(msg)
        res.append((NICE_NAME, _(msg)))
      else:
       raise ex
  except Exception, ex:
    msg = "No available Impalad to send queries to."
    LOG.exception(msg)
    res.append((NICE_NAME, _(msg)))

  return res
