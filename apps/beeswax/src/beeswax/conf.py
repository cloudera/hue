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

import os.path
import sys
import beeswax.hive_site

from django.utils.translation import ugettext_lazy as _t, ugettext as _

from desktop.lib.conf import ConfigSection, Config, coerce_bool

from beeswax.settings import NICE_NAME


HIVE_SERVER_HOST = Config(
  key="hive_server_host",
  help=_t("Host where HiveServer2 server is running. If Kerberos security is enabled, "
         "the fully-qualified domain name (FQDN) is required"),
  default="localhost")

HIVE_SERVER_PORT = Config(
  key="hive_server_port",
  help=_t("Configure the port the HiveServer2 server runs on."),
  default=10000,
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
  help=_t('Choose whether to use the old GetLog() thrift call from before Hive 0.14 to retrieve the logs.'
          'If false, use the FetchResults() thrift call from Hive 1.0 or more instead.')
)

BROWSE_PARTITIONED_TABLE_LIMIT = Config(
  key='browse_partitioned_table_limit',
  default=250,
  type=int,
  help=_t('Set a LIMIT clause when browsing a partitioned table. A positive value will be set as the LIMIT. If 0 or negative, do not set any limit.'))

DOWNLOAD_ROW_LIMIT = Config(
  key='download_row_limit',
  default=1000000,
  type=int,
  help=_t('A limit to the number of rows that can be downloaded from a query. A value of -1 means there will be no limit. A maximum of 65,000 is applied to XLS downloads.'))

CLOSE_QUERIES = Config(
  key="close_queries",
  help=_t("Hue will try to close the Hive query when the user leaves the editor page. "
          "This will free all the query resources in HiveServer2, but also make its results inaccessible."),
  type=coerce_bool,
  default=False
)

THRIFT_VERSION = Config(
  key="thrift_version",
  help=_t("Thrift version to use when communicating with HiveServer2."),
  type=int,
  default=7
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
      default="/etc/hue/cacerts.pem"
    ),

    KEY = Config(
      key="key",
      help=_t("Path to the private key file."),
      type=str,
      default="/etc/hue/key.pem"
    ),

    CERT = Config(
      key="cert",
      help=_t("Path to the public certificate file."),
      type=str,
      default="/etc/hue/cert.pem"
    ),

    VALIDATE = Config(
      key="validate",
      help=_t("Choose whether Hue should validate certificates received from the server."),
      type=coerce_bool,
      default=True
    )
  )
)

def config_validator(user):
  # dbms is dependent on beeswax.conf (this file)
  # import in method to avoid circular dependency
  from beeswax.server import dbms

  res = []
  try:
    if not 'test' in sys.argv: # Avoid tests hanging
      server = dbms.get(user)
      server.get_databases()
  except:
    res.append((NICE_NAME, _("The application won't work without a running HiveServer2.")))

  try:
    from hadoop import cluster
    warehouse = beeswax.hive_site.get_metastore_warehouse_dir()
    fs = cluster.get_hdfs()
    fs.stats(warehouse)
  except Exception:
    return [(NICE_NAME, _('Failed to access Hive warehouse: %s') % warehouse)]

  return res
