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

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from django.shortcuts import redirect

from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException

from search.api import SolrApi, _guess_gap, _zoom_range_facet, _new_range_facet
from search.conf import SOLR_URL
from search.data_export import download as export_download
from search.decorators import allow_admin_only
from search.forms import QueryForm, CollectionForm
from search.management.commands import search_setup
from search.models import Collection, augment_solr_response2, augment_solr_exception
from search.search_controller import SearchController

from django.utils.encoding import force_unicode
from desktop.lib.rest.http_client import RestException



LOG = logging.getLogger(__name__)


def initial_collection(request, hue_collections):
  return hue_collections[0].id


def dashboard(request):
  return render('dashboard.mako', request, {})


def index(request):
  hue_collections = SearchController(request.user).get_search_collections()
  collection_id = request.GET.get('collection')
  
  if not hue_collections or not collection_id:
    if request.user.is_superuser:
      return admin_collections(request, True)
    else:
      return no_collections(request)

  collection = Collection.objects.get(id=collection_id) # TODO perms HUE-1987
  query = {'q': '', 'fqs': []}

  return render('search2.mako', request, {
    'collection': collection,
    'query': query,
  })


def new_search(request):
  collection = Collection(name='twitter_demo', label='New Twitter Template')
  query = {'q': '', 'fqs': []}

  return render('search2.mako', request, {
    'collection': collection,
    'query': query,
  })


def search(request):
  response = {}  
  
  collection = json.loads(request.POST.get('collection', '{}')) # TODO decorator with doc model perms
  query = json.loads(request.POST.get('query', '{}'))

  if collection['id']:
    hue_collection = Collection.objects.get(id=collection['id']) # TODO perms

  print request.POST
    
  if collection:
    try:      
      response = SolrApi(SOLR_URL.get(), request.user).query2(collection, query)
      response = augment_solr_response2(response, collection, query)
      print response
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
    augment_solr_exception(response, collection)

  return HttpResponse(json.dumps(response), mimetype="application/json")


def save(request):
  response = {'status': -1}  
  
  collection = json.loads(request.POST.get('collection', '{}')) # TODO perms decorator
  layout = json.loads(request.POST.get('layout', '{}')) 
    
  if collection:
    if collection['id']:
      hue_collection = Collection.objects.get(id=collection['id'])
    else:
      hue_collection = Collection.objects.create2(name=collection['name'], label=collection['label'])
    hue_collection.update_properties({'collection': collection})
    hue_collection.update_properties({'layout': layout})
    # Todo update certain atttributes like, label, enabled...
    hue_collection.save()
    response['status'] = 0
    response['id'] = hue_collection.id
    response['message'] = _('Page saved !')
  else:
    response['message'] = _('There is no collection to search.')

  return HttpResponse(json.dumps(response), mimetype="application/json")


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


# TODO security
def index_fields_dynamic(request, collection_id):  
  result = {'status': -1, 'message': 'Error'}

  solr_query = {}
  
  try:
    hue_collection = Collection.objects.get(id=collection_id)
    solr_query['collection'] = hue_collection.name
    
    dynamic_fields = SolrApi(SOLR_URL.get(), request.user).luke(hue_collection.name)
    result['message'] = ''
    result['dynamic_fields'] = [name for name, properties in dynamic_fields['fields'].iteritems() if 'dynamicBase' in properties]
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


# TODO security
def get_document(request):  
  result = {'status': -1, 'message': 'Error'}

  try:
    collection = json.loads(request.POST.get('collection', '{}'))
    doc_id = request.POST.get('id')
            
    if doc_id:
      result['doc'] = SolrApi(SOLR_URL.get(), request.user).get(collection['name'], doc_id)
      result['status'] = 0
      result['message'] = ''
    else:
      result['message'] = _('This document does not have any index id.')
      result['status'] = 1
    
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


# TODO security
def get_timeline(request):  
  result = {'status': -1, 'message': 'Error'}

  try:
    collection = json.loads(request.POST.get('collection', '{}'))
    query = json.loads(request.POST.get('query', '{}'))
  
    facet = json.loads(request.POST.get('facet', '{}'))
    facet_filter = request.POST.get('d', '{}')
        
    facet_id = facet['id']
  
    # Only care about our current field:value filter
    for fq in query['fqs']:
      if fq['id'] == facet_id:
        fq['filter'] = [facet_filter] 
    
    # Remove other facets from collection
    collection['facets'] = filter(lambda f: f['widgetType'] == 'histogram-widget', collection['facets'])
    
    response = SolrApi(SOLR_URL.get(), request.user).query2(collection, query)
    response = augment_solr_response2(response, collection, query)

    result['series'] = {'label': facet_filter, 'counts': response['normalized_facets'][0]['counts']}
    result['status'] = 0
    result['message'] = ''
    
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


# TODO security
def new_facet(request):  
  result = {'status': -1, 'message': 'Error'}
  
  try:
    collection = json.loads(request.POST.get('collection', '{}'))
    
    facet_id = request.POST['id']
    facet_label = request.POST['label']
    facet_field = request.POST['field']
    widget_type = request.POST['widget_type']
    properties = {
      'sort': 'desc',
      'canRange': False,
    }
    
    solr_api = SolrApi(SOLR_URL.get(), request.user)
    range_properties = _new_range_facet(solr_api, collection, facet_field)
                          
    if range_properties:
      facet_type = 'range'
      properties.update(range_properties)       
    elif widget_type == 'hit-widget':
      facet_type = 'query'      
    else:
      facet_type = 'field'        
        
    result['message'] = ''
    result['facet'] = {
      'id': facet_id,
      'label': facet_label,
      'field': facet_field,
      'type': facet_type,
      'widgetType': widget_type,
      'properties': properties
    }
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")

# TODO security
def get_range_facet(request):  
  result = {'status': -1, 'message': 'Error'}

  try:
    collection = json.loads(request.POST.get('collection', '{}'))
    facet = json.loads(request.POST.get('facet', '{}'))
    action = request.POST.get('action', 'select')
            
    solr_api = SolrApi(SOLR_URL.get(), request.user)

    if action == 'select':
      properties = _guess_gap(solr_api, collection, facet['field'], facet['properties']['start'], facet['properties']['end'])
    else:
      properties = _zoom_range_facet(solr_api, collection, facet['field'])
            
    result['properties'] = properties
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
