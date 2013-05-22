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

try:
  import json
except ImportError:
  import simplejson as json

import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.shortcuts import redirect

from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException

from search.api import SolrApi
from search.conf import SOLR_URL
from search.decorators import allow_admin_only
from search.forms import QueryForm, CollectionForm, HighlightingForm
from search.models import Collection, augment_solr_response
from search.search_controler import SearchController

LOG = logging.getLogger(__name__)


def index(request):
  hue_collections = Collection.objects.all()

  if not hue_collections:
    if request.user.is_superuser:
      return admin_collections_wizard(request)
    else:
      raise PopupException(_('No collections! If user message, if admin send to wizard.'))

  search_form = QueryForm(request.GET)
  response = {}
  error = {}
  solr_query = {}
  hue_collection = None

  if search_form.is_valid():
    collection = search_form.cleaned_data['collection']
    if request.GET.get('collection') is None:
      collection = request.COOKIES.get('hueSearchLastCollection', hue_collections[0].name)
    solr_query['collection'] = collection
    solr_query['q'] = search_form.cleaned_data['query']
    solr_query['fq'] = search_form.cleaned_data['fq']
    if search_form.cleaned_data['sort']:
      solr_query['sort'] = search_form.cleaned_data['sort']
    solr_query['rows'] = search_form.cleaned_data['rows'] or 15
    solr_query['start'] = search_form.cleaned_data['start'] or 0
    solr_query['facets'] = search_form.cleaned_data['facets'] or 1

    try:
      hue_collection = Collection.objects.get(name=collection)
      response = SolrApi(SOLR_URL.get()).query(solr_query, hue_collection)
    except Exception, e:
      error['message'] = unicode(str(e), "utf8")
  else:
    hue_collection = hue_collections[0]
    collection = hue_collections.name

  if hue_collection is not None:
    response = augment_solr_response(response, hue_collection.facets.get_data())

  if request.GET.get('format') == 'json':
    return HttpResponse(json.dumps(response), mimetype="application/json")

  return render('search.mako', request, {
    'search_form': search_form,
    'response': response,
    'error': error,
    'solr_query': solr_query,
    'hue_collection': hue_collection,
    'hue_collections': hue_collections,
    'current_collection': collection,
    'json': json,
  })


@allow_admin_only
def admin_collections(request):
  hue_collections = Collection.objects.all()

  return render('admin_collections.mako', request, {
    'hue_collections': hue_collections,
  })


@allow_admin_only
def admin_collections_wizard(request):
  searcher = SearchController()

  if request.method == 'POST':
    result = {'status': -1, 'message': 'Error'}
    try:
      searcher.add_new_collection(request.POST.copy())
      result['status'] = 0
      request.info(_('Collection added!'))
    except Exception, e:
      result['message'] = unicode(str(e), "utf8")
    return HttpResponse(json.dumps(result), mimetype="application/json")
  else:
    collections = searcher.get_new_collections()
    cores = searcher.get_new_cores()
    return render('admin_collections_wizard.mako', request, {
      'collections': collections,
      'cores': cores,
    })


@allow_admin_only
def admin(request):
  hue_collections = Collection.objects.all()

  return render('admin.mako', request, {
    'hue_collections': hue_collections,
  })


@allow_admin_only
def admin_collection_properties(request, collection):
  solr_collection = SolrApi(SOLR_URL.get()).collection(collection)
  hue_collection = Collection.objects.get(name=collection)

  if request.method == 'POST':
    collection_form = CollectionForm(request.POST, instance=hue_collection)
    if collection_form.is_valid():
      hue_collection = collection_form.save()
      return redirect(reverse('search:admin_collection_properties', kwargs={'collection': hue_collection.name}))
    else:
      request.error(_('Errors on the form: %s') % collection_form.errors)
  else:
    collection_form = CollectionForm(instance=hue_collection)

  return render('admin_collection_properties.mako', request, {
    'solr_collection': solr_collection,
    'hue_collection': hue_collection,
    'collection_form': collection_form,
  })


