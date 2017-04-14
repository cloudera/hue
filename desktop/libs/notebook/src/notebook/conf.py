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

try:
  from collections import OrderedDict
except ImportError:
  from ordereddict import OrderedDict # Python 2.6

from django.utils.translation import ugettext_lazy as _t

from desktop import appmanager
from desktop.conf import is_hue4
from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection,\
  coerce_json_dict, coerce_bool, coerce_csv


def is_oozie_enabled():
  """Oozie needs to be available as it is the backend."""
  return len([app for app in appmanager.DESKTOP_MODULES if app.name == 'oozie']) > 0 and is_hue4()


SHOW_NOTEBOOKS = Config(
    key="show_notebooks",
    help=_t("Show the notebook menu or not"),
    type=coerce_bool,
    default=True
)

def _remove_duplications(a_list):
  return list(OrderedDict.fromkeys(a_list))


def get_ordered_interpreters(user=None):
  if not INTERPRETERS.get():
    _default_interpreters(user)

  interpreters = INTERPRETERS.get()
  interpreters_shown_on_wheel = _remove_duplications(INTERPRETERS_SHOWN_ON_WHEEL.get())

  unknown_interpreters = set(interpreters_shown_on_wheel) - set(interpreters)
  if unknown_interpreters:
      raise ValueError("Interpreters from interpreters_shown_on_wheel is not in the list of Interpreters %s" % unknown_interpreters)

  reordered_interpreters = interpreters_shown_on_wheel + [i for i in interpreters if i not in interpreters_shown_on_wheel]

  return [{
      "name": interpreters[i].NAME.get(),
      "type": i,
      "interface": interpreters[i].INTERFACE.get(),
      "options": interpreters[i].OPTIONS.get()}
      for i in reordered_interpreters
  ]


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
  type=bool,
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
  type=bool,
  default=True
)

ENABLE_QUERY_SCHEDULING = Config(
  key="enable_query_scheduling",
  help=_t("Flag to enable the creation of a coordinator for the current SQL query."),
  type=bool,
  dynamic_default=is_hue4
)

ENABLE_BATCH_EXECUTE = Config(
  key="enable_batch_execute",
  help=_t("Flag to enable the bulk submission of queries as a background task through Oozie."),
  type=bool,
  dynamic_default=is_oozie_enabled
)


def _default_interpreters(user):
  interpreters = []
  apps = appmanager.get_apps_dict(user)

  if 'impala' in apps:
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

  if 'oozie' in apps:
    interpreters.extend((
      ('pig', {
          'name': 'Pig', 'interface': 'oozie', 'options': {}
      }),
      ('java', {
          'name': 'Java', 'interface': 'oozie', 'options': {}
      }),
      ('sqoop1', {
          'name': 'Sqoop 1', 'interface': 'oozie', 'options': {}
      }),
      ('distcp', {
          'name': 'Distcp', 'interface': 'oozie', 'options': {}
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
    ))

  if 'search' in apps: # And Solr 6+
    interpreters.append(('solr', {
        'name': 'Solr SQL', 'interface': 'solr', 'options': {}
    }),)

  if SHOW_NOTEBOOKS.get():
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
