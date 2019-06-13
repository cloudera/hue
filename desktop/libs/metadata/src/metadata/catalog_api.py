#!/usr/bin/env python
# -- coding: utf-8 --
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
import re

from collections import OrderedDict

from django.http import Http404
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode, smart_str

from metadata.catalog.base import get_api
from metadata.catalog.navigator_client import CatalogApiException, CatalogEntityDoesNotExistException, CatalogAuthException
from metadata.conf import has_catalog, CATALOG, has_catalog_file_search, NAVIGATOR


LOG = logging.getLogger(__name__)


class MetadataApiException(Exception):
  pass


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    status = 500
    response = {
      'message': ''
    }

    try:
      if has_catalog(args[0].user):
        return view_fn(*args, **kwargs)
      else:
        raise MetadataApiException('Catalog API is not configured.')
    except Http404, e:
      raise e
    except CatalogEntityDoesNotExistException, e:
      response['message'] = e.message
      status = 404
    except CatalogAuthException, e:
      response['message'] = force_unicode(e.message)
      status = 403
    except CatalogApiException, e:
      try:
        response['message'] = json.loads(e.message)
      except Exception:
        response['message'] = force_unicode(e.message)
    except Exception, e:
      message = force_unicode(e)
      response['message'] = message
      LOG.exception(message)

    return JsonResponse(response, status=status)
  return decorator


@error_handler
def search_entities_interactive(request):
  """
  For search autocomplete.
  """
  interface = request.POST.get('interface', CATALOG.INTERFACE.get())
  query_s = json.loads(request.POST.get('query_s', ''))
  prefix = request.POST.get('prefix')
  offset = request.POST.get('offset', 0)
  limit = int(request.POST.get('limit', 25))
  field_facets = json.loads(request.POST.get('field_facets') or '[]')
  sources = json.loads(request.POST.get('sources') or '[]')

  api = get_api(request=request, interface=interface)

  if sources and not has_catalog_file_search(request.user):
    sources = ['sql']

  response = api.search_entities_interactive(
      query_s=query_s,
      limit=limit,
      offset=offset,
      facetFields=field_facets,
      facetPrefix=prefix,
      facetRanges=None,
      firstClassEntitiesOnly=None,
      sources=sources
  )

  if response.get('facets'): # Remove empty facets
    for fname, fvalues in response['facets'].items():
      # Should be a CATALOG option at some point for hidding table with no access / asking for access.
      if interface == 'navigator' and NAVIGATOR.APPLY_SENTRY_PERMISSIONS.get():
        fvalues = []
      else:
        fvalues = sorted([(k, v) for k, v in fvalues.items() if v > 0], key=lambda n: n[1], reverse=True)
      response['facets'][fname] = OrderedDict(fvalues)
      if ':' in query_s and not response['facets'][fname]:
        del response['facets'][fname]


  _augment_highlighting(query_s, response.get('results'))

  response['status'] = 0

  return JsonResponse(response)


@error_handler
def search_entities(request):
  """
  For displaying results.
  """
  interface = request.POST.get('interface', CATALOG.INTERFACE.get())
  query_s = json.loads(request.POST.get('query_s', ''))
  query_s = smart_str(query_s)

  offset = request.POST.get('offset', 0)
  limit = int(request.POST.get('limit', 100))
  raw_query = request.POST.get('raw_query', False)
  sources = json.loads(request.POST.get('sources') or '[]')
  if sources and not has_catalog_file_search(request.user):
    sources = ['sql']

  query_s = query_s.strip() or '*'

  api = get_api(request=request, interface=interface)

  entities = api.search_entities(query_s, limit=limit, offset=offset, raw_query=raw_query, sources=sources)

  if not raw_query:
    _augment_highlighting(query_s, entities)

  response = {
    'entities': entities,
    'count': len(entities),
    'offset': offset,
    'limit': limit,
    'query_s': query_s,
    'status': 0
  }

  return JsonResponse(response)


