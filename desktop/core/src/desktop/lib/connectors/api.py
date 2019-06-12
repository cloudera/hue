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

from desktop.lib.django_util import JsonResponse, render
from desktop.lib.connectors.lib.impala import Impala
from desktop.lib.connectors.lib.hive import Hive
from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)


# TODO: automatically load modules from lib module
# TODO: offer to white/black list available connector classes
CONNECTOR_TYPES = [{
    'name': connector.NAME,
    'type': connector.TYPE,
    'interface': connector.INTERFACE,
    'settings': connector.PROPERTIES,
    'id': None,
    'category': 'engines',
    'description': ''
    }
  for connector in [
    Impala(), Hive()
  ]
]

CONNECTOR_TYPES += [
  {'name': "Hive Tez", 'type': 'hive-tez', 'settings': [{'name': 'server_host', 'value': ''}, {'name': 'server_port', 'value': ''},], 'id': None, 'category': 'engines', 'description': ''},
  {'name': "Hive LLAP", 'type': 'hive-llap', 'settings': [{'name': 'server_host', 'value': ''}, {'name': 'server_port', 'value': ''},], 'id': None, 'category': 'engines', 'description': ''},
  {'name': "Druid", 'type': 'druid', 'settings': [{'name': 'connection_url', 'value': 'druid://druid-host.com:8082/druid/v2/sql/'}], 'id': None, 'category': 'engines', 'description': ''},
  {'name': "Kafka SQL", 'type': 'kafka-sql', 'settings': {}, 'id': None, 'category': 'engines', 'description': ''},
  {'name': "SparkSQL", 'type': 'spark-sql', 'settings': {}, 'id': None, 'category': 'engines', 'description': ''},
  {'name': "Presto", 'type': 'presto', 'settings': {}, 'id': None, 'category': 'engines', 'description': ''},
  {'name': "Athena", 'type': 'athena', 'settings': {}, 'id': None, 'category': 'engines', 'description': ''},
  {'name': "Redshift", 'type': 'redshift', 'settings': {}, 'id': None, 'category': 'engines', 'description': ''},
  {'name': "Big Query", 'type': 'bigquery', 'settings': {}, 'id': None, 'category': 'engines', 'description': ''},
  {'name': "Oracle", 'type': 'oracle', 'settings': {}, 'id': None, 'category': 'engines', 'description': ''},
  {'name': "SQL Database", 'type': 'sql-alchemy', 'settings': {}, 'id': None, 'category': 'engines', 'description': ''},
  {'name': "SQL Database (JDBC)", 'type': 'sql-jdbc', 'settings': {}, 'id': None, 'category': 'engines', 'description': 'Deprecated: older way to connect to any database.'},

  {'name': "PySpark", 'type': 'pyspark', 'settings': {}, 'id': None, 'category': 'engines', 'description': ''},
  {'name': "Spark", 'type': 'spark', 'settings': {}, 'id': None, 'category': 'engines', 'description': ''},
  {'name': "Pig", 'type': 'pig', 'settings': {}, 'id': None, 'category': 'engines', 'description': ''},
  {'name': "Java", 'type': 'java', 'settings': {}, 'id': None, 'category': 'engines', 'description': ''},

  {'name': "HDFS", 'type': 'hdfs', 'settings': {}, 'id': None, 'category': 'browsers', 'description': ''},
  {'name': "YARN", 'type': 'yarn', 'settings': {}, 'id': None, 'category': 'browsers', 'description': ''},
  {'name': "S3", 'type': 's3', 'settings': {}, 'id': None, 'category': 'browsers', 'description': ''},
  {'name': "ADLS", 'type': 'adls-v1', 'settings': {}, 'id': None, 'category': 'browsers', 'description': ''},

  {'name': "Hive Metastore", 'type': 'hms', 'settings': {}, 'id': None, 'category': 'catalogs', 'description': ''},
  {'name': "Atlas", 'type': 'atlas', 'settings': {}, 'id': None, 'category': 'catalogs', 'description': ''},
  {'name': "Navigator", 'type': 'navigator', 'settings': {}, 'id': None, 'category': 'catalogs', 'description': ''},

  {'name': "Optimizer", 'type': 'optimizer', 'settings': {}, 'id': None, 'category': 'optimizers', 'description': ''},

  {'name': "Oozie", 'type': 'oozie', 'settings': {}, 'id': None, 'category': 'schedulers', 'description': ''},
  {'name': "Celery", 'type': 'celery', 'settings': {}, 'id': None, 'category': 'schedulers', 'description': '' },
]

CATEGORIES = [
  {"name": "Editor", 'type': 'engines', 'description': ''},
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
CONFIGURED_CONNECTORS = [
  {'name': 'Impala', 'type': Impala().TYPE + '-1', 'connector_name': Impala().TYPE, 'interface': Impala().INTERFACE, 'settings': Impala().PROPERTIES, 'id': 1, 'category': 'engines', 'description': ''},
  {'name': 'Hive', 'type': Hive().TYPE + '-2', 'connector_name': Hive().TYPE, 'interface': Hive().INTERFACE, 'settings': Hive().PROPERTIES, 'id': 2, 'category': 'engines', 'description': ''},
  {'name': 'Hive c5', 'type': Hive().TYPE + '-3', 'connector_name': Hive().TYPE, 'interface': Hive().INTERFACE, 'settings': Hive().PROPERTIES, 'id': 3, 'category': 'engines', 'description': ''},
]


def get_connector_classes(request):
  global AVAILABLE_CONNECTORS
  global CATEGORIES

  return JsonResponse({
    'connectors': AVAILABLE_CONNECTORS,
    'categories': CATEGORIES
  })


def get_installed_connectors(request):
  return JsonResponse({
    'connectors': _group_category_connectors(CONFIGURED_CONNECTORS),
  })


def new_connector(request, type):
  instance = _get_connector_by_type(type)

  instance['connector_name'] = ''

  return JsonResponse({'connector': instance})


def get_connector(request, id):
  instance = _get_connector_by_id(id)

  return JsonResponse(instance)

CONNECTOR_IDS = 10

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
    instance['connector_name'] = instance['type']
    instance['type'] = '%s-%s' % (instance['type'], CONNECTOR_IDS)
    CONNECTOR_IDS += 1
    CONFIGURED_CONNECTORS.append(instance)

  return JsonResponse({'connector': instance, 'saved_as': saved_as})


def _get_connector_by_type(type):
  global CONNECTOR_TYPES

  instance = filter(lambda connector: connector['type'] == type, CONNECTOR_TYPES)

  if instance:
    return instance[0]
  else:
    raise PopupException(_('No connector with the type %s found.') % type)


def delete_connector(request):
  global CONFIGURED_CONNECTORS

  connector = json.loads(request.POST.get('connector'), '{}')

  size_before = len(CONFIGURED_CONNECTORS)
  CONFIGURED_CONNECTORS = filter(lambda _connector: _connector['name'] != connector['name'], CONFIGURED_CONNECTORS)
  size_after = len(CONFIGURED_CONNECTORS)

  if size_before == size_after + 1:
    return JsonResponse({})
  else:
    raise PopupException(_('No connector with the name %(name)s found.') % connector)


def _get_connector_by_id(id):
  global CONFIGURED_CONNECTORS

  instance = filter(lambda connector: connector['id'] == id, CONFIGURED_CONNECTORS)

  if instance:
    return instance[0]
  else:
    raise PopupException(_('No connector with the id %s found.') % id)
