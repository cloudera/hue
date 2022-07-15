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

from __future__ import division
from builtins import str
import logging
import math
import os.path
import sys

from desktop.conf import default_ssl_cacerts, default_ssl_validate, AUTH_PASSWORD as DEFAULT_AUTH_PASSWORD,\
  AUTH_USERNAME as DEFAULT_AUTH_USERNAME
from desktop.lib.conf import ConfigSection, Config, coerce_bool, coerce_csv, coerce_password_from_script

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t, gettext as _
else:
  from django.utils.translation import ugettext_lazy as _t, ugettext as _


LOG = logging.getLogger(__name__)

HIVE_DISCOVERY_LLAP = Config(
  key="hive_discovery_llap",
  help=_t("Have Hue determine Hive Server Interactive endpoint from zookeeper"),
  default="false",
  type=coerce_bool
)

HIVE_DISCOVERY_HS2 = Config(
  key="hive_discovery_hs2",
  help=_t("Determines whether we pull a random HiveServer2 from the list in zookeeper. "
    "This HS2 instance is cached until hue is restarted."),
  default="false",
  type=coerce_bool
)

HIVE_DISCOVERY_LLAP_HA = Config(
  key="hive_discovery_llap_ha",
  help=_t("If you have more than one HSI server, it has a different znode setup. "
    "This will trigger the code to check for the Active HSI Server"),
  default="false",
  type=coerce_bool
)

HIVE_DISCOVERY_LLAP_ZNODE = Config(
  key="hive_discovery_llap_znode",
  help=_t("If LLAP is enabled, you should be using zookeeper service discovery mode, this is the znode of the LLAP Master(s)"),
  default="/hiveserver2-hive2"
)

HIVE_DISCOVERY_HIVESERVER2_ZNODE = Config(
  key="hive_discovery_hiveserver2_znode",
  help=_t("If Hive is using zookeeper service discovery mode, this is the znode of the hiveserver2(s)"),
  default="/hiveserver2"
)

CACHE_TIMEOUT = Config(
  key="cache_timeout",
  help=_t("How long to pause before reaching back out to zookeeper to get the current Active HSI endpoint"),
  default=60,
  type=int
)

LLAP_SERVER_PORT = Config(
  key="llap_server_port",
  help=_t("LLAP binary Thrift port (10500 default)."),
  default=10500,
  type=int
)

LLAP_SERVER_THRIFT_PORT = Config(
  key="llap_server_thrift_port",
  help=_t("LLAP http Thrift port (10501 default)"),
  default=10501,
  type=int
)

LLAP_SERVER_HOST = Config(
  key="llap_server_host",
  help=_t("Host where Hive Server Interactive is running. If Kerberos security is enabled, "
         "the fully-qualified domain name (FQDN) is required"),
  default="localhost"
)

HIVE_SERVER_HOST = Config(
  key="hive_server_host",
  help=_t("Host where HiveServer2 server is running. If Kerberos security is enabled, "
         "the fully-qualified domain name (FQDN) is required"),
  default="localhost")

def get_hive_thrift_binary_port():
  """Devise port from core-site Thrift / execution mode & Http port"""
  from beeswax.hive_site import hiveserver2_thrift_binary_port, get_hive_execution_mode   # Cyclic dependency
  return hiveserver2_thrift_binary_port() or (10500 if (get_hive_execution_mode() or '').lower() == 'llap' else 10000)

HIVE_SERVER_PORT = Config(
  key="hive_server_port",
  help=_t("Configure the binary Thrift port for HiveServer2."),
  dynamic_default=get_hive_thrift_binary_port,
  type=int)

def get_hive_thrift_http_port():
  """Devise port from core-site Thrift / execution mode & Http port"""
  from beeswax.hive_site import hiveserver2_thrift_http_port, get_hive_execution_mode   # Cyclic dependency
  return hiveserver2_thrift_http_port() or (10501 if (get_hive_execution_mode() or '').lower() == 'llap'  else 10001)