def _augment_highlighting(query_s, records):
  fs = {}
  ts = []
  for term in query_s.split():
    if ':' in term:
      fname, fval = term.split(':', 1)
      if fval and fval.strip('*'):
        fs[fname] = fval.strip('*')
    else:
      if term.strip('*'):
        ts.append(term.strip('*'))

  for record in records:
    name = record.get('originalName', '') or ''
    record['hue_description'] = ''
    record['hue_name'] = record.get('parentPath', '') if record.get('parentPath') else ''
    if record.get('parentPath') is None:
      record['parentPath'] = ''

    if record['hue_name'] and record.get('sourceType', '') != 'S3':
      record['hue_name'] = (record['hue_name'].replace('/', '.') + '.').lstrip('.')

    record['originalName'] = record['hue_name'] + name # Inserted when selected in autocomplete, full path
    record['selectionName'] = name # Use when hovering / selecting a search result

    for term in ts:
      name = _highlight(term, name)
      if record.get('tags'):
        _highlight_tags(record, term)
    for fname, fval in fs.iteritems(): # e.g. owner:<em>hu</em>e
      if record.get(fname, ''):
        if fname == 'tags':
          _highlight_tags(record, fval)
        else:
          record['hue_description'] += ' %s:%s' % (fname, _highlight(fval, record[fname]))

    originalDescription = record.get('originalDescription', '')
    if not record['hue_description'] and originalDescription:
      record['hue_description'] = _highlight(term, originalDescription)

    record['hue_name'] += name
    record['hue_name'] = escape(record['hue_name']).replace('&lt;em&gt;', '<em>').replace('&lt;/em&gt;', '</em>')
    record['hue_description'] = escape(record['hue_description']).replace('&lt;em&gt;', '<em>').replace('&lt;/em&gt;', '</em>')


def _highlight(pattern, string):
  pattern = re.escape(pattern)
  return re.compile('(%s)' % pattern, re.IGNORECASE).sub('<em>\\1</em>', string, count=1)


def _highlight_tags(record, term):
  for tag in record['tags']:
    if re.match(term, tag):
      record['hue_description'] += ' tags:%s' % _highlight(term, tag)


@error_handler
def list_tags(request):
  interface = request.POST.get('interface', CATALOG.INTERFACE.get())
  prefix = request.POST.get('prefix')
  offset = request.POST.get('offset', 0)
  limit = request.POST.get('limit', 25)

  api = get_api(request=request, interface=interface)

  data = api.search_entities_interactive(facetFields=['tags'], facetPrefix=prefix, limit=limit, offset=offset)

  response = {
    'tags': data['facets']['tags'],
    'status': 0
  }

  return JsonResponse(response)


@error_handler
def find_entity(request):
  response = {'status': -1}

  interface = request.GET.get('interface', CATALOG.INTERFACE.get())
  entity_type = request.GET.get('type', '')
  database = request.GET.get('database', '')
  table = request.GET.get('table', '')
  name = request.GET.get('name', '')
  path = request.GET.get('path', '')

  api = get_api(request=request, interface=interface)

  if not entity_type:
    raise MetadataApiException("find_entity requires a type value, e.g. - 'database', 'table', 'file'")

  if entity_type.lower() == 'database':
    if not name:
      raise MetadataApiException('get_database requires name param')
    response['entity'] = api.get_database(name)
  elif entity_type.lower() == 'table' or entity_type.lower() == 'view':
    if not database or not name:
      raise MetadataApiException('get_table requires database and name param')
    is_view = entity_type.lower() == 'view'
    response['entity'] = api.get_table(database, name, is_view=is_view)
  elif entity_type.lower() == 'field':
    if not database or not table or not name:
      raise MetadataApiException('get_field requires database, table, and name params')
    response['entity'] = api.get_field(database, table, name)
  elif entity_type.lower() == 'directory':
    if not path:
      raise MetadataApiException('get_directory requires path param')
    response['entity'] = api.get_directory(path)
  elif entity_type.lower() == 'file':
    if not path:
      raise MetadataApiException('get_file requires path param')
    response['entity'] = api.get_file(path)
  else:
    raise MetadataApiException("type %s is unrecognized" % entity_type)

  # Prevent nulls later
  if 'tags' in response['entity'] and not response['entity']['tags']:
    response['entity']['tags'] = []

  response['status'] = 0
  return JsonResponse(response)


@error_handler
def suggest(request):
  response = {'status': -1}

  interface = request.POST.get('interface', CATALOG.INTERFACE.get())
  prefix = request.POST.get('prefix')

  api = get_api(request=request, interface=interface)

  suggest = api.suggest(prefix)

  response['suggest'] = suggest
  response['status'] = 0

  return JsonResponse(response)


