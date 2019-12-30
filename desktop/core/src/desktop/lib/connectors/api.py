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

from useradmin.models import update_app_permissions

from desktop.lib.django_util import JsonResponse, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.connectors import models
from desktop.lib.connectors.models import AVAILABLE_CONNECTORS, _get_connector_by_id, _get_installed_connectors, _group_category_connectors
from desktop.lib.connectors.types import CONNECTOR_TYPES, CATEGORIES


LOG = logging.getLogger(__name__)


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

  update_app_permissions()

  return JsonResponse({'connector': instance})


def get_connector(request, id):
  instance = _get_connector_by_id(id)

  return JsonResponse(instance)


def update_connector(request):
  connector = json.loads(request.POST.get('connector', '{}'))
  saved_as = False

  if connector.get('id'):
    instance = _get_connector_by_id(connector['id'])
    instance.update(connector)
  else:
    saved_as = True
    instance = connector
    instance['id'] = models.CONNECTOR_IDS
    instance['nice_name'] = instance['nice_name']
    instance['name'] = '%s-%s' % (instance['dialect'], models.CONNECTOR_IDS)
    models.CONNECTOR_IDS += 1
    models.CONNECTOR_INSTANCES.append(instance)

  update_app_permissions()

  return JsonResponse({'connector': instance, 'saved_as': saved_as})


def _get_connector_by_type(dialect):
  instance = [connector for connector in CONNECTOR_TYPES if connector['dialect'] == dialect]

  if instance:
    return instance[0]
  else:
    raise PopupException(_('No connector with the type %s found.') % type)


def delete_connector(request):
  connector = json.loads(request.POST.get('connector'), '{}')

  size_before = len(models.CONNECTOR_INSTANCES)
  models.CONNECTOR_INSTANCES = [_connector for _connector in models.CONNECTOR_INSTANCES if _connector['name'] != connector['name']]
  size_after = len(models.CONNECTOR_INSTANCES)

  if size_before == size_after + 1:
    update_app_permissions()
    return JsonResponse({})
  else:
    raise PopupException(_('No connector with the name %(name)s found.') % connector)
