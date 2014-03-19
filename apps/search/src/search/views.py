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
import math

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from django.shortcuts import redirect

from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException

from search.api import SolrApi
from search.conf import SOLR_URL
from search.data_export import download as export_download
from search.decorators import allow_admin_only
from search.forms import QueryForm, CollectionForm
from search.management.commands import search_setup
from search.models import Collection, augment_solr_response, augment_solr_response2
from search.search_controller import SearchController

from django.utils.encoding import force_unicode
from desktop.lib.rest.http_client import RestException


LOG = logging.getLogger(__name__)


def initial_collection(request, hue_collections):
  return hue_collections[0].id


def index(request):
  hue_collections = SearchController(request.user).get_search_collections()

  if not hue_collections:
    if request.user.is_superuser:
      return admin_collections(request, True)
    else:
      return no_collections(request)

  init_collection = initial_collection(request, hue_collections)

  search_form = QueryForm(request.GET, initial_collection=init_collection)
  response = {}
  error = {}
  solr_query = {}

  if search_form.is_valid():
    try:
      collection_id = search_form.cleaned_data['collection']
      hue_collection = Collection.objects.get(id=collection_id)

      solr_query = search_form.solr_query_dict
      response = SolrApi(SOLR_URL.get(), request.user).query(solr_query, hue_collection)

      solr_query['total_pages'] = int(math.ceil((float(response['response']['numFound']) / float(solr_query['rows']))))
      solr_query['search_time'] = response['responseHeader']['QTime']
    except Exception, e:
      error['title'] = force_unicode(e.title) if hasattr(e, 'title') else ''
      error['message'] = force_unicode(str(e))
  else:
    error['message'] = _('There is no collection to search.')

  if hue_collection is not None:
    response = augment_solr_response(response, hue_collection.facets.get_data(), solr_query)

  if request.GET.get('format') == 'json':
    return HttpResponse(json.dumps(response), mimetype="application/json")

  return render('search.mako', request, {
    'search_form': search_form,
    'response': response,
    'error': error,
    'solr_query': solr_query,
    'hue_collection': hue_collection,
    'current_collection': collection_id,
    'json': json,
  })

def dashboard(request):
  return render('dashboard.mako', request, {})


def index2(request):
  hue_collections = SearchController(request.user).get_search_collections()

  if not hue_collections:
    if request.user.is_superuser:
      return admin_collections(request, True)
    else:
      return no_collections(request)

  init_collection = initial_collection(request, hue_collections)

  search_form = QueryForm(request.POST, initial_collection=init_collection)
  response = {}
  solr_query = {}

  if search_form.is_valid():    
    try:
      collection_id = search_form.cleaned_data['collection']
      hue_collection = Collection.objects.get(id=collection_id)

      solr_query = search_form.solr_query_dict
      print request.POST
      # if selected facets --> add fq fields + exlcude tag y/n
      fcets = json.loads(request.POST.get('facets', '[]'))
      solr_query['fq'] = json.loads(request.POST.get('fq', '{}'))
      solr_query['q'] = json.loads(request.POST.get('q', '""'))
      template = json.loads(request.POST.get('template', '{}'))
      #solr_query['fl'] = template.get('fields', []) # if we do this, need to parse the template and fill up the fields list
      print solr_query
      print fcets, '===='
      response = SolrApi(SOLR_URL.get(), request.user).query2(solr_query, fcets)

      if hue_collection is not None:
        response = augment_solr_response2(response, fcets, solr_query)
      solr_query['total_pages'] = int(math.ceil((float(response['response']['numFound']) / float(solr_query['rows']))))
      solr_query['search_time'] = response['responseHeader']['QTime']
    except RestException, e:
      try:
        response['error'] = json.loads(e.message)['error']['msg']
      except:
        response['error'] = force_unicode(str(e))
    except Exception, e:
      raise PopupException(e, title=_('Error while accessing Solr'))
      
      response['error'] = force_unicode(str(e))
  else:
    response['error'] = _('There is no collection to search.')

  if 'error' in response:
    response.update(
    {
      "facet_counts": {   
      },
      "highlighting": {
      },
      "normalized_facets": [
        {
          "field": "user_location",
          "counts": [],
          "type": "field",
          "label": "Location"
        },
        {
          "field": "not_there",
          "counts": [],
          "type": "field",
          "label": "Bad facet"
        },
      ],
      "responseHeader": {
        "status": -1,
        "QTime": 0,
        "params": {
        }
      },
      "response": {
        "start": 0,
        "numFound": 0,
        "docs": [
        ]
      }
    }) 

  if request.GET.get('format') == 'json':
    return HttpResponse(json.dumps(response), mimetype="application/json")

  return render('search2.mako', request, {
    'search_form': search_form,
    'response': json.dumps(response),
    'solr_query': solr_query,
    'hue_collection': hue_collection,
    'current_collection': collection_id,
  })

def download(request, format):
  hue_collections = SearchController(request.user).get_search_collections()

  if not hue_collections:
    raise PopupException(_("No collection to download."))

  init_collection = initial_collection(request, hue_collections)

  search_form = QueryForm(request.GET, initial_collection=init_collection)

  if search_form.is_valid():
    try:
      collection_id = search_form.cleaned_data['collection']
      hue_collection = Collection.objects.get(id=collection_id)

      solr_query = search_form.solr_query_dict
      response = SolrApi(SOLR_URL.get(), request.user).query(solr_query, hue_collection)

      LOG.debug('Download results for query %s' % smart_str(solr_query))

      return export_download(response, format)
    except Exception, e:
      raise PopupException(_("Could not download search results: %s") % e)
  else:
    raise PopupException(_("Could not download search results: %s") % search_form.errors)