@error_handler
def get_entity(request):
  response = {'status': -1}

  interface = request.GET.get('interface', CATALOG.INTERFACE.get())
  entity_id = request.GET.get('id')

  api = get_api(request=request, interface=interface)

  if not entity_id:
    raise MetadataApiException("get_entity requires an 'id' parameter")

  entity = api.get_entity(entity_id)

  response['entity'] = entity
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def add_tags(request):
  interface = request.POST.get('interface', CATALOG.INTERFACE.get())
  entity_id = json.loads(request.POST.get('id', '""'))
  tags = json.loads(request.POST.get('tags', "[]"))

  api = get_api(request=request, interface=interface)

  is_allowed = request.user.has_hue_permission(action='write', app='metadata')

  request.audit = {
    'allowed': is_allowed,
    'operation': '%s_ADD_TAG' % interface.upper(),
    'operationText': 'Adding tags %s to entity %s' % (tags, entity_id)
  }

  if not is_allowed:
    raise Exception("The user does not have proper Hue permissions to add %s tags." % interface.title())
  if not entity_id:
    raise Exception("Missing required parameter 'id' in add_tags API.")
  if not tags:
    raise Exception("Missing required parameter 'tags' in add_tags API.")

  return JsonResponse(api.add_tags(entity_id, tags))


@require_POST
@error_handler
def delete_tags(request):
  interface = request.POST.get('interface', CATALOG.INTERFACE.get())
  entity_id = json.loads(request.POST.get('id', '""'))
  tags = json.loads(request.POST.get('tags', '[]'))

  api = get_api(request=request, interface=interface)

  is_allowed = request.user.has_hue_permission(action='write', app='metadata')

  request.audit = {
    'allowed': is_allowed,
    'operation': '%s_DELETE_TAG' % interface.upper(),
    'operationText': 'Removing tags %s to entity %s' % (tags, entity_id)
  }

  if not is_allowed:
    raise Exception("The user does not have proper Hue permissions to delete %s tags." % interface.title())
  if not entity_id:
    raise Exception("Missing required parameter 'id' in delete_tags API.")
  if not tags:
    raise Exception("Missing required parameter 'tags' in delete_tags API.")

  return JsonResponse(api.delete_tags(entity_id, tags))


@require_POST
@error_handler
def update_properties(request):
  interface = request.POST.get('interface', CATALOG.INTERFACE.get())
  entity_id = json.loads(request.POST.get('id', '""'))
  properties = json.loads(request.POST.get('properties', '{}')) # Entity properties
  modified_custom_metadata = json.loads(request.POST.get('modifiedCustomMetadata', '{}')) # Aka "Custom Metadata"
  deleted_custom_metadata_keys = json.loads(request.POST.get('deletedCustomMetadataKeys', '[]'))

  api = get_api(request=request, interface=interface)

  is_allowed = request.user.has_hue_permission(action='write', app='metadata')

  request.audit = {
    'allowed': is_allowed,
    'operation': '%s_UPDATE_PROPERTIES' % interface.upper(),
    'operationText': 'Updating custom metadata %s, deleted custom metadata keys %s and properties %s of entity %s' % (modified_custom_metadata, deleted_custom_metadata_keys, properties, entity_id)
  }

  if not entity_id:
    # TODO: raise HueApiException(message="Missing required parameter 'id' for update_properties", source="Hue")
    # source so the user knows which service that failed right away, in UI: "[source] responded with error: [message]"
    raise Exception("Missing required parameter 'id' in update_properties API.")

  if not is_allowed:
    # TODO: HueAuthException?
    raise Exception("The user does not have proper Hue permissions to update %s properties." % interface.title())

  return JsonResponse(api.update_properties(entity_id, properties, modified_custom_metadata, deleted_custom_metadata_keys))


