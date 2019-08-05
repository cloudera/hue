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

from desktop.conf import has_connectors, CONNECTORS
from desktop.lib.django_util import JsonResponse, render
from desktop.lib.connectors.lib.impala import Impala
from desktop.lib.connectors.lib.hive import Hive
from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)


# TODO: automatically load modules from lib module
# TODO: offer to white/black list available connector classes
CONNECTOR_TYPES = [{
    'nice_name': connector.NAME,
    'dialect': connector.TYPE,
    'interface': connector.INTERFACE, # interfaces = ['int1', 'int2'...]
    'settings': connector.PROPERTIES,
    'id': None,
    'category': 'editor',
    'description': ''
    }
  for connector in [
    Impala(), Hive()
  ]
]

CONNECTOR_TYPES += [
  {'nice_name': "Hive Tez", 'dialect': 'hive-tez', 'interface': 'hiveserver2', 'settings': [{'name': 'server_host', 'value': ''}, {'name': 'server_port', 'value': ''},], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Hive LLAP", 'dialect': 'hive-llap', 'interface': 'hiveserver2', 'settings': [{'name': 'server_host', 'value': ''}, {'name': 'server_port', 'value': ''},], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Druid", 'dialect': 'sql-druid', 'interface': 'sqlalchemy', 'settings': [{'name': 'url', 'value': 'druid://druid-host.com:8082/druid/v2/sql/'}], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Kafka SQL", 'dialect': 'kafka-sql', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "SparkSQL", 'dialect': 'spark-sql', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "MySQL", 'dialect': 'mysql', 'interface': 'sqlalchemy', 'settings': [{'name': 'url', 'value': 'mysql://username:password@mysq-host:3306/hue'}], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Presto", 'dialect': 'presto', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Athena", 'dialect': 'athena', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Redshift", 'dialect': 'redshift', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Big Query", 'dialect': 'bigquery', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Oracle", 'dialect': 'oracle', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "SQL Database", 'dialect': 'sql-alchemy', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "SQL Database (JDBC)", 'dialect': 'sql-jdbc', 'interface': 'sqlalchemy', 'settings': [], 'id': None, 'category': 'editor', 'description': 'Deprecated: older way to connect to any database.'},
  # solr
  # hbase
  # kafka

  {'nice_name': "PySpark", 'dialect': 'pyspark', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Spark", 'dialect': 'spark', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Pig", 'dialect': 'pig', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},
  {'nice_name': "Java", 'dialect': 'java', 'settings': [], 'id': None, 'category': 'editor', 'description': ''},

  {'nice_name': "HDFS", 'dialect': 'hdfs', 'settings': [], 'id': None, 'category': 'browsers', 'description': ''},
  {'nice_name': "YARN", 'dialect': 'yarn', 'settings': [], 'id': None, 'category': 'browsers', 'description': ''},
  {'nice_name': "S3", 'dialect': 's3', 'settings': [], 'id': None, 'category': 'browsers', 'description': ''},
  {'nice_name': "ADLS", 'dialect': 'adls-v1', 'settings': [], 'id': None, 'category': 'browsers', 'description': ''},

  {'nice_name': "Hive Metastore", 'dialect': 'hms', 'settings': [], 'id': None, 'category': 'catalogs', 'description': ''},
  {'nice_name': "Atlas", 'dialect': 'atlas', 'settings': [], 'id': None, 'category': 'catalogs', 'description': ''},
  {'nice_name': "Navigator", 'dialect': 'navigator', 'settings': [], 'id': None, 'category': 'catalogs', 'description': ''},

  {'nice_name': "Optimizer", 'dialect': 'optimizer', 'settings': [], 'id': None, 'category': 'optimizers', 'description': ''},

  {'nice_name': "Oozie", 'dialect': 'oozie', 'settings': [], 'id': None, 'category': 'schedulers', 'description': ''},
  {'nice_name': "Celery", 'dialect': 'celery', 'settings': [], 'id': None, 'category': 'schedulers', 'description': '' },
]

CATEGORIES = [
  {"name": "Editor", 'type': 'editor', 'description': ''},
  {"name": "Browsers", 'type': 'browsers', 'description': ''},
  {"name": "Catalogs", 'type': 'catalogs', 'description': ''},
  {"name": "Optimizers", 'type': 'optimizers', 'description': ''},
  {"name": "Schedulers", 'type': 'schedulers', 'description': ''},
  {"name": "Apps", 'type': 'apps', 'description': ''},
  {"name": "Plugins", 'type': 'plugins', 'description': ''},
]


