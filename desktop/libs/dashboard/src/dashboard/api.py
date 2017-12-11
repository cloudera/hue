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

from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import RestException

from libsolr.api import SolrApi

from search.conf import SOLR_URL

from dashboard.controller import can_edit_index
from dashboard.dashboard_api import get_engine
from dashboard.data_export import download as export_download
from dashboard.decorators import allow_viewer_only
from dashboard.facet_builder import _guess_gap, _zoom_range_facet, _new_range_facet
from dashboard.models import Collection2, augment_solr_response, pairwise2, augment_solr_exception,\
  NESTED_FACET_FORM


LOG = logging.getLogger(__name__)


@allow_viewer_only
def search(request):
  response = {}

  collection = json.loads(request.POST.get('collection', '{}'))
  query = json.loads(request.POST.get('query', '{}'))
  facet = json.loads(request.POST.get('facet', '{}'))

  query['download'] = 'download' in request.POST
  fetch_result = 'fetch_result' in request.POST

  if collection:
    try:
      if fetch_result:
        response = get_engine(request.user, collection).fetch_result(collection, query, facet)
      else:
        response = get_engine(request.user, collection).query(collection, query, facet)
    except RestException, e:
      response.update(extract_solr_exception_message(e))
    except Exception, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

      response['error'] = force_unicode(e)
  else:
    response['error'] = _('There is no collection to search.')

  if 'error' in response:
    augment_solr_exception(response, collection)

  return JsonResponse(response)