@require_POST
@error_handler
def delete_metadata_properties(request):
  response = {'status': -1}

  interface = request.POST.get('interface', CATALOG.INTERFACE.get())
  entity_id = json.loads(request.POST.get('id', '""'))
  keys = json.loads(request.POST.get('keys', '[]'))

  api = get_api(request=request, interface=interface)

  is_allowed = request.user.has_hue_permission(action='write', app='metadata')

  request.audit = {
    'allowed': is_allowed,
    'operation': '%s_DELETE_METADATA_PROPERTIES' % interface.upper(),
    'operationText': 'Deleting metadata %s of entity %s' % (keys, entity_id)
  }

  if not entity_id or not keys or not isinstance(keys, list):
    response['error'] = _("update_properties requires an 'id' parameter and 'keys' parameter that is a non-empty list")
  else:
    response['entity'] = api.delete_metadata_properties(entity_id, keys)
    response['status'] = 0

  return JsonResponse(response)


@error_handler
def get_lineage(request):
  response = {'status': -1, 'inputs': [], 'source_query': '', 'target_queries': [], 'targets': []}

  interface = request.GET.get('interface', CATALOG.INTERFACE.get())
  entity_id = request.GET.get('id')

  api = get_api(request=request, interface=interface)

  if not entity_id:
    raise MetadataApiException("get_lineage requires an 'id' parameter")

  lineage = api.get_lineage(entity_id)
  entity_name = api.get_entity(entity_id)['originalName'].upper()

  response['id'] = entity_id

  # TODO: This is a cheat way to do to this for demo using filtering but we should really traverse relationships
  parent_operation = next((entity for entity in lineage['entities'] if entity.get('outputs', []) == [entity_name]), None)
  if parent_operation:
    response['inputs'] = [input.lower() for input in parent_operation['inputs']]
    response['source_query'] = parent_operation.get('queryText', '')

  children = [entity for entity in lineage['entities'] if entity.get('inputs') is not None and entity_name in entity.get('inputs')]
  if children is not None:
    response['target_queries'] = [child['queryText'] for child in children if child.get('queryText') is not None]
    outputs = [child['outputs'] for child in children if child.get('outputs') is not None]
    response['targets'] = [target.lower() for output in outputs for target in output]

  response['status'] = 0

  return JsonResponse(response)


@error_handler
def create_namespace(request):
  interface = request.POST.get('interface', CATALOG.INTERFACE.get())
  namespace = request.POST.get('namespace')
  description = request.POST.get('description')

  api = get_api(request=request, interface=interface)

  request.audit = {
    'allowed': request.user.has_hue_permission(action='write', app='metadata'),
    'operation': '%s_CREATE_NAMESPACE' % interface.upper(),
    'operationText': 'Creating namespace %s' % namespace
  }

  namespace = api.create_namespace(namespace=namespace, description=description)

  return JsonResponse(namespace)


@error_handler
def get_namespace(request):
  interface = request.POST.get('interface', CATALOG.INTERFACE.get())
  namespace = request.POST.get('namespace')

  api = get_api(request=request, interface=interface)

  namespace = api.get_namespace(namespace)

  return JsonResponse(namespace)


@error_handler
def create_namespace_property(request):
  """
  {
  "name" : "relatedEntities",
  "displayName" : "Related objects",
  "creator" : "admin",
  "description" : "My desc",,
  "multiValued" : true,
  "maxLength" : 50,
  "pattern" : ".*",
  "enumValues" : null,
  "type" : "TEXT",
  "createdDate" : "2018-04-02T22:36:19.001Z"
}"""
  interface = request.POST.get('interface', CATALOG.INTERFACE.get())
  namespace = request.POST.get('namespace')
  properties = json.loads(request.POST.get('properties', '{}'))

  api = get_api(request=request, interface=interface)

  namespace = api.create_namespace_property(namespace, properties)

  return JsonResponse(namespace)


@error_handler
def map_namespace_property(request):
  """
  {
  namespace: "huecatalog",
  name: "relatedEntities"
  }"""
  interface = request.POST.get('interface', CATALOG.INTERFACE.get())
  clazz = request.POST.get('class')
  properties = json.loads(request.POST.get('properties', '[]'))

  api = get_api(request=request, interface=interface)

  namespace = api.map_namespace_property(clazz=clazz, properties=properties)

  return JsonResponse(namespace)


@error_handler
def get_model_properties_mapping(request):
  interface = request.POST.get('interface', CATALOG.INTERFACE.get())

  api = get_api(request=request, interface=interface)

  namespace = api.get_model_properties_mapping()

  return JsonResponse(namespace)
