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

from useradmin.models import update_app_permissions
from notebook.conf import config_validator, _connector_to_interpreter

from desktop.auth.decorators import admin_required
from desktop.decorators import api_error_handler
from desktop.lib.django_util import JsonResponse, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.connectors.models import _get_installed_connectors, get_connectors_types, Connector, _create_connector_examples, \
    _augment_connector_properties
from desktop.lib.connectors.types import get_connectors_types, get_connector_categories, get_connector_by_type

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _

LOG = logging.getLogger(__name__)


def get_connector_types(request):
  return JsonResponse({
    'connectors': _group_by_category(
      get_connectors_types()
    ),
    'categories': get_connector_categories()
  })


def get_connectors_instances(request):
  return JsonResponse({
    'connectors': _group_by_category(
      _get_installed_connectors()
    )
  })


def new_connector(request, dialect, interface):
  instance = get_connector_by_type(dialect, interface)

  instance['id'] = None

  return JsonResponse({'connector': instance})


def get_connector(request, id):
  instance = Connector.objects.get(id=id)

  return JsonResponse({
    'id': instance.id,
    'name': instance.name,
    'description': instance.description,
    'dialect': instance.dialect,
    'settings': json.loads(instance.settings)
  })


@admin_required
def update_connector(request):
  connector = json.loads(request.POST.get('connector', '{}'))
  saved_as = False

  if connector.get('id'):
    instance = Connector.objects.get(id=connector['id'])
    instance.name = connector['nice_name']
    instance.description = connector['description']
    instance.settings = json.dumps(connector['settings'])
    # TODO: if `sqlalchemy` interface, delete key in ENGINES
    instance.save()
  else:
    saved_as = True
    instance = Connector.objects.create(
      name=connector['nice_name'],
      description='',
      dialect=connector['dialect'],
      interface=connector['interface'],
      settings=json.dumps(connector['settings'])
    )
    connector['id'] = instance.id
    connector['name'] = instance.id

  update_app_permissions()

  return JsonResponse({'connector': connector, 'saved_as': saved_as})


@admin_required
def delete_connector(request):
  connector = json.loads(request.POST.get('connector', '{}'))

  try:
    Connector.objects.get(id=connector['id']).delete()
    # TODO: if `sqlalchemy` interface, delete key in ENGINES
  except Exception as e:
    raise PopupException(_('Error deleting connector %s: %s') % (connector['name'], e))

  update_app_permissions()

  return JsonResponse({})


@admin_required
def test_connector(request):
  connector = json.loads(request.POST.get('connector', '{}'))

  # Currently only Editor connectors are supported.
  interpreter = _connector_to_interpreter(
      _augment_connector_properties(connector)
  )
  interpreter['type'] = 'hello'  # This is the id of the common health check query

  warnings = ''.join([
    ''.join(warning)
    for warning in config_validator(user=request.user, interpreters=[interpreter])
  ])

  return JsonResponse({'warnings': warnings, 'hasWarnings': bool(warnings)})


@admin_required
@api_error_handler
def install_connector_examples(request):
  message = []

  try:
    added, skipped = _create_connector_examples()
    if added:
      message.append('Added connectors: ' + ', '.join(added))
    if skipped:
      message.append('Already installed connectors: ' + ', '.join(skipped))
  except Exception as e:
    raise PopupException(_('Error installing connector examples: %s') % e)

  update_app_permissions()

  return JsonResponse({'status': 0, 'message': '. '.join(message)})


def _group_by_category(conns):
  return [{
      'category': category['type'],
      'category_name': category['name'],
      'description': category['description'],
      'values': [
        _connector
        for _connector in conns if _connector['category'] == category['type']
      ],
    } for category in get_connector_categories()
  ]
