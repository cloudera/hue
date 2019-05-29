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

from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _t


from desktop import appmanager
from desktop.conf import is_oozie_enabled, CONNECTORS
from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection, coerce_json_dict, coerce_bool, coerce_csv


SHOW_NOTEBOOKS = Config(
    key="show_notebooks",
    help=_t("Show the notebook menu or not"),
    type=coerce_bool,
    default=True
)

def _remove_duplications(a_list):
  return list(OrderedDict.fromkeys(a_list))

def check_permissions(user, interpreter, user_apps=None):
  if user_apps is None:
    user_apps = appmanager.get_apps_dict(user) # Expensive method
  return (interpreter == 'hive' and 'hive' not in user_apps) or \
         (interpreter == 'impala' and 'impala' not in user_apps) or \
         (interpreter == 'pig' and 'pig' not in user_apps) or \
         (interpreter == 'solr' and 'search' not in user_apps) or \
         (interpreter in ('spark', 'pyspark', 'r', 'jar', 'py', 'sparksql') and 'spark' not in user_apps) or \
         (interpreter in ('java', 'spark2', 'mapreduce', 'shell', 'sqoop1', 'distcp') and 'oozie' not in user_apps)


def get_ordered_interpreters(user=None):
  from desktop.lib.connectors.api import CONFIGURED_CONNECTORS
  global CONFIGURED_CONNECTORS

  if not INTERPRETERS.get():
    _default_interpreters(user)

  interpreters = INTERPRETERS.get()
  interpreters_shown_on_wheel = _remove_duplications(INTERPRETERS_SHOWN_ON_WHEEL.get())

  user_apps = appmanager.get_apps_dict(user)
  user_interpreters = []
  for interpreter in interpreters:
    if check_permissions(user, interpreter, user_apps=user_apps):
      pass # Not allowed
    else:
      user_interpreters.append(interpreter)

  unknown_interpreters = set(interpreters_shown_on_wheel) - set(user_interpreters)
  if unknown_interpreters:
    raise ValueError("Interpreters from interpreters_shown_on_wheel is not in the list of Interpreters %s" % unknown_interpreters)

  if CONNECTORS.IS_ENABLED.get():
    reordered_interpreters = [{
        'name': i['name'],
        'type': i['type'],
        'interface': i['interface'],
        'options': {setting['name']: setting['value'] for setting in i['settings']}
      } for i in CONFIGURED_CONNECTORS
    ]
  else:
    reordered_interpreters = interpreters_shown_on_wheel + [i for i in user_interpreters if i not in interpreters_shown_on_wheel]
    reordered_interpreters = [{
        'name': interpreters[i].NAME.get(),
        'type': i,
        'interface': interpreters[i].INTERFACE.get(),
        'options': interpreters[i].OPTIONS.get()
      } for i in reordered_interpreters
    ]

  return [{
      "name": i['name'],
      "type": i['type'],
      "interface": i['interface'],
      "options": i['options'],
      "is_sql": i['interface'] in ["hiveserver2", "rdbms", "jdbc", "solr", "sqlalchemy"],
      "is_catalog": i['interface'] in ["hms",],
    }
    for i in reordered_interpreters
  ]

# cf. admin wizard too

INTERPRETERS = UnspecifiedConfigSection(
  "interpreters",
  help="One entry for each type of snippet.",
  each=ConfigSection(
    help=_t("Define the name and how to connect and execute the language."),
    members=dict(
      NAME=Config(
          "name",
          help=_t("The name of the snippet."),
          default="SQL",
          type=str,
      ),
      INTERFACE=Config(
          "interface",
          help="The backend connection to use to communicate with the server.",
          default="hiveserver2",
          type=str,
      ),
      OPTIONS=Config(
        key='options',
        help=_t('Specific options for connecting to the server.'),
        type=coerce_json_dict,
        default='{}'
      )
    )
  )
)

INTERPRETERS_SHOWN_ON_WHEEL = Config(
  key="interpreters_shown_on_wheel",
  help=_t("Comma separated list of interpreters that should be shown on the wheel. "
          "This list takes precedence over the order in which the interpreter entries appear. "
          "Only the first 5 interpreters will appear on the wheel."),
  type=coerce_csv,
  default=[]
)

ENABLE_DBPROXY_SERVER = Config(
  key="enable_dbproxy_server",
  help=_t("Main flag to override the automatic starting of the DBProxy server."),
  type=coerce_bool,
  default=True
)