HIVE_HTTP_THRIFT_PORT = Config(
  key="hive_server_http_port",
  help=_t("Configure the Http Thrift port for HiveServer2."),
  dynamic_default=get_hive_thrift_http_port,
  type=int)

HIVE_METASTORE_HOST = Config(
  key="hive_metastore_host",
  help=_t("Host where Hive Metastore Server (HMS) is running. If Kerberos security is enabled, "
         "the fully-qualified domain name (FQDN) is required"),
  default="localhost")

HIVE_METASTORE_PORT = Config(
  key="hive_metastore_port",
  help=_t("Configure the port the Hive Metastore Server runs on."),
  default=9083,
  type=int)

HIVE_CONF_DIR = Config(
  key='hive_conf_dir',
  help=_t('Hive configuration directory, where hive-site.xml is located.'),
  default=os.environ.get("HIVE_CONF_DIR", '/etc/hive/conf'))

HIVE_SERVER_BIN = Config(
  key="hive_server_bin",
  help=_t("Path to HiveServer2 start script"),
  default='/usr/lib/hive/bin/hiveserver2',
  private=True)

LOCAL_EXAMPLES_DATA_DIR = Config(
  key='local_examples_data_dir',
  default=os.path.join(os.path.dirname(__file__), "..", "..", "data"),
  help=_t('The local filesystem path containing the Hive examples.'))

SERVER_CONN_TIMEOUT = Config(
  key='server_conn_timeout',
  default=120,
  type=int,
  help=_t('Timeout in seconds for Thrift calls.'))

USE_GET_LOG_API = Config( # To remove in Hue 4
  key='use_get_log_api',
  default=False,
  type=coerce_bool,
  help=_t('Choose whether to use the old GetLog() Thrift call from before Hive 0.14 to retrieve the logs.'
          'If false, use the FetchResults() Thrift call from Hive 1.0 or more instead.')
)

BROWSE_PARTITIONED_TABLE_LIMIT = Config( # Deprecated, to remove in Hue 4
  key='browse_partitioned_table_limit',
  default=1000,
  type=int,
  help=_t('Limit the number of partitions to list on the partitions page. A positive value will be set as the LIMIT. '
    'If 0 or negative, do not set any limit.')
  )

QUERY_PARTITIONS_LIMIT = Config(
  key='query_partitions_limit',
  default=10,
  type=int,
  help=_t('The maximum number of partitions that will be included in the SELECT * LIMIT sample query for partitioned tables.'))

def get_browse_partitioned_table_limit():
  """Get the old default"""
  return BROWSE_PARTITIONED_TABLE_LIMIT.get()

LIST_PARTITIONS_LIMIT = Config(
  key='list_partitions_limit',
  dynamic_default=get_browse_partitioned_table_limit,
  type=int,
  help=_t('Limit the number of partitions that can be listed. A positive value will be set as the LIMIT.'))

# Deprecated
DOWNLOAD_CELL_LIMIT = Config(
  key='download_cell_limit',
  default=10000000,
  type=int,
  help=_t('A limit to the number of cells (rows * columns) that can be downloaded from a query '
          '(e.g. - 10K rows * 1K columns = 10M cells.) '
          'A value of -1 means there will be no limit.'))

def get_deprecated_download_cell_limit():
  """Get the old default"""
  return math.floor(DOWNLOAD_CELL_LIMIT.get() / 100) if DOWNLOAD_CELL_LIMIT.get() > 0 else DOWNLOAD_CELL_LIMIT.get()

DOWNLOAD_ROW_LIMIT = Config(
  key='download_row_limit',
  dynamic_default=get_deprecated_download_cell_limit,
  type=int,
  help=_t('A limit to the number of rows that can be downloaded from a query before it is truncated. '
          'A value of -1 means there will be no limit.'))

