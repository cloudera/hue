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
import re

from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import ugettext as _

from desktop.conf import USE_NEW_EDITOR
from desktop.lib.django_util import JsonResponse, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document2, Document
from desktop.views import antixss

from search.conf import LATEST
from indexer.views import importer

from dashboard.dashboard_api import get_engine
from dashboard.decorators import allow_owner_only
from dashboard.conf import get_engines
from dashboard.controller import DashboardController, can_edit_index
from dashboard.models import Collection2


LOG = logging.getLogger(__name__)


DEFAULT_LAYOUT = [
     {"size":2,"rows":[{"widgets":[]}],"drops":["temp"],"klass":"card card-home card-column span2"},
     {"size":10,"rows":[{"widgets":[
         {"size":12,"name":"Filter Bar","widgetType":"filter-widget", "id":"99923aef-b233-9420-96c6-15d48293532b",
          "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"}]},
                        {"widgets":[
         {"size":12,"name":"Grid Results","widgetType":"resultset-widget", "id":"14023aef-b233-9420-96c6-15d48293532b",
          "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"}]}],
        "drops":["temp"],"klass":"card card-home card-column span10"},
]

REPORT_LAYOUT = [
  {u'klass': u'card card-home card-column span12', u'rows': [{"widgets":[]}], u'id': u'7e0c0a45-ae90-43a6-669a-2a852ef4a449', u'drops': [u'temp'], u'size': 12}
]

QUERY_BUILDER_LAYOUT = [
  {u'klass': u'card card-home card-column span12', u'rows': [
    {u'widgets': [
        {u'name': u'Filter Bar', u'widgetType': u'filter-widget', u'properties': {}, u'isLoading': False, u'offset': 0, u'klass': u'card card-widget span12', u'id': u'abe50df3-a5a0-408a-8122-019d779b4354', u'size': 12}],
     u'id': u'22532a0a-8e43-603a-daa9-77d5d233fd7f', u'columns': []},
        {u'widgets': [], u'id': u'ebb7fe4d-64c5-c660-bdc0-02a77ff8321e', u'columns': []},
        {u'widgets': [{u'name': u'Grid Results', u'widgetType': u'resultset-widget', u'properties': {}, u'isLoading': False, u'offset': 0, u'klass': u'card card-widget span12', u'id': u'14023aef-b233-9420-96c6-15d48293532b', u'size': 12}],
    u'id': u'2bfa8b4b-f7f3-1491-4de0-282130c6ab61', u'columns': []}
    ],
    u'id': u'7e0c0a45-ae90-43a6-669a-2a852ef4a449', u'drops': [u'temp'], u'size': 12
  }
]

TEXT_SEARCH_LAYOUT = [
     {"size":12,"rows":[{"widgets":[
         {"size":12,"name":"Filter Bar","widgetType":"filter-widget", "id":"99923aef-b233-9420-96c6-15d48293532b",
          "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"}]},
                        {"widgets":[
         {"size":12,"name":"HTML Results","widgetType":"html-resultset-widget", "id":"14023aef-b233-9420-96c6-15d48293532b",
          "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"}]}],
        "drops":["temp"],"klass":"card card-home card-column span12"},
]


def index(request, is_mobile=False):
  engine = request.GET.get('engine', 'solr')
  cluster = request.POST.get('cluster','""')
  collection_id = request.GET.get('collection')

  collections = get_engine(request.user, engine, cluster=cluster).datasets() if engine != 'report' else ['default']

  if not collections:
    if engine == 'solr':
      return no_collections(request)
    else:
      return importer(request)

  try:
    collection_doc = Document2.objects.get(id=collection_id)
    if USE_NEW_EDITOR.get():
      collection_doc.can_read_or_exception(request.user)
    else:
      collection_doc.doc.get().can_read_or_exception(request.user)
    collection = Collection2(request.user, document=collection_doc)
  except Exception, e:
    raise PopupException(e, title=_("Dashboard does not exist or you don't have the permission to access it."))

  query = {'qs': [{'q': ''}], 'fqs': [], 'start': 0}

  if request.method == 'GET':
    if 'q' in request.GET:
      query['qs'][0]['q'] = antixss(request.GET.get('q', ''))
    if 'qd' in request.GET:
      query['qd'] = antixss(request.GET.get('qd', ''))

  template = 'search.mako'
  if is_mobile:
    template = 'search_m.mako'
  engine = collection.data['collection'].get('engine', 'solr')

  return render(template, request, {
    'collection': collection,
    'query': json.dumps(query),
    'initial': json.dumps({
        'collections': collections,
        'layout': DEFAULT_LAYOUT,
        'qb_layout': QUERY_BUILDER_LAYOUT,
        'text_search_layout': TEXT_SEARCH_LAYOUT,
        'is_latest': _get_latest(),
        'engines': get_engines(request.user)
    }),
    'is_owner': collection_doc.can_write(request.user) if USE_NEW_EDITOR.get() else collection_doc.doc.get().can_write(request.user),
    'can_edit_index': can_edit_index(request.user),
    'is_embeddable': request.GET.get('is_embeddable', False),
    'mobile': is_mobile,
    'is_report': collection.data['collection'].get('engine') == 'report'
  })

