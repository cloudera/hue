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

import itertools
import json
import logging
import re

from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException

from indexer.controller import CollectionManagerController
from indexer.solr_client import SolrClient
from indexer.utils import fields_from_log, field_values_from_separated_file, get_type_from_morphline_type, get_field_types


LOG = logging.getLogger(__name__)


def parse_fields(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  result = {'status': -1}

  source_type = request.POST.get('source')

  if source_type == 'file':
    content_type = request.POST.get('type')
    try:
      if content_type == 'separated':
        delimiter = request.POST.get('separator', ',')
        quote = request.POST.get('quote', '"')
        file_obj = request.fs.open(request.POST.get('path'))
        field_list = field_values_from_separated_file(file_obj, delimiter, quote)
        row = next(field_list)
        field_names = row.keys()
        field_types = get_field_types((row.values() for row in itertools.chain([row], field_list)), iterations=51)
        file_obj.close()

        result['data'] = zip(field_names, field_types)
        result['status'] = 0
      elif content_type == 'morphlines':
        morphlines = json.loads(request.POST.get('morphlines'))
        # Look for entries that take on the form %{SYSLOGTIMESTAMP:timestamp}
        field_results = re.findall(r'\%\{(?P<type>\w+)\:(?P<name>\w+)\}', morphlines['expression'])
        if field_results:
          result['data'] = []

          for field_result in field_results:
            result['data'].append( (field_result[1], get_type_from_morphline_type(field_result[0])) )

          result['status'] = 0
        else:
          result['status'] = 1
          result['message'] = _('Could not detect any fields.')
      elif content_type == 'log':
        file_obj = request.fs.open(request.POST.get('path'))
        result['data'] = fields_from_log(file_obj)
        file_obj.close()

        result['status'] = 0
      else:
        result['status'] = 1
        result['message'] = _('Type %s not supported.') % content_type
    except Exception, e:
      LOG.exception(e.message)
      result['message'] = e.message
  else:
    result['message'] = _('Source type %s not supported.') % source_type

  return JsonResponse(result)

def autocomplete(request):
  searcher = CollectionManagerController(request.user)
  autocomplete = searcher.get_autocomplete()

  massaged_collections = []

  for collection in autocomplete['collections']:
    massaged_collections.append({
      'name': collection,
      'isCollection': True,
      'isConfig': False,
    })

  for config in autocomplete['configs']:
    massaged_collections.append({
      'name': config,
      'isCollection': False,
      'isConfig': True,
    })

  response = {
    'status': 0,
    'collections': massaged_collections
  }

  return JsonResponse(response)


def collections(request):
  client = SolrClient(user=request.user)

  response = {
    'status': 0,
    'collections': client.get_indexes()
  }

  return JsonResponse(response)


def collections_create(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  response = {'status': -1}

  collection = json.loads(request.POST.get('collection', '{}'))

  if collection:
    searcher = CollectionManagerController(request.user)

    # Create instance directory, collection, and add fields
    searcher.create_collection(collection.get('name'), collection.get('fields', []), collection.get('uniqueKeyField'), collection.get('df'))

    try:
      if request.POST.get('source') == 'file':
        # Index data
        searcher.update_data_from_hdfs(request.fs,
                                       collection.get('name'),
                                       collection.get('fields', []),
                                       request.POST.get('path'),
                                       request.POST.get('type'),
                                       separator=request.POST.get('separator'),
                                       quote_character=request.POST.get('quote'))

      elif request.POST.get('source') == 'hive':
        # Run a custom hive query and post data to collection
        from beeswax.server import dbms

        db = dbms.get(request.user)

        database = request.POST.get('database')
        table = request.POST.get('table')
        columns = [field['name'] for field in collection.get('fields', [])]

        searcher.update_data_from_hive(db, collection.get('name'), database, table, columns) # Not up to date

      response['status'] = 0
      response['message'] = _('Collection created!')
    except Exception, e:
      LOG.error(e)
      raise
  else:
    response['message'] = _('Collection missing.')

  return JsonResponse(response)


def collections_import(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  response = {'status': -1}

  collection = json.loads(request.POST.get('collection', '{}'))

  if collection:
    searcher = CollectionManagerController(request.user)
    unique_key, fields = searcher.get_fields(collection.get('name'))

    # Create collection and metadata.
    hue_collection, created = Collection.objects.get_or_create(name=collection.get('name'), solr_properties='{}', is_enabled=True, user=request.user)
    properties_dict = hue_collection.properties_dict
    properties_dict['data_type'] = 'separated'
    properties_dict['field_order'] = [field_name for field_name in fields]
    hue_collection.properties = json.dumps(properties_dict)
    hue_collection.save()

    response['status'] = 0
    response['message'] = _('Collection created!')
  else:
    response['message'] = _('Collection missing.')

  return JsonResponse(response)

# Deprecated
def collections_remove(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  response = {'status': -1}

  collections = json.loads(request.POST.get('collections', '[]'))

  if not collections:
    response['message'] = _('No collections to remove.')

  if response.get('message', None) is None:
    searcher = CollectionManagerController(request.user)
    solr_collections = searcher.get_collections()

    for collection in collections:
      if collection.get('name') in solr_collections:
        # Remove collection and instancedir
        searcher.delete_collection(collection.get('name'), collection.get('isCoreOnly'))

    response['status'] = 0
    response['message'] = _('Collections removed!')

  return JsonResponse(response)


def collections_fields(request, collection):
  if request.method != 'GET':
    raise PopupException(_('GET request required.'))

  response = {}

  searcher = CollectionManagerController(request.user)
  unique_key, fields = searcher.get_fields(collection)

  response['status'] = 0
  response['fields'] = [(field, fields[field]['type'], fields[field].get('indexed', None), fields[field].get('stored', None)) for field in fields]
  response['unique_key'] = unique_key

  return JsonResponse(response)


def collections_update(request, collection):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  response = {'status': -1}

  collection = json.loads(request.POST.get('collection', '{}'))

  if not collection:
    response['message'] = _('No collection to update.')

  if response.get('message', None) is None:
    searcher = CollectionManagerController(request.user)
    searcher.update_collection(collection.get('name'), collection.get('fields', []))

    response['status'] = 0
    response['message'] = _('Collection updated!')

  return JsonResponse(response)


def collections_data(request, collection):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  response = {'status': -1}

  source = request.POST.get('source')

  if source == 'file':
    searcher = CollectionManagerController(request.user)

    searcher.update_data_from_hdfs(request.fs,
                                   collection,
                                   None,
                                   request.POST.get('path'),
                                   request.POST.get('type'),
                                   separator=request.POST.get('separator'),
                                   quote_character=request.POST.get('quote'))

    response['status'] = 0
    response['message'] = _('Index imported!')
  else:
    response['message'] = _('Unsupported source %s') % source

  return JsonResponse(response)