def _group_category_connectors(connectors):
  return [{
    'category': category['type'],
    'category_name': category['name'],
    'description': category['description'],
    'values': [_connector for _connector in connectors if _connector['category'] == category['type']],
  } for category in CATEGORIES
]

AVAILABLE_CONNECTORS = _group_category_connectors(CONNECTOR_TYPES)


# TODO: persist in DB
# TODO: remove installed connectors that don't have a connector or are blacklisted
# TODO: load back from DB and apply Category properties, e.g. defaults, interface, category, category_name...
# TODO: connector groups: if we want one type (e.g. Hive) to show-up with multiple computes and the same saved query.
# TODO: type --> name, type --> SQL language, e.g. mysql

# connector_type: category --> engine, is_sql --> engine_type: sql
CONNECTOR_INSTANCES = None
CONNECTOR_IDS = 10

def get_connector_classes(request):
  global AVAILABLE_CONNECTORS
  global CATEGORIES

  return JsonResponse({
    'connectors': AVAILABLE_CONNECTORS,
    'categories': CATEGORIES
  })


def get_installed_connectors(request):
  return JsonResponse({
    'connectors': _group_category_connectors(
      _get_installed_connectors()
    ),
  })


def new_connector(request, dialect):
  instance = _get_connector_by_type(dialect)

  instance['nice_name'] = dialect.title()

  return JsonResponse({'connector': instance})


def get_connector(request, id):
  instance = _get_connector_by_id(id)

  return JsonResponse(instance)


def update_connector(request):
  global CONNECTOR_IDS

  connector = json.loads(request.POST.get('connector'), '{}')
  saved_as = False

  if connector.get('id'):
    instance = _get_connector_by_id(connector['id'])
    instance.update(connector)
  else:
    saved_as = True
    instance = connector
    instance['id'] = CONNECTOR_IDS
    instance['nice_name'] = instance['nice_name']
    instance['name'] = '%s-%s' % (instance['dialect'], CONNECTOR_IDS)
    instance['is_sql'] = instance.get('interface') in ("hiveserver2", "sqlalchemy")
    CONNECTOR_IDS += 1
    CONNECTOR_INSTANCES.append(instance)

  return JsonResponse({'connector': instance, 'saved_as': saved_as})


def _get_connector_by_type(dialect):
  global CONNECTOR_TYPES

  instance = filter(lambda connector: connector['dialect'] == dialect, CONNECTOR_TYPES)

  if instance:
    return instance[0]
  else:
    raise PopupException(_('No connector with the type %s found.') % type)


def delete_connector(request):
  global CONNECTOR_INSTANCES

  connector = json.loads(request.POST.get('connector'), '{}')

  size_before = len(CONNECTOR_INSTANCES)
  CONNECTOR_INSTANCES = filter(lambda _connector: _connector['name'] != connector['name'], CONNECTOR_INSTANCES)
  size_after = len(CONNECTOR_INSTANCES)

  if size_before == size_after + 1:
    return JsonResponse({})
  else:
    raise PopupException(_('No connector with the name %(name)s found.') % connector)


def _get_installed_connectors():
  global CONNECTOR_INSTANCES
  connector_config = CONNECTORS.get()

  if CONNECTOR_INSTANCES is None:
    CONNECTOR_INSTANCES = []
    for i in connector_config:
      connector_class = [
        connector_type
        for connector_type in CONNECTOR_TYPES
            if connector_type['dialect'] == connector_config[i].DIALECT.get() and connector_type['interface'] == connector_config[i].INTERFACE.get()
      ]
      CONNECTOR_INSTANCES.append({
          'nice_name': connector_config[i].NICE_NAME.get() or i,
          'name': i,
          'dialect': connector_config[i].DIALECT.get(),
          'interface': connector_config[i].INTERFACE.get(),
          'settings': connector_config[i].SETTINGS.get(),
          # From Connector class
          'is_sql': True,
          'id': None,
          'category': connector_class[0]['category'],
          'description': connector_class[0]['description']
        }
      )
  return CONNECTOR_INSTANCES


def _get_connector_by_id(id):
  global CONNECTOR_INSTANCES

  instance = filter(lambda connector: connector['id'] == id, CONNECTOR_INSTANCES)

  if instance:
    return instance[0]
  else:
    raise PopupException(_('No connector with the id %s found.') % id)
