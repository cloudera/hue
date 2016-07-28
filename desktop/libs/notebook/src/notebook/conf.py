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
from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection,\
  coerce_json_dict, coerce_string, coerce_bool


def get_interpreters(user=None):
  if not INTERPRETERS.get():
    _default_interpreters()

  interpreters = INTERPRETERS.get()

  return [{
      "name": interpreters[i].NAME.get(),
      "type": i,
      "interface": interpreters[i].INTERFACE.get(),
      "options": interpreters[i].OPTIONS.get()}
      for i in interpreters
  ]

def is_oozie_enabled():
  """Oozie needs to be available as it is the backend."""
  return len([app for app in appmanager.DESKTOP_MODULES if app.name == 'oozie']) > 0


SHOW_NOTEBOOKS = Config(
    key="show_notebooks",
    help=_t("Show the notebook menu or not"),
    type=coerce_bool,
    default=True
)

INTERPRETERS = UnspecifiedConfigSection(
  "interpreters",
  help="One entry for each type of snippet. The first 5 will appear in the wheel.",
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

ENABLE_DBPROXY_SERVER = Config(
  key="enable_dbproxy_server",
  help=_t("Main flag to override the automatic starting of the DBProxy server."),
  type=bool,
  default=True
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
  dynamic_default=is_oozie_enabled
)

ENABLE_BATCH_EXECUTE = Config(
  key="enable_batch_execute",
  help=_t("Flag to enable the bulk submission of queries as a background task through Oozie."),
  type=bool,
  dynamic_default=is_oozie_enabled
)

ENABLE_JAVA_DOCUMENT = Config(
  key="enable_java_document",
  help=_t("Flag to enable the Java document in editor and workflow."),
  type=bool,
  dynamic_default=is_oozie_enabled
)


GITHUB_REMOTE_URL = Config(
    key="github_remote_url",
    help=_t("Base URL to GitHub Remote Server"),
    default='https://github.com',
    type=coerce_string,
)

GITHUB_API_URL = Config(
    key="github_api_url",
    help=_t("Base URL to GitHub API"),
    default='https://api.github.com',
    type=coerce_string,
)

GITHUB_CLIENT_ID = Config(
    key="github_client_id",
    help=_t("The Client ID of the GitHub application."),
    type=coerce_string,
    default=""
)

GITHUB_CLIENT_SECRET = Config(
    key="github_client_secret",
    help=_t("The Client Secret of the GitHub application."),
    type=coerce_string,
    default=""
)


def _default_interpreters():
  INTERPRETERS.set_for_testing(OrderedDict((
      ('hive', {
          'name': 'Hive', 'interface': 'hiveserver2', 'options': {}
      }),
      ('impala', {
          'name': 'Impala', 'interface': 'hiveserver2', 'options': {}
      }),
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
      ('pig', {
          'name': 'Pig', 'interface': 'pig', 'options': {}
      }),
      ('solr', {
          'name': 'Solr SQL', 'interface': 'solr', 'options': {}
      }),
      ('java', {
          'name': 'Java', 'interface': 'oozie', 'options': {}
      })
      ,
      ('text', {
          'name': 'Text', 'interface': 'text', 'options': {}
      }),
      ('markdown', {
          'name': 'Markdown', 'interface': 'text', 'options': {}
      })
    ))
  )

