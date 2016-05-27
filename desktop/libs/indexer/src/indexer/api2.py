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

import csv
import json
import logging

from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from libsolr.api import SolrApi
from search.conf import SOLR_URL, SECURITY_ENABLED

from indexer.controller2 import IndexController
from indexer.utils import get_default_fields


LOG = logging.getLogger(__name__)


def create_index(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  response = {'status': -1}

  name = request.POST.get('name')

  if name:
    searcher = IndexController(request.user)

    try:
      collection = searcher.create_index(
          name,
          request.POST.get('fields', get_default_fields()),
          request.POST.get('uniqueKeyField', 'id'),
          request.POST.get('df', 'text')
      )

      response['status'] = 0
      response['collection'] = collection
      response['message'] = _('Index created!')
    except Exception, e:
      response['message'] = _('Index could not be created: %s') % e
  else:
    response['message'] = _('Index requires a name field.')

  return JsonResponse(response)


def delete_indexes(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  response = {'status': -1}

  indexes = json.loads(request.POST.get('indexes', '[]'))

  if not indexes:
    response['message'] = _('No indexes to remove.')
  else:
    searcher = IndexController(request.user)

    for index in indexes:
      if index['type'] == 'collection':
        searcher.delete_index(index['name'])
      elif index['type'] == 'alias':
        searcher.delete_alias(index['name'])
      else:
        LOG.warn('We could not delete: %s' % index)

    response['status'] = 0
    response['message'] = _('Indexes removed!')

  return JsonResponse(response)


def create_or_edit_alias(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  response = {'status': -1}

  alias = request.POST.get('alias', '')
  collections = json.loads(request.POST.get('collections', '[]'))

  api = SolrApi(SOLR_URL.get(), request.user, SECURITY_ENABLED.get())

  try:
    api.create_or_modify_alias(alias, collections)
    response['status'] = 0
    response['message'] = _('Alias created or modified!')
  except Exception, e:
    response['message'] = _('Alias could not be created or modified: %s') % e

  return JsonResponse(response)


def create_wizard_get_sample(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  response = {'status': -1}

  wizard = json.loads(request.POST.get('wizard', '{}'))

  f = request.fs.open(wizard['path'])

  response['status'] = 0
  response['data'] = _read_csv(f)

  return JsonResponse(response)


def create_wizard_create(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  response = {'status': -1}

  wizard = json.loads(request.POST.get('wizard', '{}'))

  f = request.fs.open(wizard['path'])

  response['status'] = 0
  response['data'] = _read_csv(f)

  return JsonResponse(response)


def design_schema(request, index):
  if request.method == 'POST':
    pass # TODO: Support POST for update?

  result = {'status': -1, 'message': ''}

  try:
    searcher = IndexController(request.user)
    unique_key, fields = searcher.get_index_schema(index)

    result['status'] = 0
    formatted_fields = []
    for field in fields:
      formatted_fields.append({
        'name': field,
        'type': fields[field]['type'],
        'required': fields[field].get('required', None),
        'indexed': fields[field].get('indexed', None),
        'stored': fields[field].get('stored', None),
        'multivalued': fields[field].get('multivalued', None),
      })
    result['fields'] = formatted_fields
    result['unique_key'] = unique_key
  except Exception, e:
    result['message'] = _('Could not get index schema: %s') % e

  return JsonResponse(result)


def _read_csv(f):
  content = f.read(1024 * 1024)

  dialect = csv.Sniffer().sniff(content)
  lines = content.splitlines()[:5]
  reader = csv.reader(lines, delimiter=dialect.delimiter)
  
  return [row for row in reader]