DOWNLOAD_BYTES_LIMIT = Config(
  key='download_bytes_limit',
  default=-1,
  type=int,
  help=_t('A limit to the number of bytes that can be downloaded from a query before it is truncated. '
          'A value of -1 means there will be no limit.'))

APPLY_NATURAL_SORT_MAX = Config(
  key="apply_natural_sort_max",
  help=_t("The max number of records in the result set permitted to apply a natural sort to the database or tables list."),
  type=int,
  default=2000
)

CLOSE_QUERIES = Config(
  key="close_queries",
  help=_t("Hue will try to close the Hive query when the user leaves the editor page. "
          "This will free all the query resources in HiveServer2, but also make its results inaccessible."),
  type=coerce_bool,
  default=False
)

MAX_NUMBER_OF_SESSIONS = Config(
  key="max_number_of_sessions",
  help=_t("Hue will use at most this many HiveServer2 sessions per user at a time"
          # The motivation for -1 is that Hue does currently keep track of session state perfectly and the user
          # does not have ability to manage them effectively. The cost of a session is low
          "-1 is unlimited number of sessions."),
  type=int,
  default=-1
)

THRIFT_VERSION = Config(
  key="thrift_version",
  help=_t("Thrift version to use when communicating with HiveServer2."),
  type=int,
  default=11
)

CONFIG_WHITELIST = Config(
  key='config_whitelist',
  default='hive.map.aggr,hive.exec.compress.output,hive.exec.parallel,hive.execution.engine,mapreduce.job.queuename',
  type=coerce_csv,
  help=_t('A comma-separated list of white-listed Hive configuration properties that users are authorized to set.')
)

SSL = ConfigSection(
  key='ssl',
  help=_t('SSL configuration for the server.'),
  members=dict(
    CACERTS=Config(
      key="cacerts",
      help=_t("Path to Certificate Authority certificates."),
      type=str,
      dynamic_default=default_ssl_cacerts,
    ),

    KEY=Config(
      key="key",
      help=_t("Path to the private key file, e.g. /etc/hue/key.pem"),
      type=str,
      default=None
    ),

    CERT=Config(
      key="cert",
      help=_t("Path to the public certificate file, e.g. /etc/hue/cert.pem"),
      type=str,
      default=None
    ),

    VALIDATE=Config(
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

def get_use_sasl_default():
  """Get from hive_site or backward compatibility"""
  from beeswax.hive_site import get_hiveserver2_authentication, get_use_sasl  # Cyclic dependency
  use_sasl = get_use_sasl()
  if use_sasl is not None:
    return use_sasl.upper() == 'TRUE'
  return get_hiveserver2_authentication() in ('KERBEROS', 'NONE', 'LDAP', 'PAM') # list for backward compatibility

USE_SASL = Config(
  key="use_sasl",
  help=_t("Use SASL framework to establish connection to host"),
  private=False,
  type=coerce_bool,
  dynamic_default=get_use_sasl_default)

def has_multiple_sessions():
  """When true will create multiple sessions for user queries"""
  return MAX_NUMBER_OF_SESSIONS.get() != 1

CLOSE_SESSIONS = Config(
  key="close_sessions",
  help=_t(
      'When set to True, Hue will close sessions created for background queries and open new ones as needed.'
      'When set to False, Hue will keep sessions created for background queries opened and reuse them as needed.'
      'This flag is useful when max_number_of_sessions != 1'),
  type=coerce_bool,
  dynamic_default=has_multiple_sessions
)

def has_session_pool():
  return has_multiple_sessions() and not CLOSE_SESSIONS.get()

MAX_CATALOG_SQL_ENTRIES = Config(
  key="max_catalog_sql_entries",
  help=_t(
    "Max number of objects (columns, tables, databases) available to list in the left assist, autocomplete, table browser etc."
    "Setting this higher than the default can degrade performance."),
  default=5000,
  type=int
)
