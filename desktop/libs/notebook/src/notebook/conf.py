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

from django.utils.translation import ugettext_lazy as _t

from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection,\
  coerce_json_dict


def get_interpreters():
  return [{
      "name": INTERPRETERS.get()[i].NAME.get(),
      "type": i,
      "interface": INTERPRETERS.get()[i].INTERFACE.get(),
      "options": INTERPRETERS.get()[i].OPTIONS.get()}
      for i in INTERPRETERS.get()
  ]


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
  default=True)
