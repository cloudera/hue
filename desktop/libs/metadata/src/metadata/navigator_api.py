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

from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode

from metadata.navigator import NavigatorApi, is_navigator_enabled

LOG = logging.getLogger(__name__)


class MetadataApiException(Exception):
  pass


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    try:
      if is_navigator_enabled():
        return view_fn(*args, **kwargs)
      else:
        raise MetadataApiException('Navigator API is not configured.')
    except Http404, e:
      raise e
    except Exception, e:
      LOG.exception(str(e))
      response = {
        'status': -1,
        'message': force_unicode(str(e))
      }
    return JsonResponse(response, status=500)
  return decorator


@require_POST
@error_handler
def find_entity(request):
  response = {'status': -1}

  api = NavigatorApi()
  entity_type = json.loads(request.POST.get('type', ''))

  if not entity_type:
    raise MetadataApiException("find_entity requires a type value, e.g. - 'database', 'table', 'file'")

  if entity_type.lower() == 'database':
    name = json.loads(request.POST.get('name', ''))
    if not name:
      raise MetadataApiException('get_database requires name param')
    response['entity'] = api.get_database(name)
  elif entity_type.lower() == 'table':
    database = json.loads(request.POST.get('database', ''))
    name = request.POST.get('name', '')
    if not database or not name:
      raise MetadataApiException('get_table requires database and name param')
    response['entity'] = api.get_table(database, name)
  elif entity_type.lower() == 'directory':
    path = json.loads(request.POST.get('path', ''))
    if not path:
      raise MetadataApiException('get_directory requires path param')
    response['entity'] = api.get_directory(path)
  elif entity_type.lower() == 'file':
    path = json.loads(request.POST.get('path', ''))
    if not path:
      raise MetadataApiException('get_file requires path param')
    response['entity'] = api.get_file(path)
  else:
    raise MetadataApiException("type %s is unrecognized" % entity_type)

  response['status'] = 0
  return JsonResponse(response)


@error_handler
def get_entity(request):
  response = {'status': -1}

  api = NavigatorApi()
  entity_id = request.REQUEST.get('id')

  if not entity_id:
    raise MetadataApiException("get_entity requires an 'id' parameter")

  response['entity'] = api.get_entity(entity_id)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def add_tags(request):
  response = {'status': -1}

  api = NavigatorApi()
  entity_id = json.loads(request.POST.get('id', ''))
  tags = json.loads(request.POST.get('tags', []))

  if not entity_id or not tags or not isinstance(tags, list):
    response['error'] = _("add_tags requires an 'id' parameter and 'tags' parameter that is a non-empty list of tags")
  else:
    response['entity'] = api.add_tags(entity_id, tags)
    response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def delete_tags(request):
  response = {'status': -1}

  api = NavigatorApi()
  entity_id = json.loads(request.POST.get('id', ''))
  tags = json.loads(request.POST.get('tags', []))

  if not entity_id or not tags or not isinstance(tags, list):
    response['error'] = _("add_tags requires an 'id' parameter and 'tags' parameter that is a non-empty list of tags")
  else:
    response['entity'] = api.delete_tags(entity_id, tags)
    response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def update_properties(request):
  response = {'status': -1}

  api = NavigatorApi()
  entity_id = json.loads(request.POST.get('id', ''))
  properties = json.loads(request.POST.get('properties', {}))

  if not entity_id or not properties or not isinstance(properties, dict):
    response['error'] = _("update_properties requires an 'id' parameter and 'properties' parameter that is a non-empty dict")
  else:
    response['entity'] = api.update_properties(entity_id, properties)
    response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def delete_properties(request):
  response = {'status': -1}

  api = NavigatorApi()
  entity_id = json.loads(request.POST.get('id', ''))
  keys = json.loads(request.POST.get('keys', []))

  if not entity_id or not keys or not isinstance(keys, list):
    response['error'] = _("update_properties requires an 'id' parameter and 'keys' parameter that is a non-empty list")
  else:
    response['entity'] = api.delete_properties(entity_id, keys)
    response['status'] = 0

  return JsonResponse(response)
