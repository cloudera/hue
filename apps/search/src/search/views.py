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
from django.utils.html import escape
from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import RestException
from desktop.models import Document2, Document

from libsolr.api import SolrApi
from indexer.management.commands import indexer_setup

from search.api import _guess_gap, _zoom_range_facet, _new_range_facet
from search.conf import SOLR_URL, LATEST
from search.data_export import download as export_download
from search.decorators import allow_owner_only, allow_viewer_only
from search.management.commands import search_setup
from search.models import Collection2, augment_solr_response, augment_solr_exception, pairwise2
from search.search_controller import SearchController, can_edit_index


LOG = logging.getLogger(__name__)



def index(request):
  hue_collections = SearchController(request.user).get_search_collections()
  collection_id = request.GET.get('collection')

  if not hue_collections or not collection_id:
    return admin_collections(request, True)

  try:
    collection_doc = Document2.objects.get(id=collection_id)
    collection_doc.doc.get().can_read_or_exception(request.user)
    collection = Collection2(request.user, document=collection_doc)
  except Exception, e:
    raise PopupException(e, title=_("Dashboard does not exist or you don't have the permission to access it."))

  query = {'qs': [{'q': ''}], 'fqs': [], 'start': 0}

  if request.method == 'GET':
    if 'q' in request.GET:
      query['qs'][0]['q'] = request.GET.get('q')
    if 'qd' in request.GET:
      query['qd'] = request.GET.get('qd')


  return render('search.mako', request, {
    'collection': collection,
    'query': json.dumps(query),
    'initial': json.dumps({'collections': [], 'layout': [], 'is_latest': LATEST.get()}),
    'is_owner': collection_doc.doc.get().can_write(request.user),
    'can_edit_index': can_edit_index(request.user)
  })


def new_search(request):
  collections = SearchController(request.user).get_all_indexes()
  if not collections:
    return no_collections(request)

  collection = Collection2(user=request.user, name=collections[0])
  query = {'qs': [{'q': ''}], 'fqs': [], 'start': 0}

  return render('search.mako', request, {
    'collection': collection,
    'query': query,
    'initial': json.dumps({
         'collections': collections,
         'layout': [
              {"size":2,"rows":[{"widgets":[]}],"drops":["temp"],"klass":"card card-home card-column span2"},
              {"size":10,"rows":[{"widgets":[
                  {"size":12,"name":"Filter Bar","widgetType":"filter-widget", "id":"99923aef-b233-9420-96c6-15d48293532b",
                   "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"}]},
                                 {"widgets":[
                  {"size":12,"name":"Grid Results","widgetType":"resultset-widget", "id":"14023aef-b233-9420-96c6-15d48293532b",
                   "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"}]}],
                 "drops":["temp"],"klass":"card card-home card-column span10"},
         ],
         'is_latest': LATEST.get(),
     }),
    'is_owner': True,
    'can_edit_index': can_edit_index(request.user)
  })


def browse(request, name):
  collections = SearchController(request.user).get_all_indexes()
  if not collections:
    return no_collections(request)

  collection = Collection2(user=request.user, name=name)
  query = {'qs': [{'q': ''}], 'fqs': [], 'start': 0}

  return render('search.mako', request, {
    'collection': collection,
    'query': query,
    'initial': json.dumps({
         'autoLoad': True,
         'collections': collections,
         'layout': [
              {"size":12,"rows":[{"widgets":[
                  {"size":12,"name":"Grid Results","id":"52f07188-f30f-1296-2450-f77e02e1a5c0","widgetType":"resultset-widget",
                   "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"}]}],
              "drops":["temp"],"klass":"card card-home card-column span10"}
         ],
         'is_latest': LATEST.get()
     }),
     'is_owner': True,
     'can_edit_index': can_edit_index(request.user)
  })