@allow_admin_only
def admin_collection_template(request, collection):
  solr_collection = SolrApi(SOLR_URL.get()).collection(collection)
  hue_collection = Collection.objects.get(name=collection)
  hue_collections = Collection.objects.all()

  if request.method == 'POST':
    hue_collection.result.update_from_post(request.POST)
    hue_collection.result.save()
    return HttpResponse(json.dumps({}), mimetype="application/json")

  solr_query = {}
  solr_query['collection'] = collection
  solr_query['q'] = ''
  solr_query['fq'] = ''
  solr_query['rows'] = 5
  solr_query['start'] = 0
  solr_query['facets'] = 0

  response = SolrApi(SOLR_URL.get()).query(solr_query, hue_collection)

  return render('admin_collection_template.mako', request, {
    'solr_collection': solr_collection,
    'hue_collection': hue_collection,
    'hue_collections': hue_collections,
    'sample_data': json.dumps(response["response"]["docs"]),
  })


@allow_admin_only
def admin_collection_facets(request, collection):
  solr_collection = SolrApi(SOLR_URL.get()).collection(collection)
  hue_collection = Collection.objects.get(name=collection)
  hue_collections = Collection.objects.all()

  if request.method == 'POST':
    hue_collection.facets.update_from_post(request.POST)
    hue_collection.facets.save()
    return HttpResponse(json.dumps({}), mimetype="application/json")

  return render('admin_collection_facets.mako', request, {
    'solr_collection': solr_collection,
    'hue_collection': hue_collection,
    'hue_collections': hue_collections,
  })


@allow_admin_only
def admin_collection_sorting(request, collection):
  solr_collection = SolrApi(SOLR_URL.get()).collection(collection)
  hue_collection = Collection.objects.get(name=collection)
  hue_collections = Collection.objects.all()

  if request.method == 'POST':
    hue_collection.sorting.update_from_post(request.POST)
    hue_collection.sorting.save()
    return HttpResponse(json.dumps({}), mimetype="application/json")

  return render('admin_collection_sorting.mako', request, {
    'solr_collection': solr_collection,
    'hue_collection': hue_collection,
    'hue_collections': hue_collections,
  })


@allow_admin_only
def admin_collection_highlighting(request, collection):
  solr_collection = SolrApi(SOLR_URL.get()).collection(collection)
  hue_collection = Collection.objects.get(name=collection)
  hue_collections = Collection.objects.all()

  if request.method == 'POST':
    hue_collection.result.update_from_post(request.POST)
    hue_collection.result.save()
    return HttpResponse(json.dumps({}), mimetype="application/json")

  return render('admin_collection_highlighting.mako', request, {
    'solr_collection': solr_collection,
    'hue_collection': hue_collection,
    'hue_collections': hue_collections,
  })


# Ajax below

@allow_admin_only
def admin_collection_solr_properties(request, collection):
  solr_collection = SolrApi(SOLR_URL.get()).collection(collection)
  hue_collection = Collection.objects.get(name=collection)
  hue_collections = Collection.objects.all()

  content = render('admin_collection_properties_solr_properties.mako', request, {
    'solr_collection': solr_collection,
    'hue_collection': hue_collection,
    'hue_collections': hue_collections,
  }, force_template=True).content

  return HttpResponse(json.dumps({'content': content}), mimetype="application/json")


@allow_admin_only
def admin_collection_schema(request, collection):
  solr_schema = SolrApi(SOLR_URL.get()).schema(collection)
  hue_collection = Collection.objects.get(name=collection)
  hue_collections = Collection.objects.all()

  content = render('admin_collection_properties_solr_schema.mako', request, {
    'solr_schema': solr_schema,
    'hue_collection': hue_collection,
    'hue_collections': hue_collections,
  }, force_template=True).content

  return HttpResponse(json.dumps({'content': content}), mimetype="application/json")


# TODO security
def query_suggest(request, collection, query=""):
  hue_collection = Collection.objects.get(name=collection)
  result = {'status': -1, 'message': 'Error'}

  solr_query = {}
  solr_query['collection'] = collection
  solr_query['q'] = query

  try:
    response = SolrApi(SOLR_URL.get()).suggest(solr_query, hue_collection)
    result['message'] = response
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")
