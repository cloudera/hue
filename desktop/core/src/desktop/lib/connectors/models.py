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
from desktop.lib.connectors.types import get_connectors_types
from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)


class Connector(models.Model):
  """
  Instance of a connector pointing to an external service: connection
  """
  name = models.CharField(default='', max_length=255)
  description = models.TextField(default='')
  dialect = models.CharField(max_length=32, db_index=True, help_text=_t('Type of connector, e.g. hive, mysql... '))
  settings = models.TextField(default='{}')
  last_modified = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_t('Time last modified'))

  organization = models.ForeignKey('useradmin.Organization', on_delete=models.CASCADE)

  class Meta:
    verbose_name = _t('connector')
    verbose_name_plural = _t('connectors')
    unique_together = ('name', 'organization',)


def _get_installed_connectors(category=None, categories=None, dialect=None, interface=None, user=None):
  connectors = []
  connector_instances = [
      {
        'id': connector.id,
        'nice_name': connector.name,
        'description': connector.description,
        'dialect': connector.dialect,
        'interface': None,
        'setting': json.loads(connector.settings),
        'is_demo': False,
      }
      for connector in Connector.objects.all()
  ] + [ # TODO move to samples? or auto
      {
        'id': i,
        'nice_name':  CONNECTORS.get()[i].NICE_NAME.get() or i,
        'description': '',
        'dialect': CONNECTORS.get()[i].DIALECT.get(),
        'interface': CONNECTORS.get()[i].INTERFACE.get(),
        'settings': CONNECTORS.get()[i].SETTINGS.get(),
        'is_demo': True,
      }
      for i in CONNECTORS.get()
  ]

  for connector in connector_instances:
    connector_types = []

    for connector_type in get_connectors_types():
      if connector_type['dialect'] == connector['dialect']:
        connector_types.insert(0, connector_type)
      elif connector_type.get('interface') == connector['interface']:
        connector_types.append(connector_type)

    if not connector_types:
      LOG.warn('Skipping connector %(id)s as connector dialect %(dialect)s or interface %(interface)s are not installed' % (
          {'id': connector['id'], 'dialect': connector['dialect'], 'interface': connector['interface']}
        )
      )
    else:
      connector_type = connector_types[0]
      connectors.append({
        'nice_name': connector['nice_name'],
        'name': connector['id'],
        'dialect': connector['dialect'],
        'interface': connector['interface'] or connector_type['interface'],
        'settings': connector['settings'],
        'id': connector['id'],
        'category': connector_type['category'],
        'description': connector_type['description'],
        'dialect_properties': connector_type.get('properties', {})
      })

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
