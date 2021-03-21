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

from collections import OrderedDict

from django.test.client import Client
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _t, ugettext as _

from desktop import appmanager
from desktop.conf import is_oozie_enabled, has_connectors, is_cm_managed
from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection, coerce_json_dict, coerce_bool, coerce_csv


LOG = logging.getLogger(__name__)

# Not used when connector are on
INTERPRETERS_CACHE = None


SHOW_NOTEBOOKS = Config(
    key="show_notebooks",
    help=_t("Show the notebook menu or not"),
    type=coerce_bool,
    default=True
)


def _remove_duplications(a_list):
  return list(OrderedDict.fromkeys(a_list))


def check_has_missing_permission(user, interpreter, user_apps=None):
  # TODO: port to cluster config
  if user_apps is None:
    user_apps = appmanager.get_apps_dict(user)  # Expensive method
  return (interpreter == 'hive' and 'hive' not in user_apps) or \
         (interpreter == 'impala' and 'impala' not in user_apps) or \
         (interpreter == 'pig' and 'pig' not in user_apps) or \
         (interpreter == 'solr' and 'search' not in user_apps) or \
         (interpreter in ('spark', 'pyspark', 'r', 'jar', 'py', 'sparksql') and 'spark' not in user_apps) or \
         (interpreter in ('java', 'spark2', 'mapreduce', 'shell', 'sqoop1', 'distcp') and 'oozie' not in user_apps)


def _connector_to_iterpreter(connector):
  return {
      'name': connector['nice_name'],
      'type': connector['name'],  # Aka id
      'dialect': connector['dialect'],
      'category': connector['category'],
      'is_sql': connector['dialect_properties']['is_sql'],
      'interface': connector['interface'],
      'options': {setting['name']: setting['value'] for setting in connector['settings']},
      'dialect_properties': connector['dialect_properties'],
  }


