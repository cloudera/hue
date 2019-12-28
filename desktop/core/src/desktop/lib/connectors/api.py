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
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.connectors.types import CONNECTOR_TYPES, CATEGORIES


LOG = logging.getLogger(__name__)


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

# connector_type: category --> engine, is_sql --> engine_type: sql
CONNECTOR_INSTANCES = None
CONNECTOR_IDS = 1

def get_connector_types(request):
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
  instance['id'] = None

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
    CONNECTOR_IDS += 1
    CONNECTOR_INSTANCES.append(instance)

  return JsonResponse({'connector': instance, 'saved_as': saved_as})


def _get_connector_by_type(dialect):
  instance = [connector for connector in CONNECTOR_TYPES if connector['dialect'] == dialect]

  if instance:
    return instance[0]
  else:
    raise PopupException(_('No connector with the type %s found.') % type)


def delete_connector(request):
  global CONNECTOR_INSTANCES

  connector = json.loads(request.POST.get('connector'), '{}')

  size_before = len(CONNECTOR_INSTANCES)
  CONNECTOR_INSTANCES = [_connector for _connector in CONNECTOR_INSTANCES if _connector['name'] != connector['name']]
  size_after = len(CONNECTOR_INSTANCES)

  if size_before == size_after + 1:
    return JsonResponse({})
  else:
    raise PopupException(_('No connector with the name %(name)s found.') % connector)


def _get_installed_connectors(category=None, categories=None, dialect=None, interface=None):
  global CONNECTOR_INSTANCES
  global CONNECTOR_IDS
  config_connectors = CONNECTORS.get()

  if CONNECTOR_INSTANCES is None:
    CONNECTOR_INSTANCES = []

    for i in config_connectors:
      connector_types = []

      for connector_type in CONNECTOR_TYPES:
        if connector_type['dialect'] == config_connectors[i].DIALECT.get():
          connector_types.insert(0, connector_type)
        elif connector_type.get('interface') == config_connectors[i].INTERFACE.get():
          connector_types.append(connector_type)

      if not connector_types:
        LOG.warn('Skipping connector %s as connector dialect %s or interface %s are not installed' % (
            i, config_connectors[i].DIALECT.get(), config_connectors[i].INTERFACE.get()
          )
        )
      else:
        connector_type = connector_types[0]
        connector = {
          'nice_name': config_connectors[i].NICE_NAME.get() or i,
          'name': i,
          'dialect': config_connectors[i].DIALECT.get(),
          'interface': config_connectors[i].INTERFACE.get(),
          'settings': config_connectors[i].SETTINGS.get(),
          'id': CONNECTOR_IDS,
          'category': connector_type['category'],
          'description': connector_type['description']
        }
        connector.update(connector_type['properties'])
        CONNECTOR_INSTANCES.append(connector)
        CONNECTOR_IDS += 1

  connectors = CONNECTOR_INSTANCES

  if categories is not None:
    connectors = [connector for connector in connectors if connector['category'] in categories]
  if category is not None:
    connectors = [connector for connector in connectors if connector['category'] == category]
  if dialect is not None:
    connectors = [connector for connector in connectors if connector['dialect'] == dialect]
  if interface is not None:
    connectors = [connector for connector in connectors if connector['interface'] == interface]

  return connectors


def _get_connector_by_id(id):
  global CONNECTOR_INSTANCES

  instance = [connector for connector in CONNECTOR_INSTANCES if connector['id'] == id]

  if instance:
    return instance[0]
  else:
    raise PopupException(_('No connector with the id %s found.') % id)
