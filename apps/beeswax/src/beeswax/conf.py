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
"""Configuration options for the Hive UI (Beeswax)."""
from desktop.lib.conf import Config
import os.path

BEESWAX_SERVER_HOST = Config(
  key="beeswax_server_host",
  help="Host where beeswax server thrift daemon is running",
  private=True,
  default="localhost")

BEESWAX_SERVER_PORT = Config(
  key="beeswax_server_port",
  help="Configure the port the beeswax thrift server runs on",
  default=8002,
  type=int)

BEESWAX_META_SERVER_HOST = Config(
  key="beeswax_meta_server_host",
  help="Host where beeswax internal metastore thrift daemon is running",
  private=True,
  default="localhost")

BEESWAX_META_SERVER_PORT = Config(
  key="beeswax_meta_server_port",
  help="Configure the port the internal metastore daemon runs on. Used only if "
       "hive.metastore.local is true.",
  default=8003,
  type=int)

BEESWAX_SERVER_BIN = Config(
  key="beeswax_server_bin",
  help="Path to beeswax_server.sh",
  private=True,
  default=os.path.join(os.path.dirname(__file__), "..", "..", "beeswax_server.sh"))

BEESWAX_SERVER_HEAPSIZE = Config(
  key="beeswax_server_heapsize",
  help="Maximum Java heapsize (in megabytes) used by Beeswax Server.  " + \
    "Note that the setting of HADOOP_HEAPSIZE in $HADOOP_CONF_DIR/hadoop-env.sh " + \
    "may override this setting.",
  default="1000")

BEESWAX_HIVE_HOME_DIR = Config(
  key="hive_home_dir",
  default=os.environ.get("HIVE_HOME", "/usr/lib/hive"),
  help=("Path to the root of the Hive installation; " +
        "defaults to environment variable when not set.")
)

BEESWAX_HIVE_CONF_DIR = Config(
  key='hive_conf_dir',
  help='Hive configuration directory, where hive-site.xml is located',
  default=os.environ.get("HIVE_CONF_DIR", '/etc/hive/conf'))

LOCAL_EXAMPLES_DATA_DIR = Config(
  key='local_examples_data_dir',
  default=os.path.join(os.path.dirname(__file__), "..", "..", "data"),
  help='The local filesystem path containing the beeswax examples')

BEESWAX_SERVER_CONN_TIMEOUT = Config(
  key='beeswax_server_conn_timeout',
  default=120,
  type=int,
  help='Timeout in seconds for thrift calls to beeswax service')

METASTORE_CONN_TIMEOUT= Config(
  key='metastore_conn_timeout',
  default=10,
  type=int,
  help='Timeouts in seconds for thrift calls to the hive metastore. This timeout should take into account that the metastore could talk to an external DB')
