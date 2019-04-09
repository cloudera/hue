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


INSTALLED_CONNECTORS = [
  {'name': 'Impala', 'type': Impala().NAME, 'settings': Impala().PROPERTIES, 'id': 1, 'category': 'engines', 'description': ''},
  {'name': 'Hive', 'type': Hive().NAME, 'settings': Hive().PROPERTIES, 'id': 2, 'category': 'engines', 'description': ''},
]

CONNECTOR_TYPES = [
  {'name': connector.NAME, 'type': connector.TYPE, 'settings': connector.PROPERTIES, 'id': None, 'category': 'engines', 'description': ''}
    for connector in [
      Impala(),
      Hive()
    ]
]

CONNECTOR_TYPES += [
  {'name': "SQL Database", 'type': 'sql-alchemy', 'settings': {}, 'id': None, 'category': 'engines', 'description': ''},
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

  {'name': "HDFS", 'type': 'hdfs', 'settings': {}, 'id': None, 'category': 'browsers', 'description': ''},
  {'name': "YARN", 'type': 'yarn', 'settings': {}, 'id': None, 'category': 'browsers', 'description': ''},
  {'name': "S3", 'type': 's3', 'settings': {}, 'id': None, 'category': 'browsers', 'description': ''},
  {'name': "ADLS", 'type': 'adls-v1', 'settings': {}, 'id': None, 'category': 'browsers', 'description': ''},

  {'name': "Atlas", 'type': 'atlas', 'settings': {}, 'id': None, 'category': 'catalogs', 'description': ''},
  {'name': "Navigator", 'type': 'navigator', 'settings': {}, 'id': None, 'category': 'catalogs', 'description': ''},

  {'name': "Optimizer", 'type': 'optimizer', 'settings': {}, 'id': None, 'category': 'optimizers', 'description': ''},

  {'name': "Oozie", 'type': 'oozie', 'settings': {}, 'id': None, 'category': 'schedulers', 'description': ''},
  {'name': "Celery", 'type': 'celery', 'settings': {}, 'id': None, 'category': 'schedulers', 'description': '' },
]

CATEGORIES = [
  {"name": "Query Engines", 'type': 'engines', 'description': ''},
  {"name": "Browsers", 'type': 'browsers', 'description': ''},
  {"name": "Catalogs", 'type': 'catalogs', 'description': ''},
  {"name": "Optimizers", 'type': 'optimizers', 'description': ''},
  {"name": "Schedulers", 'type': 'schedulers', 'description': ''},
  {"name": "Apps", 'type': 'apps', 'description': ''},
  {"name": "Plugins", 'type': 'plugins', 'description': ''},
]

AVAILABLE_CONNECTORS = {
  "connectors": [{
    'category': category['name'],
    'values': [_connector for _connector in CONNECTOR_TYPES if _connector['category'] == category['type']],
    'description': category['description'],
  } for category in CATEGORIES]
}


def connectors(request):
  return JsonResponse({
    'connectors': INSTALLED_CONNECTORS
  })


def new_connector(request, type):
  instance = _get_connector_by_type(type)

  return JsonResponse({'connector': instance})


def get_connector(request, id):
  instance = _get_connector_by_id(id)

  return JsonResponse(instance)

CONNECTOR_IDS = 10

def update_connector(request):
  global CONNECTOR_IDS

  connector = json.loads(request.POST.get('connector'), '{}')

  if connector.get('id'):
    instance = _get_connector_by_id(connector['id'])
    instance.update(connector)
  else:
    instance = connector
    instance['id'] = CONNECTOR_IDS
    CONNECTOR_IDS += 1
    INSTALLED_CONNECTORS.append(instance)

  return JsonResponse(instance)


def _get_connector_by_type(type):
  global CONNECTOR_TYPES

  instance = filter(lambda connector: connector['type'] == type, CONNECTOR_TYPES)

  if instance:
    return instance[0]
  else:
    raise PopupException(_('No connector with the type %s found.') % type)


def delete_connector(request):
  global INSTALLED_CONNECTORS

  connector = json.loads(request.POST.get('connector'), '{}')

  size_before = len(INSTALLED_CONNECTORS)
  INSTALLED_CONNECTORS = filter(lambda _connector: _connector['name'] != connector['name'], INSTALLED_CONNECTORS)
  size_after = len(INSTALLED_CONNECTORS)

  if size_before == size_after + 1:
    return JsonResponse({})
  else:
    raise PopupException(_('No connector with the name %(name)s found.') % connector)


def _get_connector_by_id(id):
  global INSTALLED_CONNECTORS

  instance = filter(lambda connector: connector['id'] == id, INSTALLED_CONNECTORS)

  if instance:
    return instance[0]
  else:
    raise PopupException(_('No connector with the id %s found.') % id)


def connector_types(request):
  global AVAILABLE_CONNECTORS

  return JsonResponse(AVAILABLE_CONNECTORS)