def no_collections(request):
  return render('no_collections.mako', request, {})


@allow_admin_only
def admin_collections(request, is_redirect=False):
  existing_hue_collections = Collection.objects.all()

  if request.GET.get('format') == 'json':
    collections = []
    for collection in existing_hue_collections:
      massaged_collection = {
        'id': collection.id,
        'name': collection.name,
        'label': collection.label,
        'isCoreOnly': collection.is_core_only,
        'absoluteUrl': collection.get_absolute_url()
      }
      collections.append(massaged_collection)
    return HttpResponse(json.dumps(collections), mimetype="application/json")

  return render('admin_collections.mako', request, {
    'existing_hue_collections': existing_hue_collections,
    'is_redirect': is_redirect
  })


@allow_admin_only
def admin_collections_import(request):
  if request.method == 'POST':
    searcher = SearchController(request.user)
    imported = []
    not_imported = []
    status = -1
    message = ""
    importables = json.loads(request.POST["selected"])
    for imp in importables:
      try:
        searcher.add_new_collection(imp)
        imported.append(imp['name'])
      except Exception, e:
        not_imported.append(imp['name'] + ": " + unicode(str(e), "utf8"))

    if len(imported) == len(importables):
      status = 0;
      message = _('Collection(s) or core(s) imported successfully!')
    elif len(not_imported) == len(importables):
      status = 2;
      message = _('There was an error importing the collection(s) or core(s)')
    else:
      status = 1;
      message = _('Collection(s) or core(s) partially imported')

    result = {
      'status': status,
      'message': message,
      'imported': imported,
      'notImported': not_imported
    }

    return HttpResponse(json.dumps(result), mimetype="application/json")
  else:
    if request.GET.get('format') == 'json':
      searcher = SearchController(request.user)
      new_solr_collections = searcher.get_new_collections()
      massaged_collections = []
      for coll in new_solr_collections:
        massaged_collections.append({
          'type': 'collection',
          'name': coll
        })
      new_solr_cores = searcher.get_new_cores()
      massaged_cores = []
      for core in new_solr_cores:
        massaged_cores.append({
          'type': 'core',
          'name': core
        })
      response = {
        'newSolrCollections': list(massaged_collections),
        'newSolrCores': list(massaged_cores)
      }
      return HttpResponse(json.dumps(response), mimetype="application/json")
    else:
      return admin_collections(request, True)