@allow_viewer_only
def search(request):
  response = {}

  collection = json.loads(request.POST.get('collection', '{}'))
  query = json.loads(request.POST.get('query', '{}'))
  query['download'] = 'download' in request.POST

  if collection:
    try:
      response = SolrApi(SOLR_URL.get(), request.user).query(collection, query)
      response = augment_solr_response(response, collection, query)
    except RestException, e:
      try:
        response['error'] = json.loads(e.message)['error']['msg']
      except:
        LOG.exception('failed to parse json response')
        response['error'] = force_unicode(e)
    except Exception, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

      response['error'] = force_unicode(e)
  else:
    response['error'] = _('There is no collection to search.')

  if 'error' in response:
    augment_solr_exception(response, collection)

  return JsonResponse(response)


@allow_owner_only
def save(request):
  response = {'status': -1}

  collection = json.loads(request.POST.get('collection', '{}'))
  layout = json.loads(request.POST.get('layout', '{}'))

  collection['template']['extracode'] = escape(collection['template']['extracode'])

  if collection:
    if collection['id']:
      dashboard_doc = Document2.objects.get(id=collection['id'])
    else:
      dashboard_doc = Document2.objects.create(name=collection['name'], uuid=collection['uuid'], type='search-dashboard', owner=request.user, description=collection['label'])
      Document.objects.link(dashboard_doc, owner=request.user, name=collection['name'], description=collection['label'], extra='search-dashboard')

    dashboard_doc.update_data({
        'collection': collection,
        'layout': layout
    })
    dashboard_doc1 = dashboard_doc.doc.get()
    dashboard_doc.name = dashboard_doc1.name = collection['label']
    dashboard_doc.description = dashboard_doc1.description = collection['description']
    dashboard_doc.save()
    dashboard_doc1.save()

    response['status'] = 0
    response['id'] = dashboard_doc.id
    response['message'] = _('Page saved !')
  else:
    response['message'] = _('There is no collection to search.')

  return JsonResponse(response)


@allow_viewer_only
def download(request):
  try:
    file_format = 'csv' if 'csv' == request.POST.get('type') else 'xls' if 'xls' == request.POST.get('type') else 'json'
    response = search(request)

    if file_format == 'json':
      docs = json.loads(response.content)['response']['docs']
      resp = JsonResponse(docs, safe=False)
      resp['Content-Disposition'] = 'attachment; filename=%s.%s' % ('query_result', file_format)
      return resp
    else:
      collection = json.loads(request.POST.get('collection', '{}'))
      return export_download(json.loads(response.content), file_format, collection)
  except Exception, e:
    raise PopupException(_("Could not download search results: %s") % e)


def no_collections(request):
  return render('no_collections.mako', request, {})


def admin_collections(request, is_redirect=False):
  existing_hue_collections = SearchController(request.user).get_search_collections()

  if request.GET.get('format') == 'json':
    collections = []
    for collection in existing_hue_collections:
      massaged_collection = collection.to_dict()
      massaged_collection['isOwner'] = collection.doc.get().can_write(request.user)
      collections.append(massaged_collection)
    return JsonResponse(collections, safe=False)

  return render('admin_collections.mako', request, {
    'existing_hue_collections': existing_hue_collections,
    'is_redirect': is_redirect
  })


