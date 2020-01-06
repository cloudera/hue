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

import logging

from django.db import connection, models, transaction
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.translation import ugettext as _, ugettext_lazy as _t

from desktop.conf import CONNECTORS
from desktop.lib.connectors.types import CONNECTOR_TYPES, CATEGORIES
from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)


# TODO: persist in DB and migrations
# TODO: connector groups: if we want one dialect (e.g. hive) to show-up with multiple/transient computes and the same saved query

CONNECTOR_INSTANCES = None
CONNECTOR_IDS = 1

# class Connector(models.Model):
  # '''
  # Instance of a connector pointing to an external service: connection
  # '''
#   type = models.CharField(max_length=32, db_index=True, help_text=_t('Type of connector, e.g. hive-tez, '))
#   name = models.CharField(default='', max_length=255)
#   description = models.TextField(default='')
#   is_valid # Must be in lib

#   settings = models.TextField(default='{}')
#   last_modified = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_t('Time last modified'))

#   organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

  # class Meta:
  #   verbose_name = _t('connector')
  #   verbose_name_plural = _t('connectors')
  #   unique_together = ('name', 'organization',)


def _group_category_connectors(connectors):
  return [{
      'category': category['type'],
      'category_name': category['name'],
      'description': category['description'],
      'values': [_connector for _connector in connectors if _connector['category'] == category['type']],
    } for category in CATEGORIES
  ]

AVAILABLE_CONNECTORS = _group_category_connectors(CONNECTOR_TYPES)


def _get_installed_connectors(category=None, categories=None, dialect=None, interface=None, user=None):
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
          'interface': config_connectors[i].INTERFACE.get() or connector_type.get('interface'),
          'settings': config_connectors[i].SETTINGS.get(),
          'id': CONNECTOR_IDS,
          'category': connector_type['category'],
          'description': connector_type['description'],
          'dialect_properties': connector_type.get('properties', {})
        }
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
  if user is not None:
    allowed_connectors = user.get_permissions().values_list('app', flat=True)
    connectors = [connector for connector in connectors if connector['name'] in allowed_connectors]

  return connectors


def _get_connector_by_id(id):
  global CONNECTOR_INSTANCES

  instance = [connector for connector in CONNECTOR_INSTANCES if connector['id'] == id]

  if instance:
    return instance[0]
  else:
    raise PopupException(_('No connector with the id %s found.') % id)