def index_m(request):
  return index(request, True)

def new_search(request):
  engine = request.GET.get('engine', 'solr')
  cluster = request.POST.get('cluster','""')

  collections = get_engine(request.user, engine, cluster=cluster).datasets() if engine != 'report' else ['default']

  if not collections:
    if engine == 'solr':
      return no_collections(request)
    else:
      return importer(request)

  collection = Collection2(user=request.user, name=collections[0], engine=engine)
  query = {'qs': [{'q': ''}], 'fqs': [], 'start': 0}
  layout = DEFAULT_LAYOUT if engine != 'report' else REPORT_LAYOUT

  if request.GET.get('format', 'plain') == 'json':
    return JsonResponse({
      'collection': collection.get_props(request.user),
      'query': query,
      'initial': {
          'collections': collections,
          'layout': layout,
          'qb_layout': QUERY_BUILDER_LAYOUT,
          'text_search_layout': TEXT_SEARCH_LAYOUT,
          'is_latest': _get_latest(),
          'engines': get_engines(request.user)
       }
     })
  else:
    return render('search.mako', request, {
      'collection': collection,
      'query': query,
      'initial': json.dumps({
          'collections': collections,
          'layout': layout,
          'qb_layout': QUERY_BUILDER_LAYOUT,
          'text_search_layout': TEXT_SEARCH_LAYOUT,
          'is_latest': _get_latest(),
          'engines': get_engines(request.user)
       }),
      'is_owner': True,
      'is_embeddable': request.GET.get('is_embeddable', False),
      'can_edit_index': can_edit_index(request.user),
      'is_report': engine == 'report'
    })

def browse(request, name, is_mobile=False):
  engine = request.GET.get('engine', 'solr')
  source = request.GET.get('source', 'data')

  if engine == 'solr':
    name = re.sub('^default\.', '', name)

  collections = get_engine(request.user, engine, source=source).datasets()
  if not collections and engine == 'solr':
    return no_collections(request)

  collection = Collection2(user=request.user, name=name, engine=engine, source=source)
  query = {'qs': [{'q': ''}], 'fqs': [], 'start': 0}

  template = 'search.mako'
  if is_mobile:
    template = 'search_m.mako'

  return render(template, request, {
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
      'qb_layout': QUERY_BUILDER_LAYOUT,
      'text_search_layout': TEXT_SEARCH_LAYOUT,
      'is_latest': _get_latest(),
      'engines': get_engines(request.user)
    }),
    'is_owner': True,
    'is_embeddable': request.GET.get('is_embeddable', False),
    'can_edit_index': can_edit_index(request.user),
    'mobile': is_mobile
  })


def browse_m(request, name):
  return browse(request, name, True)


@allow_owner_only
def save(request):
  response = {'status': -1}

  collection = json.loads(request.POST.get('collection', '{}'))
  layout = json.loads(request.POST.get('layout', '{}'))
  gridItems = json.loads(request.POST.get('gridItems', '{}'))

  collection['template']['extracode'] = escape(collection['template']['extracode'])

  if collection:
    if collection['id']:
      dashboard_doc = Document2.objects.get(id=collection['id'])
    else:
      dashboard_doc = Document2.objects.create(name=collection['name'], uuid=collection['uuid'], type='search-dashboard', owner=request.user, description=collection['label'])
      Document.objects.link(dashboard_doc, owner=request.user, name=collection['name'], description=collection['label'], extra='search-dashboard')

    dashboard_doc.update_data({
        'collection': collection,
        'layout': layout,
        'gridItems': gridItems
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


def no_collections(request):
  return render('no_collections.mako', request, {'is_embeddable': request.GET.get('is_embeddable', False)})


def admin_collections(request, is_redirect=False, is_mobile=False):
  existing_hue_collections = DashboardController(request.user).get_search_collections()

  if request.GET.get('format') == 'json':
    collections = []
    for collection in existing_hue_collections:
      massaged_collection = collection.to_dict()
      if request.GET.get('is_mobile'):
        massaged_collection['absoluteUrl'] = reverse('search:index_m') + '?collection=%s' % collection.id
      massaged_collection['isOwner'] = collection.doc.get().can_write(request.user)
      collections.append(massaged_collection)
    return JsonResponse(collections, safe=False)

  template = 'admin_collections.mako'
  if is_mobile:
    template = 'admin_collections_m.mako'

  return render(template, request, {
    'is_embeddable': request.GET.get('is_embeddable', False),
    'existing_hue_collections': existing_hue_collections,
    'is_redirect': is_redirect
  })


def admin_collection_delete(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  collections = json.loads(request.POST.get('collections'))
  searcher = DashboardController(request.user)
  response = {
    'result': searcher.delete_collections([collection['id'] for collection in collections])
  }

  return JsonResponse(response)


def admin_collection_copy(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  collections = json.loads(request.POST.get('collections'))
  searcher = DashboardController(request.user)
  response = {
    'result': searcher.copy_collections([collection['id'] for collection in collections])
  }

  return JsonResponse(response)


def _get_latest():
  return hasattr(LATEST, 'get') and LATEST.get() or True