def query_suggest(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  collection = json.loads(request.POST.get('collection', '{}'))
  query = request.POST.get('query', '')

  result = {'status': -1, 'message': ''}

  solr_query = {}
  solr_query['q'] = query
  solr_query['dictionary'] = collection['suggest']['dictionary']

  try:
    response = SolrApi(SOLR_URL.get(), request.user).suggest(collection['name'], solr_query)
    result['response'] = response
    result['status'] = 0
  except Exception, e:
    result['message'] = force_unicode(e)

  return JsonResponse(result)


def index_fields_dynamic(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    name = request.POST['name']
    engine = request.POST['engine']

    dynamic_fields = get_engine(request.user, engine).luke(name)

    result['message'] = ''
    result['fields'] = [
        Collection2._make_field(name, properties)
        for name, properties in dynamic_fields['fields'].iteritems() if 'dynamicBase' in properties
    ]
    result['gridlayout_header_fields'] = [
        Collection2._make_gridlayout_header_field({'name': name, 'type': properties.get('type')}, True)
        for name, properties in dynamic_fields['fields'].iteritems() if 'dynamicBase' in properties
    ]
    result['status'] = 0
  except Exception, e:
    result['message'] = force_unicode(e)

  return JsonResponse(result)


def nested_documents(request):
  result = {'status': -1, 'message': 'Error'}

  response = {}

  collection = json.loads(request.POST.get('collection', '{}'))
  query = {'qs': [{'q': '_root_:*'}], 'fqs': [], 'start': 0, 'limit': 0}

  try:
    response = get_engine(request.user, collection).query(collection, query)
    result['has_nested_documents'] = response['response']['numFound'] > 0
    result['status'] = 0
  except Exception, e:
    LOG.exception('Failed to list nested documents')
    result['message'] = force_unicode(e)
    result['has_nested_documents'] = False

  return JsonResponse(result)


@allow_viewer_only
def get_document(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    collection = json.loads(request.POST.get('collection', '{}'))
    doc_id = request.POST.get('id')

    if doc_id:
      result['doc'] = get_engine(request.user, collection).get(collection, doc_id)
      if result['doc']['doc']:
        result['status'] = 0
        result['message'] = ''
      else:
        result['status'] = 1
        result['message'] = _('No document was returned by Solr.')
    else:
      result['message'] = _('This document does not have any index id.')
      result['status'] = 1

  except Exception, e:
    result['message'] = force_unicode(e)

  return JsonResponse(result)


@allow_viewer_only
def update_document(request):
  result = {'status': -1, 'message': 'Error'}

  if not can_edit_index(request.user):
    result['message'] = _('Permission to edit the document denied')
    return JsonResponse(result)

  try:
    collection = json.loads(request.POST.get('collection', '{}'))
    document = json.loads(request.POST.get('document', '{}'))
    doc_id = request.POST.get('id')

    if document['hasChanged']:
      edits = {
          "id": doc_id,
      }
      version = None # If there is a version, use it to avoid potential concurrent update conflicts

      for field in document['details']:
        if field['hasChanged'] and field['key'] != '_version_':
          edits[field['key']] = {"set": field['value']}
        if field['key'] == '_version_':
          version = field['value']

      result['update'] = SolrApi(SOLR_URL.get(), request.user).update(collection['name'], json.dumps([edits]), content_type='json', version=version)
      result['message'] = _('Document successfully updated.')
      result['status'] = 0
    else:
      result['status'] = 0
      result['message'] = _('Document has no modifications to change.')
  except RestException, e:
    try:
      result['message'] = json.loads(e.message)['error']['msg']
    except:
      LOG.exception('Failed to parse json response')
      result['message'] = force_unicode(e)
  except Exception, e:
    result['message'] = force_unicode(e)

  return JsonResponse(result)


@allow_viewer_only
def get_stats(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    collection = json.loads(request.POST.get('collection', '{}'))
    query = json.loads(request.POST.get('query', '{}'))
    analysis = json.loads(request.POST.get('analysis', '{}'))

    field = analysis['name']
    facet = analysis['stats']['facet']

    result['stats'] = get_engine(request.user, collection).stats(collection['name'], [field], query, facet)
    result['status'] = 0
    result['message'] = ''

  except Exception, e:
    LOG.exception('Failed to get stats for field')
    result['message'] = force_unicode(e)
    if 'not currently supported' in result['message']:
      result['status'] = 1
      result['message'] = _('This field type does not support stats')

  return JsonResponse(result)


@allow_viewer_only
def get_terms(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    collection = json.loads(request.POST.get('collection', '{}'))
    analysis = json.loads(request.POST.get('analysis', '{}'))
    limit = json.loads(request.POST.get('limit', '25'))

    field = analysis['name']
    properties = {
      'terms.limit': limit,
      # lower
      # mincount
      # maxcount
    }
    if analysis['terms']['prefix']:
      properties['terms.prefix'] = analysis['terms']['prefix']

    result['terms'] = SolrApi(SOLR_URL.get(), request.user).terms(collection['name'], field, properties)
    result['terms'] = pairwise2(field, [], result['terms']['terms'][field])
    result['status'] = 0
    result['message'] = ''

  except Exception, e:
    result['message'] = force_unicode(e)
    if 'not currently supported' in result['message']:
      result['status'] = 1
      result['message'] = _('This field does not support stats')

  return JsonResponse(result)


@allow_viewer_only
def download(request):
  try:
    file_format = 'csv' if 'csv' == request.POST.get('type') else 'xls' if 'xls' == request.POST.get('type') else 'json'
    facet = json.loads(request.POST.get('facet', '{}'))

    json_response = search(request)
    response = json.loads(json_response.content)

    if facet:
      response['response']['docs'] = response['normalized_facets'][0]['docs']
      collection = facet
    else:
      collection = json.loads(request.POST.get('collection', '{}'))

    if file_format == 'json':
      docs = response['response']['docs']
      resp = JsonResponse(docs, safe=False)
      resp['Content-Disposition'] = 'attachment; filename=%s.%s' % ('query_result', file_format)
      return resp
    else:
      return export_download(response, file_format, collection)
  except Exception, e:
    raise PopupException(_("Could not download search results: %s") % e)


@allow_viewer_only
def get_timeline(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    collection = json.loads(request.POST.get('collection', '{}'))
    query = json.loads(request.POST.get('query', '{}'))
    facet = json.loads(request.POST.get('facet', '{}'))
    qdata = json.loads(request.POST.get('qdata', '{}'))
    multiQ = request.POST.get('multiQ', 'query')

    if multiQ == 'query':
      label = qdata['q']
      query['qs'] = [qdata]
    elif facet['type'] == 'range':
      _prop = filter(lambda prop: prop['from'] == qdata, facet['properties'])[0]
      label = '%(from)s - %(to)s ' % _prop
      facet_id = facet['id']
      # Only care about our current field:value filter
      for fq in query['fqs']:
        if fq['id'] == facet_id:
          fq['properties'] = [_prop]
    else:
      label = qdata
      facet_id = facet['id']
      # Only care about our current field:value filter
      for fq in query['fqs']:
        if fq['id'] == facet_id:
          fq['filter'] = [{'value': qdata, 'exclude': False}]

    # Remove other facets from collection for speed
    collection['facets'] = filter(lambda f: f['widgetType'] == 'histogram-widget', collection['facets'])

    response = SolrApi(SOLR_URL.get(), request.user).query(collection, query)
    response = augment_solr_response(response, collection, query)

    label += ' (%s) ' % response['response']['numFound']

    result['series'] = {'label': label, 'counts': response['normalized_facets'][0]['counts']}
    result['status'] = 0
    result['message'] = ''
  except Exception, e:
    result['message'] = force_unicode(e)

  return JsonResponse(result)


@allow_viewer_only
def new_facet(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    collection = json.loads(request.POST.get('collection', '{}'))

    facet_id = request.POST['id']
    facet_label = request.POST['label']
    facet_field = request.POST['field']
    widget_type = request.POST['widget_type']

    result['message'] = ''
    result['facet'] = _create_facet(collection, request.user, facet_id, facet_label, facet_field, widget_type)
    result['status'] = 0
  except Exception, e:
    result['message'] = force_unicode(e)

  return JsonResponse(result)


def _create_facet(collection, user, facet_id, facet_label, facet_field, widget_type):
  properties = {
    'sort': 'desc',
    'canRange': False,
    'stacked': False,
    'limit': 10,
    'mincount': 1,
    'isDate': False,
    'aggregate': {'function': 'unique', 'formula': '', 'plain_formula': '', 'percentile': 50}
  }

  if widget_type in ('tree-widget', 'heatmap-widget', 'map-widget'):
    facet_type = 'pivot'
  elif widget_type == 'document-widget':
    # SQL query, 1 solr widget
    properties['uuid'] = facet_field
    properties['engine'] = 'impala'
    properties['statement'] = 'select * from web_logs limit 50'
    properties['facets'] = [{'canRange': False, 'field': 'blank', 'limit': 10, 'mincount': 1, 'sort': 'desc', 'aggregate': {'function': 'count'}, 'isDate': False}]
    facet_type = 'statement'
  else:
    api = get_engine(user, collection)
    range_properties = _new_range_facet(api, collection, facet_field, widget_type)

    if range_properties:
      facet_type = 'range'
      properties.update(range_properties)
      properties['initial_gap'] = properties['gap']
      properties['initial_start'] = properties['start']
      properties['initial_end'] = properties['end']
    else:
      facet_type = 'field'

    if widget_type in ('bucket-widget', 'pie2-widget', 'timeline-widget', 'tree2-widget', 'text-facet-widget', 'hit-widget', 'gradient-map-widget'):
      # properties = {'canRange': False, 'stacked': False, 'limit': 10} # TODO: Lighter weight top nested facet

      if widget_type == 'text-facet-widget':
        properties['type'] = facet_type

      properties['facets_form'] = NESTED_FACET_FORM
      # Not supported on dim 2 currently
      properties['facets_form']['type'] = 'field'
      properties['facets_form']['canRange'] = False
      properties['facets_form']['isFacetForm'] = True

      facet = NESTED_FACET_FORM.copy()
      facet['field'] = facet_field
      facet['limit'] = 10

      if range_properties:
        # TODO: timeline still uses properties from top properties
        facet.update(range_properties)
        facet['initial_gap'] = facet['gap']
        facet['initial_start'] = facet['start']
        facet['initial_end'] = facet['end']
        facet['stacked'] = False
        facet['type'] = 'range'
      else:
        facet['type'] = facet_type

      if collection.get('engine', 'solr') != 'solr':
        facet['sort'] = 'default'

      properties['facets'] = [facet]
      properties['domain'] = {'blockParent': [], 'blockChildren': []}

      if widget_type == 'hit-widget':
        facet_type = 'function'
        facet['aggregate']['function'] = 'unique'
      else:
        facet_type = 'nested'
        facet['aggregate']['function'] = 'count'

      if widget_type == 'pie2-widget':
        properties['scope'] = 'stack'
        properties['timelineChartType'] = 'bar'
      elif widget_type == 'tree2-widget':
        properties['scope'] = 'tree'
        properties['facets_form']['limit'] = 5
        properties['isOldPivot'] = True
      elif widget_type == 'gradient-map-widget':
        properties['scope'] = 'world'
        facet['limit'] = 100
      else:
        properties['scope'] = 'stack'
        properties['timelineChartType'] = 'bar'

  if widget_type in ('tree-widget', 'heatmap-widget', 'map-widget') and widget_type != 'gradient-map-widget':
    properties['mincount'] = 1
    properties['facets'] = []
    properties['stacked'] = True
    properties['facets_form'] = {'field': '', 'mincount': 1, 'limit': 5}

    if widget_type == 'map-widget':
      properties['scope'] = 'world'
      properties['limit'] = 100
    else:
      properties['scope'] = 'stack' if widget_type == 'heatmap-widget' else 'tree'

  if widget_type == 'histogram-widget':
    properties['enableSelection'] = True
    properties['timelineChartType'] = 'bar'
    properties['extraSeries'] = []

  return {
    'id': facet_id,
    'label': facet_label,
    'field': facet_field,
    'type': facet_type,
    'widgetType': widget_type,
    'properties': properties,
    # Hue 4+
    'template': {
        "showFieldList": True,
        "showGrid": False,
        "showChart": True,
        "chartSettings" : {
          'chartType': 'pie' if widget_type == 'pie2-widget' else ('timeline' if widget_type == 'timeline-widget' else ('gradientmap' if widget_type == 'gradient-map-widget' else 'bars')),
          'chartSorting': 'none',
          'chartScatterGroup': None,
          'chartScatterSize': None,
          'chartScope': 'world',
          'chartX': None,
          'chartYSingle': None,
          'chartYMulti': [],
          'chartData': [],
          'chartMapLabel': None,
        },
        "fieldsAttributes": [],
        "fieldsAttributesFilter": "",
        "filteredAttributeFieldsAll": True,
        "fields": [],
        "fieldsSelected": [],
        "leafletmap": {'latitudeField': None, 'longitudeField': None, 'labelField': None}, # Use own?
        'leafletmapOn': False,
        'isGridLayout': False,
        "hasDataForChart": True,
        "rows": 25,
    },
    'queryResult': {}
  }


@allow_viewer_only
def get_range_facet(request):
  result = {'status': -1, 'message': ''}

  try:
    collection = json.loads(request.POST.get('collection', '{}'))
    facet = json.loads(request.POST.get('facet', '{}'))
    action = request.POST.get('action', 'select')

    solr_api = SolrApi(SOLR_URL.get(), request.user)

    if action == 'select':
      properties = _guess_gap(solr_api, collection, facet, facet['properties']['start'], facet['properties']['end'])
    else:
      properties = _zoom_range_facet(solr_api, collection, facet) # Zoom out

    result['properties'] = properties
    result['status'] = 0

  except Exception, e:
    result['message'] = force_unicode(e)

  return JsonResponse(result)


def get_collection(request):
  result = {'status': -1, 'message': ''}

  try:
    name = request.POST['name']
    engine = request.POST['engine']

    collection = Collection2(request.user, name=name, engine=engine)
    collection_json = collection.get_json(request.user)

    result['collection'] = json.loads(collection_json)
    result['status'] = 0

  except Exception, e:
    result['message'] = force_unicode(e)

  return JsonResponse(result)


def get_collections(request):
  result = {'status': -1, 'message': ''}

  try:
    collection = json.loads(request.POST.get('collection'))
    show_all = json.loads(request.POST.get('show_all'))

    result['collection'] = get_engine(request.user, collection).datasets(show_all=show_all)
    result['status'] = 0

  except Exception, e:
    if 'does not have privileges' in str(e):
      result['status'] = 0
      result['collection'] = [json.loads(request.POST.get('collection'))['name']]
    else:
      result['message'] = force_unicode(e)

  return JsonResponse(result)


def extract_solr_exception_message(e):
  response = {}

  try:
    message = json.loads(e.message)
    msg = message['error'].get('msg')
    response['error'] = msg if msg else message['error']['trace']
  except Exception, e2:
    LOG.exception('Failed to extract json message: %s' % force_unicode(e2))
    LOG.exception('Failed to parse json response: %s' % force_unicode(e))
    response['error'] = force_unicode(e)

  return response
