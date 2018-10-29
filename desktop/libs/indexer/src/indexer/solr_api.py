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
from django.views.decorators.http import require_GET, require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import smart_unicode
from libsolr.api import SolrApi

from indexer.solr_client import SolrClient


LOG = logging.getLogger(__name__)


def api_error_handler(func):
  def decorator(*args, **kwargs):
    response = {}

    try:
      return func(*args, **kwargs)
    except Exception, e:
      LOG.exception('Error running %s' % func.__name__)
      response['status'] = -1
      response['message'] = smart_unicode(e)
    finally:
      if response:
        return JsonResponse(response)

  return decorator


@require_POST
@api_error_handler
def list_indexes(request):
  response = {'status': -1}

  client = SolrClient(user=request.user)

  response['collections'] = client.get_indexes()
  response['status'] = 0

  return JsonResponse(response)


@api_error_handler
def list_index(request):
  response = {'status': -1}

  name = request.POST.get('name')

  client = SolrClient(user=request.user)

  response['schema'] = client.list_schema(name)
  response['name'] = name
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@api_error_handler
def delete_collections(request):
  response = {'status': -1}

  names = request.POST.get_list('name')

  api = SolrApi(user=request.user)

  response['statuses'] = [api.remove_collection(name) for name in names]
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@api_error_handler
def create_index(request):
  response = {'status': -1}

  name = request.POST.get('name')
  fields = json.loads(request.POST.get('fields', '[]'))
  unique_key_field = request.POST.get('unique_key_field')
  df = request.POST.get('df')

  client = SolrClient(request.user)

  collection = client.create_index(
      name=name,
      fields=fields,
      unique_key_field=unique_key_field,
      df=df
  )

  response['status'] = 0
  response['collection'] = collection
  response['message'] = _('Index created!')

  return JsonResponse(response)


@require_POST
@api_error_handler
def delete_indexes(request):
  response = {'status': -1}

  indexes = json.loads(request.POST.get('indexes', '[]'))

  if not indexes:
    response['message'] = _('No indexes to remove.')
  else:
    client = SolrClient(request.user)

    for index in indexes:
      if index['type'] == 'collection':
        client.delete_index(index['name'], keep_config=False)
      elif index['type'] == 'alias':
        client.delete_alias(index['name'])
      else:
        LOG.warn('We could not delete: %s' % index)

    response['status'] = 0
    response['message'] = _('Indexes removed!')

  return JsonResponse(response)

@require_POST
@api_error_handler
def index(request):
  response = {'status': -1}

  name = request.POST.get('name')
  data = request.POST.get('data')
  client = SolrClient(request.user)
  client.index(name, data)
  response['status'] = 0
  response['message'] = _('Data added')

  return JsonResponse(response)

@require_POST
@api_error_handler
def create_alias(request):
  response = {'status': -1}

  name = request.POST.get('name', '')
  collections = json.loads(request.POST.get('collections', '[]'))

  client = SolrClient(request.user)

  response['status'] = 0
  response['response'] = client.create_alias(name, collections)
  response['alias'] = {'name': name, 'type': 'alias', 'collections': collections, 'isSelected': False}
  response['message'] = _('Alias created or modified!')

  return JsonResponse(response)


@require_POST
@api_error_handler
def sample_index(request):
  response = {'status': -1}

  name = request.POST.get('name')

  client = SolrClient(user=request.user)

  response['sample'] = client.sample_index(name)['response']['docs']
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@api_error_handler
def config_index(request):
  response = {'status': -1}

  name = request.POST.get('name')

  client = SolrClient(user=request.user)

  response['config'] = json.dumps(client.get_config(name), indent=2)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@api_error_handler
def list_configs(request):
  response = {'status': -1}

  client = SolrClient(user=request.user)

  response['configs'] = client.list_configs()
  response['status'] = 0

  return JsonResponse(response)