DBPROXY_EXTRA_CLASSPATH = Config(
  key="dbproxy_extra_classpath",
  help=_t("Additional classes to put on the dbproxy classpath when starting. Values separated by ':'"),
  type=str,
  default=''
)

ENABLE_QUERY_BUILDER = Config(
  key="enable_query_builder",
  help=_t("Flag to enable the SQL query builder of the table assist."),
  type=coerce_bool,
  default=True
)

ENABLE_NOTEBOOK_2 = Config(
  key="enable_notebook_2",
  help=_t("Feature flag to enable Notebook 2."),
  type=coerce_bool,
  default=False
)

# Note: requires Oozie app
ENABLE_QUERY_SCHEDULING = Config(
  key="enable_query_scheduling",
  help=_t("Flag to enable the creation of a coordinator for the current SQL query."),
  type=coerce_bool,
  default=False
)

ENABLE_EXTERNAL_STATEMENT = Config(
  key="enable_external_statements",
  help=_t("Flag to enable the selection of queries from files, saved queries into the editor or as snippet."),
  type=coerce_bool,
  default=True
)

ENABLE_BATCH_EXECUTE = Config(
  key="enable_batch_execute",
  help=_t("Flag to enable the bulk submission of queries as a background task through Oozie."),
  type=coerce_bool,
  dynamic_default=is_oozie_enabled
)

ENABLE_SQL_INDEXER = Config(
  key="enable_sql_indexer",
  help=_t("Flag to turn on the SQL indexer."),
  type=coerce_bool,
  default=False
)

ENABLE_PRESENTATION = Config(
  key="enable_presentation",
  help=_t("Flag to turn on the Presentation mode of the editor."),
  type=coerce_bool,
  default=True
)

ENABLE_QUERY_ANALYSIS = Config(
  key="enable_query_analysis",
  help=_t("Flag to turn on the built-in hints on Impala queries in the editor."),
  type=coerce_bool,
  default=False
)


def _default_interpreters(user):
  interpreters = []
  apps = appmanager.get_apps_dict(user)

  if 'hive' in apps:
    interpreters.append(('hive', {
      'name': 'Hive', 'interface': 'hiveserver2', 'options': {}
    }),)

  if 'impala' in apps:
    interpreters.append(('impala', {
      'name': 'Impala', 'interface': 'hiveserver2', 'options': {}
    }),)

  if 'pig' in apps:
    interpreters.append(('pig', {
      'name': 'Pig', 'interface': 'oozie', 'options': {}
    }))

  if 'oozie' in apps and 'jobsub' in apps:
    interpreters.extend((
      ('java', {
          'name': 'Java', 'interface': 'oozie', 'options': {}
      }),
      ('spark2', {
          'name': 'Spark', 'interface': 'oozie', 'options': {}
      }),
      ('mapreduce', {
          'name': 'MapReduce', 'interface': 'oozie', 'options': {}
      }),
      ('shell', {
          'name': 'Shell', 'interface': 'oozie', 'options': {}
      }),
      ('sqoop1', {
          'name': 'Sqoop 1', 'interface': 'oozie', 'options': {}
      }),
      ('distcp', {
          'name': 'Distcp', 'interface': 'oozie', 'options': {}
      }),
    ))

  from dashboard.conf import get_properties  # Cyclic dependency
  dashboards = get_properties()
  if dashboards.get('solr') and dashboards['solr']['analytics']:
    interpreters.append(('solr', {
        'name': 'Solr SQL', 'interface': 'solr', 'options': {}
    }),)

  from desktop.models import Cluster  # Cyclic dependency
  cluster = Cluster(user)
  if cluster and cluster.get_type() == 'dataeng':
    interpreters.append(('dataeng', {
        'name': 'DataEng', 'interface': 'dataeng', 'options': {}
    }))

  if 'spark' in apps:
    interpreters.extend((
      ('spark', {
          'name': 'Scala', 'interface': 'livy', 'options': {}
      }),
      ('pyspark', {
          'name': 'PySpark', 'interface': 'livy', 'options': {}
      }),
      ('r', {
          'name': 'R', 'interface': 'livy', 'options': {}
      }),
      ('jar', {
          'name': 'Spark Submit Jar', 'interface': 'livy-batch', 'options': {}
      }),
      ('py', {
          'name': 'Spark Submit Python', 'interface': 'livy-batch', 'options': {}
      }),
      ('text', {
          'name': 'Text', 'interface': 'text', 'options': {}
      }),
      ('markdown', {
          'name': 'Markdown', 'interface': 'text', 'options': {}
      })
    ))

  INTERPRETERS.set_for_testing(OrderedDict(interpreters))
