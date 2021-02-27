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

import json
import logging

from django.utils.translation import ugettext as _

from desktop.conf import CONNECTORS_BLACKLIST, CONNECTORS_WHITELIST
from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)


CONNECTOR_TYPES = [
  {
    'dialect': 'hive',
    'nice_name': 'Hive',
    'description': 'Recommended',
    'category': 'editor',
    'interface': 'hiveserver2',
    'settings': [
      {'name': 'server_host', 'value': 'localhost'},
      {'name': 'server_port', 'value': 10000},
      {'name': 'is_llap', 'value': False},  # cf. _get_session_by_id() or create a separate connector
      {'name': 'use_sasl', 'value': True},
    ],
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': False,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': True,
      'has_reference_functions': True,
      'has_use_statement': True,
      'trim_statement_semicolon': False,
    }
  },
  {
    'dialect': 'hive',
    'nice_name': 'Hive',
    'description': 'Via SqlAlchemy interface',
    'category': 'editor',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'hive://localhost:10000'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': False,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': True,
      'has_reference_functions': True,
      'has_use_statement': True,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'Impala',
    'dialect': 'impala',
    'interface': 'hiveserver2',
    'category': 'editor',
    'description': '',
    'settings': [
      {'name': 'server_host', 'value': 'localhost'},
      {'name': 'server_port', 'value': 21050},
      {'name': 'impersonation_enabled', 'value': False},
      {'name': 'use_sasl', 'value': False},
    ],
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': False,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': True,
      'has_reference_functions': True,
      'has_use_statement': True,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'Impala',
    'dialect': 'impala',
    'interface': 'sqlalchemy',
    'category': 'editor',
    'description': 'Via SqlAlchemy interface',
    'settings': [
      {'name': 'url', 'value': 'impala://localhost:21050'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': False,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': True,
      'has_reference_functions': True,
      'has_use_statement': True,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'Druid',
    'dialect': 'druid',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'druid://localhost:8082/druid/v2/sql/'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '"',
      'sql_identifier_comment_single': '--',
      'has_catalog': False,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': True,
    }
  },
  {
    'nice_name': 'ksqlDB',
    'dialect': 'ksql',
    'interface': 'ksql',
    'settings': [
      {'name': 'url', 'value': 'http://localhost:8088'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': False,
      'has_database': False,
      'has_table': True,
      'has_live_queries': True,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': True,
    }
  },
  {
    'nice_name': 'Flink SQL',
    'dialect': 'flink',
    'interface': 'flink',
    'settings': [
      {'name': 'url', 'value': 'http://localhost:8083'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': False,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': True,
    }
  },
  {
    'nice_name': 'SparkSQL',
    'dialect': 'sparksql',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'hive://localhost:10000'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': 'Via Thrift Server and SqlAlchemy interface',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': False,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': True,
    }
  },
  {
    'nice_name': 'SparkSQL',
    'dialect': 'sparksql',
    'interface': 'hiveserver2',
    'settings': [
      {'name': 'server_host', 'value': 'localhost'},
      {'name': 'server_port', 'value': 10000},
      {'name': 'impersonation_enabled', 'value': False},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
      {'name': 'use_sasl', 'value': True},
    ],
    'category': 'editor',
    'description': 'Via Thrift Server and Hive interface',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': False,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': True,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'SparkSQL',
    'dialect': 'sparksql',
    'interface': 'livy',
    'settings': [
      {'name': 'api_url', 'value': 'http://localhost:8998'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': 'Via Livy server',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': False,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'Phoenix SQL',
    'dialect': 'phoenix',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'phoenix://localhost:8765/'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '"',
      'sql_identifier_comment_single': '--',
      'has_catalog': False,
      'has_database': False,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': True,
    }
  },
  {
    'nice_name': 'MySQL',
    'dialect': 'mysql',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'mysql://username:password@localhost:3306/hue'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'PostgreSQL',
    'dialect': 'postgresql',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'postgresql://username:password@localhost:5432/hue'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '"',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'Trino (Presto SQL)',
    'dialect': 'presto',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'presto://localhost:8080/tpch'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
      {'name': 'has_impersonation', 'value': False},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '"',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': True,
    }
  },
  {
    'nice_name': 'Dasksql',
    'dialect': 'dasksql',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'presto://localhost:8080/catalog/default'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
      {'name': 'has_impersonation', 'value': False},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '"',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': False,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'trim_statement_semicolon': True,
    }
  },
  {
    'nice_name': 'Elasticsearch SQL',
    'dialect': 'elasticsearch',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'elasticsearch+http://localhost:9200/'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '"',
      'sql_identifier_comment_single': '--',
      'has_catalog': False,
      'has_database': False,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': False,
      'has_optimizer_values': False,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'Calcite',
    'dialect': 'calcite',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'server_host', 'value': 'localhost'},
      {'name': 'server_port', 'value': 10000},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': False,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'Athena',
    'dialect': 'athena',
    'interface': 'sqlalchemy',
    'settings': [
      {
        'name': 'url',
        'value': 'awsathena+rest://XXXXXXXXXXXXXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX@athena.us-west-2.amazonaws.com:'
            '443/default?s3_staging_dir=s3://gethue-athena/scratch'
      },
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '"',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'Redshift',
    'dialect': 'redshift',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'edshift+psycopg2://username@host.amazonaws.com:5439/database'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'Snowflake',
    'dialect': 'snowflake',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'snowflake://{user}:{password}@{account}/{database}'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'Big Query',
    'dialect': 'bigquery',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'bigquery://project-XXXXXX/dataset_name'},
      {'name': 'credentials_json', 'value': '{"type": "service_account", ...}'}
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'Oracle',
    'dialect': 'oracle',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'oracle://user:password@localhost'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'Clickhouse',
    'dialect': 'clickhouse',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'clickhouse://localhost:8123'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '"',
      'sql_identifier_comment_single': '--',
      'has_catalog': False,
      'has_database': False,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': True,
    }
  },
  {
    'nice_name': 'Solr SQL',
    'dialect': 'solr',
    'interface': 'solr',
    'settings': [
    {'name': 'url', 'value': 'solr://user:password@localhost:8983/solr/<collection>[?use_ssl=true|false]'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'SQL Database',
    'dialect': 'sql',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'name://projectName/datasetName'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'SQL Database (JDBC)',
    'dialect': 'sql',
    'interface': 'sqlalchemy',
    'settings': [
      {'name': 'url', 'value': 'jdbc:db2://localhost:50000/SQOOP'},
      {'name': 'driver', 'value': 'com.ibm.db2.jcc.DB2Driver'},
      {'name': 'user', 'value': 'hue'},
      {'name': 'password', 'value': 'hue'},
      {'name': 'has_ssh', 'value': False},
      {'name': 'ssh_server_host', 'value': '127.0.0.1'},
    ],
    'category': 'editor',
    'description': 'Deprecated: older way to connect to any database.',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': False,
      'has_optimizer_values': False,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },
  {
    'nice_name': 'SqlFlow',
    'dialect': 'sqlflow',
    'interface': 'sqlflow',
    'settings': [
      {'name': 'url', 'value': 'localhost:50051'},
      {'name': 'datasource', 'value': 'hive://localhost:10000/iris'},
    ],
    'category': 'editor',
    'description': '',
    'properties': {
      'is_sql': True,
      'sql_identifier_quote': '`',
      'sql_identifier_comment_single': '--',
      'has_catalog': True,
      'has_database': True,
      'has_table': True,
      'has_live_queries': False,
      'has_optimizer_risks': True,
      'has_optimizer_values': True,
      'has_auto_limit': False,
      'has_reference_language': False,
      'has_reference_functions': False,
      'has_use_statement': False,
      'trim_statement_semicolon': False,
    }
  },

  {'nice_name': 'PySpark', 'dialect': 'pyspark', 'settings': [], 'category': 'editor', 'description': '', 'properties': {}},
  {'nice_name': 'Spark', 'dialect': 'spark', 'settings': [], 'category': 'editor', 'description': '', 'properties': {}},
  {'nice_name': 'Pig', 'dialect': 'pig', 'settings': [], 'category': 'editor', 'description': '', 'properties': {}},
  {'nice_name': 'Java', 'dialect': 'java', 'settings': [], 'category': 'editor', 'description': '', 'properties': {}},

  {'nice_name': 'HDFS', 'dialect': 'hdfs', 'interface': 'rest',
    'settings': [
      {'name': 'server_url', 'value': 'http://localhost:9870/webhdfs/v1'},
      {'name': 'default_fs', 'value': 'fs_defaultfs=hdfs://localhost:8020'}
    ],
    'category': 'browsers', 'description': '', 'properties': {}
  },
  {'nice_name': 'YARN', 'dialect': 'yarn', 'settings': [], 'category': 'browsers', 'description': '', 'properties': {}},
  {'nice_name': 'S3', 'dialect': 's3', 'settings': [], 'category': 'browsers', 'description': '', 'properties': {}},
  {'nice_name': 'ADLS', 'dialect': 'adls-v1', 'settings': [], 'category': 'browsers', 'description': '', 'properties': {}},
  # HBase
  # Solr

  {
    'nice_name': 'Hive Metastore',
    'dialect': 'hms',
    'interface': 'hiveserver2',
    'settings': [{'name': 'server_host', 'value': ''}, {'name': 'server_port', 'value': ''},],
    'category': 'catalogs',
    'description': '',
    'properties': {}
  },
  {
    'nice_name': 'Atlas', 'dialect': 'atlas', 'interface': 'rest', 'settings': [], 'category': 'catalogs', 'description': '',
    'properties': {}
  },
  {
    'nice_name': 'Navigator', 'dialect': 'navigator', 'interface': 'rest', 'settings': [], 'category': 'catalogs',
    'description': '',
    'properties': {}
  },

  {'nice_name': 'Optimizer', 'dialect': 'optimizer', 'settings': [], 'category': 'optimizers', 'description': '', 'properties': {}},

  {'nice_name': 'Oozie', 'dialect': 'oozie', 'settings': [], 'category': 'schedulers', 'description': '', 'properties': {}},
  {'nice_name': 'Celery', 'dialect': 'celery', 'settings': [], 'category': 'schedulers', 'description': '', 'properties': {}},
]

CONNECTOR_TYPES = [connector for connector in CONNECTOR_TYPES if connector['dialect'] not in CONNECTORS_BLACKLIST.get()]

if CONNECTORS_WHITELIST.get():
  CONNECTOR_TYPES = [connector for connector in CONNECTOR_TYPES if connector['dialect'] in CONNECTORS_WHITELIST.get()]


CATEGORIES = [
  {"name": 'Editor', 'type': 'editor', 'description': ''},
  {"name": 'Browsers', 'type': 'browsers', 'description': ''},
  {"name": 'Catalogs', 'type': 'catalogs', 'description': ''},
  {"name": 'Optimizers', 'type': 'optimizers', 'description': ''},
  {"name": 'Schedulers', 'type': 'schedulers', 'description': ''},
  {"name": 'Plugins', 'type': 'plugins', 'description': ''},
]


def get_connectors_types():
  return CONNECTOR_TYPES

def get_connector_categories():
  return CATEGORIES

def get_connector_by_type(dialect, interface):
  instance = [
    connector
    for connector in get_connectors_types() if connector['dialect'] == dialect and connector['interface'] == interface
  ]

  if instance:
    return instance[0]
  else:
    raise PopupException(_('No connector with the type %s found.') % type)