def get_ordered_interpreters(user=None):
  global INTERPRETERS_CACHE

  if has_connectors():
    from desktop.lib.connectors.api import _get_installed_connectors
    interpreters = [
      _connector_to_iterpreter(connector)
      for connector in _get_installed_connectors(categories=['editor', 'catalogs'], user=user)
    ]
  else:
    if INTERPRETERS_CACHE is None:
      none_user = None # for getting full list of interpreters
      if is_cm_managed():
        extra_interpreters = INTERPRETERS.get()  # Combine the other apps interpreters
        _default_interpreters(none_user)
      else:
        extra_interpreters = {}

      if not INTERPRETERS.get():
        _default_interpreters(none_user)

      INTERPRETERS_CACHE = INTERPRETERS.get()
      INTERPRETERS_CACHE.update(extra_interpreters)

    user_apps = appmanager.get_apps_dict(user)
    user_interpreters = []
    for interpreter in INTERPRETERS_CACHE:
      if check_has_missing_permission(user, interpreter, user_apps=user_apps):
        pass  # Not allowed
      else:
        user_interpreters.append(interpreter)

    interpreters_shown_on_wheel = _remove_duplications(INTERPRETERS_SHOWN_ON_WHEEL.get())
    unknown_interpreters = set(interpreters_shown_on_wheel) - set(user_interpreters)
    if unknown_interpreters:
      # Just filtering it out might be better than failing for this user
      raise ValueError("Interpreters from interpreters_shown_on_wheel is not in the list of Interpreters %s" % unknown_interpreters)

    reordered_interpreters = interpreters_shown_on_wheel + [i for i in user_interpreters if i not in interpreters_shown_on_wheel]

    interpreters = [{
        'name': INTERPRETERS_CACHE[i].NAME.get(),
        'type': i,
        'interface': INTERPRETERS_CACHE[i].INTERFACE.get(),
        'options': INTERPRETERS_CACHE[i].OPTIONS.get()
      }
      for i in reordered_interpreters
    ]

  return [{
      "name": i.get('nice_name', i['name']),
      "type": i['type'],
      "interface": i['interface'],
      "options": i['options'],
      'dialect': i.get('dialect', i['name']).lower(),
      'dialect_properties': i.get('dialect_properties') or {},  # Empty when connectors off
      'category': i.get('category', 'editor'),
      "is_sql": i.get('is_sql') or \
          i['interface'] in ["hiveserver2", "rdbms", "jdbc", "solr", "sqlalchemy", "ksql", "flink"] or \
          i['type'] == 'sql',
      "is_catalog": i['interface'] in ["hms",],
    }
    for i in interpreters
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

DEFAULT_LIMIT = Config(
  "default_limit",
  help="Default limit to use in SELECT statements if not present. Set to 0 to disable.",
  default=5000,
  type=int
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
  default=False
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
  default=False
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


EXAMPLES = ConfigSection(
  key='examples',
  help=_t('Define which query and table examples can be automatically setup for the available dialects.'),
  members=dict(
    AUTO_LOAD=Config(
      'auto_load',
      help=_t('If installing the examples automatically at startup.'),
      type=coerce_bool,
      default=False
    ),
    AUTO_OPEN=Config(
      'auto_open',
      help=_t('If automatically loading the dialect example at Editor opening.'),
      type=coerce_bool,
      default=False
    ),
    QUERIES=Config(
      'queries',
      help='Names of the saved queries to install. All if empty.',
      type=coerce_csv,
      default=[]
    ),
    TABLES=Config(
      key='tables',
      help=_t('Names of the tables to install. All if empty.'),
      type=coerce_csv,
      default=[]
    )
  )
)

def _default_interpreters(user):
  interpreters = []
  apps = appmanager.get_apps_dict(user)

  if 'hive' in apps:
    from beeswax.hive_site import get_hive_execution_engine
    interpreter_name = 'Impala' if get_hive_execution_engine() == 'impala' else 'Hive'  # Until using a proper dialect for 'FENG'

    interpreters.append(('hive', {
      'name': interpreter_name, 'interface': 'hiveserver2', 'options': {}
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


def config_validator(user, interpreters=None):
  res = []

  if not has_connectors():
    return res

  client = Client()
  client.force_login(user=user)

  if not user.is_authenticated:
    res.append(('Editor', _('Could not authenticate with user %s to validate interpreters') % user))

  if interpreters is None:
    interpreters = get_ordered_interpreters(user=user)

  for interpreter in interpreters:
    if interpreter.get('is_sql'):
      connector_id = interpreter['type']

      try:
        response = _excute_test_query(client, connector_id, interpreter=interpreter)
        data = json.loads(response.content)

        if data['status'] != 0:
          raise Exception(data)
      except Exception as e:
        trace = str(e)
        msg = "Testing the connector connection failed."
        if 'Error validating the login' in trace or 'TSocket read 0 bytes' in trace:
          msg += ' Failed to authenticate, check authentication configurations.'

        LOG.exception(msg)
        res.append(
          (
            '%(name)s - %(dialect)s (%(type)s)' % interpreter,
            _(msg) + (' %s' % trace[:100] + ('...' if len(trace) > 50 else ''))
          )
        )

  return res


def _excute_test_query(client, connector_id, interpreter=None):
  '''
  Helper utils until the API gets simplified.
  '''
  notebook_json = """
    {
      "selectedSnippet": "hive",
      "showHistory": false,
      "description": "Test Query",
      "name": "Test Query",
      "sessions": [
          {
              "type": "hive",
              "properties": [],
              "id": null
          }
      ],
      "type": "hive",
      "id": null,
      "snippets": [{"id":"2b7d1f46-17a0-30af-efeb-33d4c29b1055","type":"%(connector_id)s","status":"running","statement":"select * from web_logs","properties":{"settings":[],"variables":[],"files":[],"functions":[]},"result":{"id":"b424befa-f4f5-8799-a0b4-79753f2552b1","type":"table","handle":{"log_context":null,"statements_count":1,"end":{"column":21,"row":0},"statement_id":0,"has_more_statements":false,"start":{"column":0,"row":0},"secret":"rVRWw7YPRGqPT7LZ/TeFaA==an","has_result_set":true,"statement":"select * from web_logs","operation_type":0,"modified_row_count":null,"guid":"7xm6+epkRx6dyvYvGNYePA==an"}},"lastExecuted": 1462554843817,"database":"default"}],
      "uuid": "d9efdee1-ef25-4d43-b8f9-1a170f69a05a"
  }
  """ % {
    'connector_id': connector_id,
  }
  snippet = json.loads(notebook_json)['snippets'][0]
  snippet['interpreter'] = interpreter

  return client.post(
    reverse('notebook:api_sample_data', kwargs={'database': 'default', 'table': 'default'}), {
      'notebook': notebook_json,
      'snippet': json.dumps(snippet),
      'is_async': json.dumps(True),
      'operation': json.dumps('hello')
  })
