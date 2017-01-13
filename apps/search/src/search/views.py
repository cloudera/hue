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

from desktop.conf import USE_NEW_EDITOR
from desktop.lib.django_util import JsonResponse, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document2, Document

from indexer.management.commands import indexer_setup

from search.conf import LATEST
from search.data_export import download as export_download
from search.decorators import allow_owner_only, allow_viewer_only
from search.management.commands import search_setup
from search.models import Collection2
from search.search_controller import SearchController, can_edit_index

from django.core.urlresolvers import reverse


LOG = logging.getLogger(__name__)


def index(request, is_mobile=False, is_embeddable=False):
  hue_collections = SearchController(request.user).get_search_collections()
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
  if is_embeddable:
    template = 'search_embeddable.mako'

  return render(template, request, {
    'collection': collection,
    'query': json.dumps(query),
    'initial': json.dumps({'collections': [], 'layout': [], 'is_latest': LATEST.get()}),
    'is_owner': collection_doc.doc.get().can_write(request.user),
    'can_edit_index': can_edit_index(request.user),
    'mobile': is_mobile
  })

def index_m(request):
  return index(request, True)

def index_embeddable(request):
  return index(request, False, True)

def new_search(request, is_embeddable=False):
  collections = SearchController(request.user).get_all_indexes()
  if not collections:
    return no_collections(request)

  collection = Collection2(user=request.user, name=collections[0])
  query = {'qs': [{'q': ''}], 'fqs': [], 'start': 0}

  template = 'search.mako'
  if is_embeddable:
    template = 'search_embeddable.mako'

  return render(template, request, {
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

def new_search_embeddable(request):
  return new_search(request, True)

def browse(request, name, is_mobile=False):
  collections = SearchController(request.user).get_all_indexes()
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
      'is_latest': LATEST.get()
    }),
    'is_owner': True,
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


def admin_collections(request, is_redirect=False, is_mobile=False):
  existing_hue_collections = SearchController(request.user).get_search_collections()

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
