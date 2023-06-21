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
import sys

from django.db import connection, models, transaction
from django.db.models import Q
from django.db.models.query import QuerySet

from useradmin.organization import _fitered_queryset, get_user_request_organization

from desktop.conf import CONNECTORS, ENABLE_ORGANIZATIONS
from desktop.lib.connectors.types import get_connectors_types
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_unicode

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _, gettext_lazy as _t
else:
  from django.utils.translation import ugettext as _, ugettext_lazy as _t


LOG = logging.getLogger()


class BaseConnector(models.Model):
  """
  Instance of a connector type pointing to an external service of a certain dialect.
  """
  name = models.CharField(default='', max_length=255)
  description = models.TextField(default='')
  dialect = models.CharField(max_length=32, db_index=True, help_text=_t('Type of connector, e.g. hive, mysql... '))
  interface = models.CharField(
      max_length=32,
      db_index=True,
      help_text=_t('Type of interface, e.g. sqlalchemy, hiveserver2... '),
      default='sqlalchemy'
  )
  settings = models.TextField(default='{}')
  last_modified = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_t('Time last modified'))

  class Meta:
    abstract = True
    verbose_name = _t('connector')
    verbose_name_plural = _t('connectors')
    unique_together = ('name',)

  def __str__(self):
    return '%s (%s)' % (self.name, self.dialect)

  def to_dict(self):
    return {
      'id': self.id,
      'type': str(self.id),
      'name': self.name,
      'description': self.description,
      'dialect': self.dialect,
      'interface': self.interface,
      'settings': self.settings,
      'last_modified': self.last_modified
    }


if ENABLE_ORGANIZATIONS.get():
  class ConnectorManager(models.Manager):

    def get_queryset(self):
      """Restrict to only organization's connectors"""
      queryset = super(ConnectorManager, self).get_queryset()
      return _fitered_queryset(queryset)

    def get_by_natural_key(self, dialect, interface, organization):
      return self.get(dialect=dialect, interface=interface, organization__name=organization)

  class Connector(BaseConnector):
    organization = models.ForeignKey('useradmin.Organization', on_delete=models.CASCADE)

    objects = ConnectorManager()

    class Meta:
      unique_together = ('name', 'organization',)

    def __init__(self, *args, **kwargs):
      if not kwargs.get('organization'):
        kwargs['organization'] = get_user_request_organization()

      super(Connector, self).__init__(*args, **kwargs)

    def __str__(self):
      return '%s (%s) @ %s' % (self.name, self.dialect, self.organization)

    def natural_key(self):
      return (self.dialect, self.interface) + self.organization.natural_key()
else:
  class ConnectorManager(models.Manager):

    def get_by_natural_key(self, dialect, interface):
      return self.get(dialect=dialect, interface=interface)

  class Connector(BaseConnector):

    objects = ConnectorManager()

    def natural_key(self):
      # Note: duplicates are still possible without key on the name
      return (self.dialect, self.interface)


def _get_installed_connectors(category=None, categories=None, dialect=None, interface=None, user=None, connector_id=None):
  from desktop.auth.backend import is_admin

  connectors_objects = Connector.objects.all()

  if user is not None and not is_admin(user):  # Apply Permissions
    connectors_objects = connectors_objects.filter(huepermission__in=user.get_permissions())

  connectors_objects = connectors_objects.order_by('id')

  connector_instances = [
      {
        'id': connector.id,
        'nice_name': connector.name,
        'description': connector.description,
        'dialect': connector.dialect,
        'interface': connector.interface,
        'settings': json.loads(connector.settings),
        'is_demo': False,
      }
      for connector in connectors_objects if connector_id is None or connector_id == connector.id
  ]
  connectors = []

  for connector in connector_instances:
    full_connector = _augment_connector_properties(connector)
    if full_connector:
      connectors.append(full_connector)
    else:
      LOG.warning('Skipping connector %(id)s as connector dialect %(dialect)s or interface %(interface)s are not installed' % (
          {'id': connector['id'], 'dialect': connector['dialect'], 'interface': connector['interface']}
        )
      )

  if categories is not None:
    connectors = [connector for connector in connectors if connector['category'] in categories]
  if category is not None:
    connectors = [connector for connector in connectors if connector['category'] == category]
  if dialect is not None:
    connectors = [connector for connector in connectors if connector['dialect'] == dialect]
  if interface is not None:
    connectors = [connector for connector in connectors if connector['interface'] == interface]

  if connector_id and user and not connectors:
    raise ConnectorNotFoundException(_('Connector %s not found for user %s') % (connector_id, user))

  return connectors


def _augment_connector_properties(connector):
  '''
  Add the connector properties based on the dialect + interface matching to each connector.
  The connector type must exist in desktop/core/src/desktop/lib/connectors/types.py.
  '''

  connector_types = []
  connector_type = None

  for connector_type in get_connectors_types():
    if connector_type['dialect'] == connector['dialect'] and connector['interface'] and \
        connector_type.get('interface') == connector.get('interface'):
      connector_types.insert(0, connector_type)
      break
    if connector_type['dialect'] == connector['dialect']:
      connector_types.insert(0, connector_type)
    elif connector['interface'] and connector_type.get('interface') == connector['interface']:
      connector_types.append(connector_type)

  if connector_types:
    connector_type = connector_types[0]
    return {
      'nice_name': connector['nice_name'],
      'name': str(connector['id']),
      'dialect': connector['dialect'],
      'interface': connector['interface'] or connector_type['interface'],
      'settings': connector['settings'],
      'id': str(connector['id']),
      'category': connector_type['category'],
      'description': connector_type['description'],
      'dialect_properties': connector_type.get('properties', {})
    }


def _create_connector_examples():
  added = []
  skipped = []

  for connector in _get_connector_examples():
    name = '%(nice_name)s (%(dialect)s)' % connector
    if not Connector.objects.filter(name=connector['nice_name']).exists():
      connector = Connector.objects.create(
        name=connector['nice_name'],
        description=connector['description'],
        dialect=connector['dialect'],
        settings=json.dumps(connector['settings'])
      )
      added.append(name)
    else:
      skipped.append(name)

  return added, skipped


def _get_connector_examples():
  return [
    {
      'id': i,
      'nice_name': CONNECTORS.get()[i].NICE_NAME.get() or i,
      'description': '',
      'dialect': CONNECTORS.get()[i].DIALECT.get(),
      'interface': CONNECTORS.get()[i].INTERFACE.get(),
      'settings': CONNECTORS.get()[i].SETTINGS.get(),
      'is_demo': True,
    }
    for i in CONNECTORS.get()
  ]


class ConnectorNotFoundException(Exception):
  def __init__(self, message=None):
    self.message = message or _('No error message, please check the logs.')

  def __str__(self):
    return str(self.message)

  def __unicode__(self):
    return smart_unicode(self.message)