@allow_admin_only
def admin_collection_delete(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  id = request.POST.get('id')
  searcher = SearchController(request.user)
  response = {
    'id': searcher.delete_collection(id)
  }

  return HttpResponse(json.dumps(response), mimetype="application/json")


@allow_admin_only
def admin_collection_copy(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  id = request.POST.get('id')
  searcher = SearchController(request.user)
  response = {
    'id': searcher.copy_collection(id)
  }

  return HttpResponse(json.dumps(response), mimetype="application/json")


@allow_admin_only
def admin_collection_properties(request, collection_id):
  hue_collection = Collection.objects.get(id=collection_id)
  solr_collection = SolrApi(SOLR_URL.get(), request.user).collection_or_core(hue_collection)

  if request.method == 'POST':
    collection_form = CollectionForm(request.POST, instance=hue_collection, user=request.user)
    if collection_form.is_valid(): # Check for autocomplete in data?
      searcher = SearchController(request.user)
      hue_collection = collection_form.save(commit=False)
      hue_collection.is_core_only = not searcher.is_collection(hue_collection.name)
      hue_collection.autocomplete = json.loads(request.POST.get('autocomplete'))
      hue_collection.save()
      return redirect(reverse('search:admin_collection_properties', kwargs={'collection_id': hue_collection.id}))
    else:
      request.error(_('Errors on the form: %s.') % collection_form.errors)
  else:
    collection_form = CollectionForm(instance=hue_collection)

  return render('admin_collection_properties.mako', request, {
    'solr_collection': solr_collection,
    'hue_collection': hue_collection,
    'collection_form': collection_form,
    'collection_properties': json.dumps(hue_collection.properties_dict)
  })


@allow_admin_only
def admin_collection_template(request, collection_id):
  hue_collection = Collection.objects.get(id=collection_id)
  solr_collection = SolrApi(SOLR_URL.get(), request.user).collection_or_core(hue_collection)
  sample_data = {}

  if request.method == 'POST':
    hue_collection.result.update_from_post(request.POST)
    hue_collection.result.save()
    return HttpResponse(json.dumps({}), mimetype="application/json")

  solr_query = {}
  solr_query['collection'] = hue_collection.name
  solr_query['q'] = ''
  solr_query['fq'] = ''
  solr_query['rows'] = 5
  solr_query['start'] = 0
  solr_query['facets'] = 0

  try:
    response = SolrApi(SOLR_URL.get(), request.user).query(solr_query, hue_collection)
    sample_data = json.dumps(response["response"]["docs"])
  except PopupException, e:
    message = e
    try:
      message = json.loads(e.message.message)['error']['msg'] # Try to get the core error
    except:
      pass
    request.error(_('No preview available, some facets are invalid: %s') % message)
    LOG.exception(e)

  return render('admin_collection_template.mako', request, {
    'solr_collection': solr_collection,
    'hue_collection': hue_collection,
    'sample_data': sample_data,
  })


@allow_admin_only
def admin_collection_facets(request, collection_id):
  hue_collection = Collection.objects.get(id=collection_id)
  solr_collection = SolrApi(SOLR_URL.get(), request.user).collection_or_core(hue_collection)

  if request.method == 'POST':
    hue_collection.facets.update_from_post(request.POST)
    hue_collection.facets.save()
    return HttpResponse(json.dumps({}), mimetype="application/json")

  return render('admin_collection_facets.mako', request, {
    'solr_collection': solr_collection,
    'hue_collection': hue_collection,
  })


@allow_admin_only
def admin_collection_sorting(request, collection_id):
  hue_collection = Collection.objects.get(id=collection_id)
  solr_collection = SolrApi(SOLR_URL.get(), request.user).collection_or_core(hue_collection)

  if request.method == 'POST':
    hue_collection.sorting.update_from_post(request.POST)
    hue_collection.sorting.save()
    return HttpResponse(json.dumps({}), mimetype="application/json")

  return render('admin_collection_sorting.mako', request, {
    'solr_collection': solr_collection,
    'hue_collection': hue_collection,
  })


@allow_admin_only
def admin_collection_highlighting(request, collection_id):
  hue_collection = Collection.objects.get(id=collection_id)
  solr_collection = SolrApi(SOLR_URL.get(), request.user).collection_or_core(hue_collection)

  if request.method == 'POST':
    hue_collection.result.update_from_post(request.POST)
    hue_collection.result.save()
    return HttpResponse(json.dumps({}), mimetype="application/json")

  return render('admin_collection_highlighting.mako', request, {
    'solr_collection': solr_collection,
    'hue_collection': hue_collection,
  })


# Ajax below

@allow_admin_only
def admin_collection_solr_properties(request, collection_id):
  hue_collection = Collection.objects.get(id=collection_id)
  solr_collection = SolrApi(SOLR_URL.get(), request.user).collection_or_core(hue_collection)

  content = render('admin_collection_properties_solr_properties.mako', request, {
    'solr_collection': solr_collection,
    'hue_collection': hue_collection,
  }, force_template=True).content

  return HttpResponse(json.dumps({'content': content}), mimetype="application/json")


@allow_admin_only
def admin_collection_schema(request, collection_id):
  hue_collection = Collection.objects.get(id=collection_id)
  solr_schema = SolrApi(SOLR_URL.get(), request.user).schema(hue_collection.name)

  content = {
    'solr_schema': solr_schema.decode('utf-8')
  }
  return HttpResponse(json.dumps(content), mimetype="application/json")


# TODO security
def query_suggest(request, collection_id, query=""):
  hue_collection = Collection.objects.get(id=collection_id)
  result = {'status': -1, 'message': 'Error'}

  solr_query = {}
  solr_query['collection'] = hue_collection.name
  solr_query['q'] = query

  try:
    response = SolrApi(SOLR_URL.get(), request.user).suggest(solr_query, hue_collection)
    result['message'] = response
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


def install_examples(request):
  result = {'status': -1, 'message': ''}

  if request.method != 'POST':
    result['message'] = _('A POST request is required.')
  else:
    try:
      search_setup.Command().handle_noargs()
      result['status'] = 0
    except Exception, e:
      LOG.exception(e)
      result['message'] = str(e)

  return HttpResponse(json.dumps(result), mimetype="application/json")

MOCK = """{
  "facet_counts": {
    "facet_ranges": {
      "created_at": {
        "start": "2014-02-18T12:00:00Z",
        "counts": [
          "2014-02-25T16:05:00Z",
          97,
          "2014-02-25T16:10:00Z",
          92,
          "2014-02-25T16:15:00Z",
          115,
          "2014-02-25T16:20:00Z",
          83,
          "2014-02-25T16:25:00Z",
          108,
          "2014-02-25T16:30:00Z",
          120,
          "2014-02-25T16:35:00Z",
          98,
          "2014-02-25T16:40:00Z",
          101,
          "2014-02-25T16:45:00Z",
          110,
          "2014-02-25T16:50:00Z",
          100,
          "2014-02-25T16:55:00Z",
          96,
          "2014-02-25T17:00:00Z",
          119,
          "2014-02-25T17:05:00Z",
          125,
          "2014-02-25T17:10:00Z",
          115,
          "2014-02-25T17:15:00Z",
          116,
          "2014-02-25T17:20:00Z",
          107,
          "2014-02-25T17:25:00Z",
          139,
          "2014-02-25T17:30:00Z",
          131,
          "2014-02-25T17:35:00Z",
          123,
          "2014-02-25T17:40:00Z",
          125,
          "2014-02-25T17:45:00Z",
          125,
          "2014-02-25T17:50:00Z",
          102,
          "2014-02-25T17:55:00Z",
          149,
          "2014-02-25T18:00:00Z",
          130,
          "2014-02-25T18:05:00Z",
          123,
          "2014-02-25T18:10:00Z",
          145,
          "2014-02-25T18:15:00Z",
          108,
          "2014-02-25T18:20:00Z",
          133,
          "2014-02-25T18:25:00Z",
          132,
          "2014-02-25T18:30:00Z",
          162,
          "2014-02-25T18:35:00Z",
          142,
          "2014-02-25T18:40:00Z",
          139,
          "2014-02-25T18:45:00Z",
          156,
          "2014-02-25T18:50:00Z",
          132,
          "2014-02-25T18:55:00Z",
          159,
          "2014-02-25T19:00:00Z",
          157,
          "2014-02-25T19:05:00Z",
          136,
          "2014-02-25T19:10:00Z",
          137,
          "2014-02-25T19:15:00Z",
          164,
          "2014-02-25T19:20:00Z",
          132,
          "2014-02-25T19:25:00Z",
          154,
          "2014-02-25T19:30:00Z",
          187,
          "2014-02-25T19:35:00Z",
          161,
          "2014-02-25T19:40:00Z",
          159,
          "2014-02-25T19:45:00Z",
          144,
          "2014-02-25T19:50:00Z",
          157,
          "2014-02-25T19:55:00Z",
          146,
          "2014-02-25T20:00:00Z",
          193,
          "2014-02-25T20:05:00Z",
          175,
          "2014-02-25T20:10:00Z",
          189,
          "2014-02-25T20:15:00Z",
          182,
          "2014-02-25T20:20:00Z",
          168,
          "2014-02-25T20:25:00Z",
          171,
          "2014-02-25T20:30:00Z",
          175,
          "2014-02-25T20:35:00Z",
          169,
          "2014-02-25T20:40:00Z",
          182,
          "2014-02-25T20:45:00Z",
          163,
          "2014-02-25T20:50:00Z",
          186,
          "2014-02-25T20:55:00Z",
          184,
          "2014-02-25T21:00:00Z",
          216,
          "2014-02-25T21:05:00Z",
          202,
          "2014-02-25T21:10:00Z",
          176,
          "2014-02-25T21:15:00Z",
          196,
          "2014-02-25T21:20:00Z",
          192,
          "2014-02-25T21:25:00Z",
          189,
          "2014-02-25T21:30:00Z",
          190,
          "2014-02-25T21:35:00Z",
          187,
          "2014-02-25T21:40:00Z",
          215,
          "2014-02-25T21:45:00Z",
          197,
          "2014-02-25T21:50:00Z",
          174,
          "2014-02-25T21:55:00Z",
          179,
          "2014-02-25T22:00:00Z",
          216,
          "2014-02-25T22:05:00Z",
          185,
          "2014-02-25T22:10:00Z",
          178,
          "2014-02-25T22:15:00Z",
          219,
          "2014-02-25T22:20:00Z",
          190,
          "2014-02-25T22:25:00Z",
          190,
          "2014-02-25T22:30:00Z",
          196,
          "2014-02-25T22:35:00Z",
          176,
          "2014-02-25T22:40:00Z",
          215,
          "2014-02-25T22:45:00Z",
          212,
          "2014-02-25T22:50:00Z",
          200,
          "2014-02-25T22:55:00Z",
          216,
          "2014-02-25T23:00:00Z",
          225,
          "2014-02-25T23:05:00Z",
          186,
          "2014-02-25T23:10:00Z",
          181,
          "2014-02-25T23:15:00Z",
          213,
          "2014-02-25T23:20:00Z",
          214,
          "2014-02-25T23:25:00Z",
          189,
          "2014-02-25T23:30:00Z",
          188,
          "2014-02-25T23:35:00Z",
          174,
          "2014-02-25T23:40:00Z",
          199,
          "2014-02-25T23:45:00Z",
          165,
          "2014-02-25T23:50:00Z",
          198,
          "2014-02-25T23:55:00Z",
          158,
          "2014-02-26T00:00:00Z",
          193,
          "2014-02-26T00:05:00Z",
          168,
          "2014-02-26T00:10:00Z",
          186,
          "2014-02-26T00:15:00Z",
          182,
          "2014-02-26T00:20:00Z",
          174,
          "2014-02-26T00:25:00Z",
          185,
          "2014-02-26T00:30:00Z",
          184,
          "2014-02-26T00:35:00Z",
          157,
          "2014-02-26T00:40:00Z",
          161,
          "2014-02-26T00:45:00Z",
          158,
          "2014-02-26T00:50:00Z",
          175,
          "2014-02-26T00:55:00Z",
          151,
          "2014-02-26T01:00:00Z",
          203,
          "2014-02-26T01:05:00Z",
          154,
          "2014-02-26T01:10:00Z",
          158,
          "2014-02-26T01:15:00Z",
          153,
          "2014-02-26T01:20:00Z",
          141,
          "2014-02-26T01:25:00Z",
          150,
          "2014-02-26T01:30:00Z",
          165,
          "2014-02-26T01:35:00Z",
          152,
          "2014-02-26T01:40:00Z",
          161,
          "2014-02-26T01:45:00Z",
          178,
          "2014-02-26T01:50:00Z",
          145,
          "2014-02-26T01:55:00Z",
          161,
          "2014-02-26T02:00:00Z",
          171,
          "2014-02-26T02:05:00Z",
          151,
          "2014-02-26T02:10:00Z",
          141,
          "2014-02-26T02:15:00Z",
          145,
          "2014-02-26T02:20:00Z",
          149,
          "2014-02-26T02:25:00Z",
          131,
          "2014-02-26T02:30:00Z",
          134,
          "2014-02-26T02:35:00Z",
          142,
          "2014-02-26T02:40:00Z",
          133,
          "2014-02-26T02:45:00Z",
          157,
          "2014-02-26T02:50:00Z",
          154,
          "2014-02-26T02:55:00Z",
          146,
          "2014-02-26T03:00:00Z",
          124,
          "2014-02-26T03:05:00Z",
          147,
          "2014-02-26T03:10:00Z",
          142,
          "2014-02-26T03:15:00Z",
          137,
          "2014-02-26T03:20:00Z",
          139,
          "2014-02-26T03:25:00Z",
          156,
          "2014-02-26T03:30:00Z",
          18,
          "2014-02-26T04:10:00Z",
          15,
          "2014-02-26T04:15:00Z",
          65,
          "2014-02-26T04:20:00Z",
          53,
          "2014-02-26T04:25:00Z",
          66,
          "2014-02-26T04:30:00Z",
          65,
          "2014-02-26T04:35:00Z",
          57,
          "2014-02-26T04:40:00Z",
          61
        ],
        "end": "2014-02-28T12:00:00Z",
        "gap": "+5MINUTES"
      },
      "user_followers_count": {
        "start": 0,
        "counts": [
          "0",
          4585,
          "100",
          3725,
          "200",
          2719,
          "300",
          1881,
          "400",
          1346,
          "500",
          966,
          "600",
          709,
          "700",
          668,
          "800",
          448,
          "900",
          383
        ],
        "end": 1000,
        "gap": 100
      },
      "user_statuses_count": {
        "start": 0,
        "counts": [
          "0",
          3981,
          "1000",
          2223,
          "2000",
          1701,
          "3000",
          1270,
          "4000",
          1051,
          "5000",
          922,
          "6000",
          784,
          "7000",
          770,
          "8000",
          603,
          "9000",
          587
        ],
        "end": 10000,
        "gap": 1000
      }
    },
    "facet_fields": {
      "user_location": [
        "indonesia",
        2897,
        "venezuela",
        1798,
        "london",
        1783,
        "istanbul",
        1674,
        "philippines",
        1284,
        "argentina",
        1199,
        "brasil",
        1017,
        "thailand",
        1009,
        "jakarta",
        912,
        "paris",
        911,
        "uk",
        902,
        "france",
        862,
        "\u6771\u4eac",
        809,
        "malaysia",
        758,
        "japan",
        719,
        "usa",
        696,
        "madrid",
        680,
        "espa\u00f1a",
        659,
        "\u5927\u962a",
        591,
        "new york",
        581,
        "t\u00fcrkiye",
        477
      ]
    },
    "facet_dates": {},
    "facet_queries": {}
  },
  "highlighting": {
    "438585496994725888": {},
    "438585509556658176": {},
    "438585555710791680": {},
    "438585614410063872": {},
    "438585664741703681": {},
    "438585618617352192": {},
    "438585568302489600": {},
    "438585593438560256": {},
    "438585606034046976": {},
    "438585664745906176": {},
    "438585526355238912": {},
    "438585601831763968": {},
    "438585618612756480": {},
    "438585501180653568": {},
    "438585580856045568": {}
  },
  "normalized_facets": [
    {
      "field": "user_location",
      "counts": [
        "indonesia",
        2897,
        "venezuela",
        1798,
        "london",
        1783,
        "istanbul",
        1674,
        "philippines",
        1284,
        "argentina",
        1199,
        "brasil",
        1017,
        "thailand",
        1009,
        "jakarta",
        912,
        "paris",
        911,
        "uk",
        902,
        "france",
        862,
        "\u6771\u4eac",
        809,
        "malaysia",
        758,
        "japan",
        719,
        "usa",
        696,
        "madrid",
        680,
        "espa\u00f1a",
        659,
        "\u5927\u962a",
        591,
        "new york",
        581,
        "t\u00fcrkiye",
        477
      ],
      "type": "field",
      "label": "Location"
    },
    {
      "end": 1000,
      "start": 0,
      "label": "Followers count",
      "field": "user_followers_count",
      "counts": [
        "0",
        4585,
        "100",
        3725,
        "200",
        2719,
        "300",
        1881,
        "400",
        1346,
        "500",
        966,
        "600",
        709,
        "700",
        668,
        "800",
        448,
        "900",
        383
      ],
      "gap": 100,
      "type": "range"
    },
    {
      "end": 10000,
      "start": 0,
      "label": "Tweet count",
      "field": "user_statuses_count",
      "counts": [
        "0",
        3981,
        "1000",
        2223,
        "2000",
        1701,
        "3000",
        1270,
        "4000",
        1051,
        "5000",
        922,
        "6000",
        784,
        "7000",
        770,
        "8000",
        603,
        "9000",
        587
      ],
      "gap": 1000,
      "type": "range"
    },
    {
      "end": "2014-02-28T12:00:00Z",
      "start": "2014-02-18T12:00:00Z",
      "label": "created_at",
      "field": "created_at",
      "counts": [
        "2014-02-25T16:05:00Z",
        97,
        "2014-02-25T16:10:00Z",
        92,
        "2014-02-25T16:15:00Z",
        115,
        "2014-02-25T16:20:00Z",
        83,
        "2014-02-25T16:25:00Z",
        108,
        "2014-02-25T16:30:00Z",
        120,
        "2014-02-25T16:35:00Z",
        98,
        "2014-02-25T16:40:00Z",
        101,
        "2014-02-25T16:45:00Z",
        110,
        "2014-02-25T16:50:00Z",
        100,
        "2014-02-25T16:55:00Z",
        96,
        "2014-02-25T17:00:00Z",
        119,
        "2014-02-25T17:05:00Z",
        125,
        "2014-02-25T17:10:00Z",
        115,
        "2014-02-25T17:15:00Z",
        116,
        "2014-02-25T17:20:00Z",
        107,
        "2014-02-25T17:25:00Z",
        139,
        "2014-02-25T17:30:00Z",
        131,
        "2014-02-25T17:35:00Z",
        123,
        "2014-02-25T17:40:00Z",
        125,
        "2014-02-25T17:45:00Z",
        125,
        "2014-02-25T17:50:00Z",
        102,
        "2014-02-25T17:55:00Z",
        149,
        "2014-02-25T18:00:00Z",
        130,
        "2014-02-25T18:05:00Z",
        123,
        "2014-02-25T18:10:00Z",
        145,
        "2014-02-25T18:15:00Z",
        108,
        "2014-02-25T18:20:00Z",
        133,
        "2014-02-25T18:25:00Z",
        132,
        "2014-02-25T18:30:00Z",
        162,
        "2014-02-25T18:35:00Z",
        142,
        "2014-02-25T18:40:00Z",
        139,
        "2014-02-25T18:45:00Z",
        156,
        "2014-02-25T18:50:00Z",
        132,
        "2014-02-25T18:55:00Z",
        159,
        "2014-02-25T19:00:00Z",
        157,
        "2014-02-25T19:05:00Z",
        136,
        "2014-02-25T19:10:00Z",
        137,
        "2014-02-25T19:15:00Z",
        164,
        "2014-02-25T19:20:00Z",
        132,
        "2014-02-25T19:25:00Z",
        154,
        "2014-02-25T19:30:00Z",
        187,
        "2014-02-25T19:35:00Z",
        161,
        "2014-02-25T19:40:00Z",
        159,
        "2014-02-25T19:45:00Z",
        144,
        "2014-02-25T19:50:00Z",
        157,
        "2014-02-25T19:55:00Z",
        146,
        "2014-02-25T20:00:00Z",
        193,
        "2014-02-25T20:05:00Z",
        175,
        "2014-02-25T20:10:00Z",
        189,
        "2014-02-25T20:15:00Z",
        182,
        "2014-02-25T20:20:00Z",
        168,
        "2014-02-25T20:25:00Z",
        171,
        "2014-02-25T20:30:00Z",
        175,
        "2014-02-25T20:35:00Z",
        169,
        "2014-02-25T20:40:00Z",
        182,
        "2014-02-25T20:45:00Z",
        163,
        "2014-02-25T20:50:00Z",
        186,
        "2014-02-25T20:55:00Z",
        184,
        "2014-02-25T21:00:00Z",
        216,
        "2014-02-25T21:05:00Z",
        202,
        "2014-02-25T21:10:00Z",
        176,
        "2014-02-25T21:15:00Z",
        196,
        "2014-02-25T21:20:00Z",
        192,
        "2014-02-25T21:25:00Z",
        189,
        "2014-02-25T21:30:00Z",
        190,
        "2014-02-25T21:35:00Z",
        187,
        "2014-02-25T21:40:00Z",
        215,
        "2014-02-25T21:45:00Z",
        197,
        "2014-02-25T21:50:00Z",
        174,
        "2014-02-25T21:55:00Z",
        179,
        "2014-02-25T22:00:00Z",
        216,
        "2014-02-25T22:05:00Z",
        185,
        "2014-02-25T22:10:00Z",
        178,
        "2014-02-25T22:15:00Z",
        219,
        "2014-02-25T22:20:00Z",
        190,
        "2014-02-25T22:25:00Z",
        190,
        "2014-02-25T22:30:00Z",
        196,
        "2014-02-25T22:35:00Z",
        176,
        "2014-02-25T22:40:00Z",
        215,
        "2014-02-25T22:45:00Z",
        212,
        "2014-02-25T22:50:00Z",
        200,
        "2014-02-25T22:55:00Z",
        216,
        "2014-02-25T23:00:00Z",
        225,
        "2014-02-25T23:05:00Z",
        186,
        "2014-02-25T23:10:00Z",
        181,
        "2014-02-25T23:15:00Z",
        213,
        "2014-02-25T23:20:00Z",
        214,
        "2014-02-25T23:25:00Z",
        189,
        "2014-02-25T23:30:00Z",
        188,
        "2014-02-25T23:35:00Z",
        174,
        "2014-02-25T23:40:00Z",
        199,
        "2014-02-25T23:45:00Z",
        165,
        "2014-02-25T23:50:00Z",
        198,
        "2014-02-25T23:55:00Z",
        158,
        "2014-02-26T00:00:00Z",
        193,
        "2014-02-26T00:05:00Z",
        168,
        "2014-02-26T00:10:00Z",
        186,
        "2014-02-26T00:15:00Z",
        182,
        "2014-02-26T00:20:00Z",
        174,
        "2014-02-26T00:25:00Z",
        185,
        "2014-02-26T00:30:00Z",
        184,
        "2014-02-26T00:35:00Z",
        157,
        "2014-02-26T00:40:00Z",
        161,
        "2014-02-26T00:45:00Z",
        158,
        "2014-02-26T00:50:00Z",
        175,
        "2014-02-26T00:55:00Z",
        151,
        "2014-02-26T01:00:00Z",
        203,
        "2014-02-26T01:05:00Z",
        154,
        "2014-02-26T01:10:00Z",
        158,
        "2014-02-26T01:15:00Z",
        153,
        "2014-02-26T01:20:00Z",
        141,
        "2014-02-26T01:25:00Z",
        150,
        "2014-02-26T01:30:00Z",
        165,
        "2014-02-26T01:35:00Z",
        152,
        "2014-02-26T01:40:00Z",
        161,
        "2014-02-26T01:45:00Z",
        178,
        "2014-02-26T01:50:00Z",
        145,
        "2014-02-26T01:55:00Z",
        161,
        "2014-02-26T02:00:00Z",
        171,
        "2014-02-26T02:05:00Z",
        151,
        "2014-02-26T02:10:00Z",
        141,
        "2014-02-26T02:15:00Z",
        145,
        "2014-02-26T02:20:00Z",
        149,
        "2014-02-26T02:25:00Z",
        131,
        "2014-02-26T02:30:00Z",
        134,
        "2014-02-26T02:35:00Z",
        142,
        "2014-02-26T02:40:00Z",
        133,
        "2014-02-26T02:45:00Z",
        157,
        "2014-02-26T02:50:00Z",
        154,
        "2014-02-26T02:55:00Z",
        146,
        "2014-02-26T03:00:00Z",
        124,
        "2014-02-26T03:05:00Z",
        147,
        "2014-02-26T03:10:00Z",
        142,
        "2014-02-26T03:15:00Z",
        137,
        "2014-02-26T03:20:00Z",
        139,
        "2014-02-26T03:25:00Z",
        156,
        "2014-02-26T03:30:00Z",
        18,
        "2014-02-26T04:10:00Z",
        15,
        "2014-02-26T04:15:00Z",
        65,
        "2014-02-26T04:20:00Z",
        53,
        "2014-02-26T04:25:00Z",
        66,
        "2014-02-26T04:30:00Z",
        65,
        "2014-02-26T04:35:00Z",
        57,
        "2014-02-26T04:40:00Z",
        61
      ],
      "gap": "+5MINUTES",
      "type": "chart"
    }
  ],
  "responseHeader": {
    "status": 0,
    "QTime": 248,
    "params": {
      "f.created_at.facet.range.start": "2014-02-28T12:00:00Z-10DAYS",
      "f.created_at.facet.range.gap": "+5MINUTES",
      "f.user_followers_count.facet.range.start": "0",
      "facet": "true",
      "facet.mincount": "1",
      "rows": "15",
      "f.user_statuses_count.facet.range.gap": "1000",
      "doAs": "romain",
      "start": "0",
      "user.name": "hue",
      "f.created_at.facet.range.end": "2014-02-28T12:00:00Z",
      "f.user_statuses_count.facet.range.start": "0",
      "facet.field": "user_location",
      "wt": "json",
      "hl": "true",
      "hl.fl": "text",
      "f.user_followers_count.facet.range.gap": "100",
      "facet.sort": "count",
      "f.user_statuses_count.facet.range.end": "10000",
      "f.user_followers_count.facet.range.end": "1000",
      "facet.limit": "100",
      "facet.range": [
        "created_at",
        "user_followers_count",
        "user_statuses_count"
      ],
      "f.created_at.facet.limit": "-1",
      "q": "*:*"
    }
  },
  "response": {
    "start": 0,
    "numFound": 22218,
    "docs": [
      {
        "created_at": "2014-02-25T16:05:05Z",
        "user_followers_count": 1897,
        "text": "RT @Fact: People who are strongly connected with their friends have stronger immune system than those who keep themselves isolated.",
        "user_screen_name": "Jade___Richards",
        "user_location": "UK",
        "user_statuses_count": 75045,
        "source": "<a href=\"http://dlvr.it\" rel=\"nofollow\">dlvr.it</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321259343872,
        "retweet_count": 0,
        "user_name": "Jade Richards News",
        "id": "438585496994725888",
        "user_friends_count": 2617
      },
      {
        "created_at": "2014-02-25T16:05:08Z",
        "user_followers_count": 39,
        "text": "Udh dimanee@nimnimc",
        "user_screen_name": "vergiawanlista2",
        "user_location": "JAKARTA",
        "user_statuses_count": 136,
        "source": "<a href=\"http://blackberry.com/twitter\" rel=\"nofollow\">Twitter for BlackBerry\u00ae</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321313869824,
        "retweet_count": 0,
        "user_name": "VergiawanLisTanto",
        "id": "438585509556658176",
        "user_friends_count": 121
      },
      {
        "created_at": "2014-02-25T16:05:06Z",
        "user_followers_count": 140,
        "text": "Emo. huwaaaaa... T.T",
        "user_screen_name": "nickdayah",
        "user_location": "Malaysia",
        "user_statuses_count": 8777,
        "source": "<a href=\"https://twitter.com/download/android\" rel=\"nofollow\">Twitter for  Android</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321315966976,
        "retweet_count": 0,
        "user_name": "Dayah Badri",
        "id": "438585501180653568",
        "user_friends_count": 144
      },
      {
        "created_at": "2014-02-25T16:05:19Z",
        "user_followers_count": 124,
        "text": "RT @2TheHacker_: hati hati dengan saya saya memauntau anda",
        "user_screen_name": "dayantiday",
        "user_location": "indonesia",
        "user_statuses_count": 7355,
        "source": "<a href=\"http://www.twitter.com\" rel=\"nofollow\">Sistem Autentikasi</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321318064128,
        "retweet_count": 0,
        "user_name": "dayanti sukmawati",
        "id": "438585555710791680",
        "user_friends_count": 2002
      },
      {
        "created_at": "2014-02-25T16:05:12Z",
        "user_followers_count": 14,
        "text": "RT @cosythirlwall: The girls have to win this, rt rt rt #VoteLittleMixUK #KCA",
        "user_screen_name": "glitterstars98",
        "user_location": "London",
        "user_statuses_count": 468,
        "source": "<a href=\"http://twitter.com/download/android\" rel=\"nofollow\">Twitter for Android</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321320161280,
        "retweet_count": 0,
        "user_name": "LM are my idols",
        "id": "438585526355238912",
        "user_friends_count": 28
      },
      {
        "created_at": "2014-02-25T16:05:30Z",
        "user_followers_count": 2666,
        "text": "Toriii (Red) Gates number 995 - 1000 @reginachristian #prettygirl #livebold #liveglorious\u2026 http://t.co/1LXuzzvmmk",
        "user_screen_name": "evantjandra",
        "user_location": "Jakarta",
        "user_statuses_count": 4439,
        "source": "<a href=\"http://instagram.com\" rel=\"nofollow\">Instagram</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321322258432,
        "retweet_count": 0,
        "user_name": "Evan Tjandra",
        "id": "438585601831763968",
        "user_friends_count": 587
      },
      {
        "created_at": "2014-02-25T16:05:31Z",
        "user_followers_count": 4258,
        "text": "\u5f15\u3063\u8d8a\u3057\u306e\u4e00\u62ec\u898b\u7a4d\u3082\u308a\u3057\u3066\u2026\u55b6\u696d\u306e\u96fb\u8a71\u304c\u5acc\u3067\u3059\u3088\u306d\uff61\u696d\u754c\u521d\uff01\u500b\u4eba\u60c5\u5831\u3092\u4f0f\u305b\u305f\u4e0a\u3067\u3001\u5f15\u8d8a\u696d\u8005\u62c5\u5f53\u8005\u3068\u30c1\u30e3\u30c3\u30c8\u3067\u3084\u308a\u53d6\u308a\u304c\u51fa\u6765\u308b\u30b5\u30a4\u30c8\u306f\u3053\u3053\u3060\u3051\uff01 http://t.co/OsRUDcfQTM",
        "user_screen_name": "otoku_matome",
        "user_location": "japan",
        "user_statuses_count": 15614,
        "source": "<a href=\"http://twittbot.net/\" rel=\"nofollow\">twittbot.net</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321324355584,
        "retweet_count": 0,
        "user_name": "\u304a\u5f97\u60c5\u5831\u307e\u3068\u3081",
        "id": "438585606034046976",
        "user_friends_count": 4016
      },
      {
        "created_at": "2014-02-25T16:05:28Z",
        "user_followers_count": 248,
        "text": "@TeladanRasul: Jgn kalian saling membenci,jangan saling hasad,jangan saling membelakangi,jangan saling memutuskan silaturrahim (HR Muslim)",
        "user_screen_name": "SATGASiti",
        "user_location": "Indonesia",
        "user_statuses_count": 1776,
        "source": "<a href=\"https://twitter.com/download/android\" rel=\"nofollow\">Twitter for  Android</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": 213140358,
        "_version_": 1461767321324355585,
        "retweet_count": 0,
        "user_name": "Nana\u2665",
        "id": "438585593438560256",
        "user_friends_count": 299
      },
      {
        "created_at": "2014-02-25T16:05:33Z",
        "user_followers_count": 103,
        "text": "It hurts, because I'm so lonely so I say I'm missing you. 2NE1's slow songs.. *cry*",
        "user_screen_name": "ahyu_savitri",
        "user_location": "Indonesia",
        "user_statuses_count": 268,
        "source": "<a href=\"https://twitter.com/download/android\" rel=\"nofollow\">Twitter for  Android</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321325404160,
        "retweet_count": 0,
        "user_name": "Savitri",
        "id": "438585614410063872",
        "user_friends_count": 347
      },
      {
        "created_at": "2014-02-25T16:05:25Z",
        "user_followers_count": 140,
        "text": "Dustin O'Halloran - An Ending, A Beginning http://t.co/jafiD40DFr",
        "user_screen_name": "adadidem",
        "user_location": "\u0130stanbul",
        "user_statuses_count": 11670,
        "source": "<a href=\"http://www.apple.com\" rel=\"nofollow\">iOS</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321325404161,
        "retweet_count": 0,
        "user_name": "Didem Saritas",
        "id": "438585580856045568",
        "user_friends_count": 287
      },
      {
        "created_at": "2014-02-25T16:05:22Z",
        "user_followers_count": 554,
        "text": "Me tiene que sonar la alarma a las 11:30 para tomar la pasti, espero despertarme U.U",
        "user_screen_name": "Badgalcamm",
        "user_location": "Argentina",
        "user_statuses_count": 19242,
        "source": "<a href=\"http://twitter.com/download/android\" rel=\"nofollow\">Twitter for Android</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321326452736,
        "retweet_count": 0,
        "user_name": "Camila\u2661",
        "id": "438585568302489600",
        "user_friends_count": 667
      },
      {
        "created_at": "2014-02-25T16:05:34Z",
        "user_followers_count": 33,
        "text": "RT @2TheHacker_: hati hati dengan saya saya memauntau anda",
        "user_screen_name": "uzie_oz",
        "user_location": "indonesia",
        "user_statuses_count": 5419,
        "source": "<a href=\"http://www.twitter.com\" rel=\"nofollow\">Sistem Autentikasi</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321326452737,
        "retweet_count": 0,
        "user_name": "ahmad fauji",
        "id": "438585618612756480",
        "user_friends_count": 2002
      },
      {
        "created_at": "2014-02-25T16:05:34Z",
        "user_followers_count": 86,
        "text": "En Espa\u00f1a existen tres tipos diferentes de legislaci\u00f3n sobre el r\u00e9gimen econ\u00f3mico matrimonial http://t.co/SVxwfCaYDS",
        "user_screen_name": "DGAabogados",
        "user_location": "Madrid",
        "user_statuses_count": 535,
        "source": "<a href=\"http://twitter.com/download/android\" rel=\"nofollow\">Twitter for Android</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321327501312,
        "retweet_count": 0,
        "user_name": "DGA Abogados",
        "id": "438585618617352192",
        "user_friends_count": 201
      },
      {
        "created_at": "2014-02-25T16:05:45Z",
        "user_followers_count": 547,
        "text": "Dan ga seharusnya mslh beginian gw yg ngadepin!!! Yg gw tau,gw cm ngurusin mslh DUIT dan kelancaran operasional divisi kitchen !!!!",
        "user_screen_name": "nona_etty",
        "user_location": "jakarta",
        "user_statuses_count": 1018,
        "source": "<a href=\"http://ubersocial.com\" rel=\"nofollow\">UberSocial for Android</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321329598464,
        "retweet_count": 0,
        "user_name": "Etty_Sundari",
        "id": "438585664741703681",
        "user_friends_count": 95
      },
      {
        "created_at": "2014-02-25T16:05:45Z",
        "user_followers_count": 267,
        "text": "This is real",
        "user_screen_name": "dinimslm",
        "user_location": "Malaysia",
        "user_statuses_count": 14817,
        "source": "<a href=\"http://twitter.com/download/android\" rel=\"nofollow\">Twitter for Android</a>",
        "in_reply_to_status_id": [
          -1
        ],
        "in_reply_to_user_id": -1,
        "_version_": 1461767321330647040,
        "retweet_count": 0,
        "user_name": "aurora ",
        "id": "438585664745906176",
        "user_friends_count": 649
      }
    ]
  }
}"""
