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

from desktop.conf import is_hue4
from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection, coerce_json_dict, coerce_bool


IS_ENABLED = Config(
  key="is_enabled",
  help=_t("Activate the app in the menu."),
  dynamic_default=is_hue4,
  private=True,
  type=coerce_bool
)

# ANALYTICS_ENABLED 
SUPPORT_LATEST_SOLR = Config(
  key="support_latest_solr",
  help=_t("Use latest Solr 5+ functionalities like Analytics Facets and Nested Documents (warning: still in beta)."),
  default=True,
  type=coerce_bool
)

NESTED_ENABLED = Config(
  key="support_latest_solr",
  help=_t("Use latest Solr 5+ functionalities like Analytics Facets and Nested Documents (warning: still in beta)."),
  default=True,
  type=coerce_bool
)

# TODO [[interfaces]] instead
IS_SQL_ENABLED = Config(
  key="is_sql_enabled",
  help=_t("Offer to use SQL engines to compute the dashboards."),
  dynamic_default=is_hue4,
  private=True,
  type=coerce_bool
)

INTERPRETERS = UnspecifiedConfigSection(
  "connectors",
  help="One entry for each type of snippet.",
  each=ConfigSection(
    help=_t("Define the name and how to connect and execute the language."),
    members=dict(
      ANALYTICS_SUPPORT=Config(
          "name",
          help=_t("The name of the snippet."),
          default=False,
          type=coerce_bool,
      ),
      NESTED_SUPPORT=Config(
          "name",
          help=_t("The name of the snippet."),
          default=False,
          type=coerce_bool,
      ),
    )
  )
)