def admin_collection_delete(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  collections = json.loads(request.POST.get('collections'))
  searcher = SearchController(request.user)
  response = {
    'result': searcher.delete_collections([collection['id'] for collection in collections])
  }

  return JsonResponse(response)


def admin_collection_copy(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  collections = json.loads(request.POST.get('collections'))
  searcher = SearchController(request.user)
  response = {
    'result': searcher.copy_collections([collection['id'] for collection in collections])
  }

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

    dynamic_fields = SolrApi(SOLR_URL.get(), request.user).luke(name)

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


@allow_viewer_only
def get_document(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    collection = json.loads(request.POST.get('collection', '{}'))
    doc_id = request.POST.get('id')

    if doc_id:
      result['doc'] = SolrApi(SOLR_URL.get(), request.user).get(collection['name'], doc_id)
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

    result['stats'] = SolrApi(SOLR_URL.get(), request.user).stats(collection['name'], [field], query, facet)
    result['status'] = 0
    result['message'] = ''

  except Exception, e:
    result['message'] = force_unicode(e)
    if 'not currently supported' in result['message']:
      result['status'] = 1
      result['message'] = _('This field does not support stats')

  return JsonResponse(result)


@allow_viewer_only
def get_terms(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    collection = json.loads(request.POST.get('collection', '{}'))
    analysis = json.loads(request.POST.get('analysis', '{}'))

    field = analysis['name']
    properties = {
      'terms.limit': 25,
      'terms.prefix': analysis['terms']['prefix']
      # lower
      # limit
      # mincount
      # maxcount
    }

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
    'mincount': 0,
    'isDate': False,
    'aggregate': 'unique'
  }

  if widget_type in ('tree-widget', 'heatmap-widget', 'map-widget'):
    facet_type = 'pivot'
  elif widget_type == 'hit-widget':
    facet_type = 'function'
  else:
    solr_api = SolrApi(SOLR_URL.get(), user)
    range_properties = _new_range_facet(solr_api, collection, facet_field, widget_type)

    if range_properties:
      facet_type = 'range'
      properties.update(range_properties)
      properties['initial_gap'] = properties['gap']
      properties['initial_start'] = properties['start']
      properties['initial_end'] = properties['end']
    else:
      facet_type = 'field'

    if widget_type == 'bucket-widget' or widget_type == 'pie2-widget':
      facet_type = 'nested'
      properties['facets_form'] = {'field': '', 'mincount': 1, 'limit': 10, 'aggregate': 'count'}
      properties['facets'] = []
      if widget_type == 'pie2-widget':
        properties['scope'] = 'stack'
        properties['timelineChartType'] = 'bar'
      else:
        properties['scope'] = 'stack'
        properties['timelineChartType'] = 'bar'

  if widget_type in ('tree-widget', 'heatmap-widget', 'map-widget'):
    properties['mincount'] = 1
    properties['facets'] = []
    properties['stacked'] = True
    properties['facets_form'] = {'field': '', 'mincount': 1, 'limit': 5}

    if widget_type == 'map-widget':
      properties['scope'] = 'world'
      properties['limit'] = 100
    else:
      properties['scope'] = 'stack' if widget_type == 'heatmap-widget' else 'tree'

  return {
    'id': facet_id,
    'label': facet_label,
    'field': facet_field,
    'type': facet_type,
    'widgetType': widget_type,
    'properties': properties
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

    collection = Collection2(request.user, name=name)
    collection_json = collection.get_json(request.user)

    result['collection'] = json.loads(collection_json)
    result['status'] = 0

  except Exception, e:
    result['message'] = force_unicode(e)

  return JsonResponse(result)


def get_collections(request):
  result = {'status': -1, 'message': ''}

  try:
    show_all = json.loads(request.POST.get('show_all'))
    result['collection'] = SearchController(request.user).get_all_indexes(show_all=show_all)
    result['status'] = 0

  except Exception, e:
    if 'does not have privileges' in str(e):
      result['status'] = 0
      result['collection'] = [json.loads(request.POST.get('collection'))['name']]
    else:
      result['message'] = force_unicode(e)

  return JsonResponse(result)


def install_examples(request):
  result = {'status': -1, 'message': ''}

  if not request.user.is_superuser:
    return PopupException(_("You must be a superuser."))

  if request.method != 'POST':
    result['message'] = _('A POST request is required.')
  else:
    try:
      search_setup.Command().handle_noargs()
      indexer_setup.Command().handle_noargs()
      result['status'] = 0
    except Exception, e:
      LOG.exception(e)
      result['message'] = str(e)

  return JsonResponse(result)
