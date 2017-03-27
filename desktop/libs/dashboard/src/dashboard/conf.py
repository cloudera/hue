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

from django.utils.translation import ugettext as _, ugettext_lazy as _t

from desktop.conf import is_hue4
from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection, coerce_bool
from desktop.appmanager import get_apps_dict
from notebook.conf import get_ordered_interpreters



def is_enabled():
  """Automatic when search is enabled."""
  apps = get_apps_dict()

  return 'search' in apps or HAS_SQL_ENABLED.get()


IS_ENABLED = Config(
  key="is_enabled",
  help=_t("Activate the Dashboard link in the menu."),
  dynamic_default=is_enabled,
  type=coerce_bool
)

HAS_SQL_ENABLED = Config(
  key="has_sql_enabled",
  help=_t("Activate the SQL Dashboard (beta)."),
  dynamic_default=is_hue4,
  type=coerce_bool
)


def get_properties():
  if ENGINES.get():
    engines = ENGINES.get()
    return dict([
      (i, {
        'analytics': engines[i].ANALYTICS.get(),
        'nesting': engines[i].NESTING.get()
      }) for i in engines]
    )
  else:
    return {
      'solr': {
        'analytics': False,
        'nesting': False,
      },
      'sql': {
        'analytics': True,
        'nesting': False,
      },
    }

def get_engines(user):
  engines = []
  apps = get_apps_dict()
  settings = get_properties()

  if 'search' in apps:
    engines.append({
      'name': _('index (Solr)'),
      'type': 'solr',
      'analytics': settings.get('solr') and settings['solr'].get('analytics'),
      'nesting': settings.get('solr') and settings['solr'].get('nesting'),
    })

  if HAS_SQL_ENABLED.get() and ('beeswax' in apps or 'rdbms' in apps):
    engines += [{
          'name': _('table (%s)') % interpreter['name'],
          'type': interpreter['type'],
          'async': interpreter['interface'] == 'hiveserver2',
          'analytics': settings.get('sql') and settings['sql'].get('analytics'),
          'nesting': settings.get('sql') and settings['sql'].get('nesting'),
      }
      for interpreter in get_ordered_interpreters(user) if interpreter['interface'] in ('hiveserver2', 'jdbc', 'rdbms')
    ]

  return engines



ENGINES = UnspecifiedConfigSection(
  "engines",
  help="One entry for each type of snippet.",
  each=ConfigSection(
    help=_t("Name of the interface to use as query engine for the dashboard, e.g. solr, sql."),
    members=dict(
      ANALYTICS=Config(
          "analytics",
          help=_t("Support analytics facets or not."),
          default=False,
          type=coerce_bool,
      ),
      NESTING=Config(
          "nesting",
          help=_t("Support nested documents or not."),
          default=False,
          type=coerce_bool,
      ),
    )
  )
)