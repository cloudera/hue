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

from django.utils.html import escape
from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse
from desktop.conf import USE_NEW_EDITOR
from desktop.lib.django_util import JsonResponse, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document2, Document

from search.conf import LATEST

from dashboard.dashboard_api import get_engine
from dashboard.decorators import allow_owner_only
from dashboard.models import Collection2
from dashboard.conf import get_engines
from dashboard.controller import DashboardController, can_edit_index


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


def index(request, is_mobile=False):
  hue_collections = DashboardController(request.user).get_search_collections()
  collection_id = request.GET.get('collection')

  if not hue_collections or not collection_id:
    return admin_collections(request, True, is_mobile)

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
      query['qs'][0]['q'] = request.GET.get('q')
    if 'qd' in request.GET:
      query['qd'] = request.GET.get('qd')

  template = 'search.mako'
  if is_mobile:
    template = 'search_m.mako'

  return render(template, request, {
    'collection': collection,
    'query': json.dumps(query),
    'initial': json.dumps({
        'collections': [],
        'layout': DEFAULT_LAYOUT,
        'is_latest': LATEST.get(),
        'engines': get_engines(request.user)
    }),
    'is_owner': collection_doc.doc.get().can_write(request.user),
    'can_edit_index': can_edit_index(request.user),
    'is_embeddable': request.GET.get('is_embeddable', False),
    'mobile': is_mobile,
  })

def index_m(request):
  return index(request, True)

def new_search(request):
  engine = request.GET.get('engine', 'solr')
  collections = get_engine(request.user, engine).datasets()
  if not collections:
    return no_collections(request)

  collection = Collection2(user=request.user, name=collections[0], engine=engine)
  query = {'qs': [{'q': ''}], 'fqs': [], 'start': 0}

  if request.GET.get('format', 'plain') == 'json':
    return JsonResponse({
      'collection': collection.get_props(request.user),
      'query': query,
      'initial': {
          'collections': collections,
          'layout': DEFAULT_LAYOUT,
          'is_latest': LATEST.get(),
          'engines': get_engines(request.user)
       }
     })
  else:
    return render('search.mako', request, {
      'collection': collection,
      'query': query,
      'initial': json.dumps({
          'collections': collections,
          'layout': DEFAULT_LAYOUT,
          'is_latest': LATEST.get(),
          'engines': get_engines(request.user)
       }),
      'is_owner': True,
      'is_embeddable': request.GET.get('is_embeddable', False),
      'can_edit_index': can_edit_index(request.user)
    })

def browse(request, name, is_mobile=False):
  engine = request.GET.get('engine', 'solr')
  collections = get_engine(request.user, engine).datasets()
  if not collections:
    return no_collections(request)

  collection = Collection2(user=request.user, name=name)
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
      'is_latest': LATEST.get(),
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
