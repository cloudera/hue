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

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render

from search.api import SolrApi
from search.conf import SOLR_URL
from search.decorators import allow_admin_only
from search.forms import QueryForm
from search.models import Core, temp_fixture_hook


LOG = logging.getLogger(__name__)


def index(request):
  temp_fixture_hook()

  cores = SolrApi(SOLR_URL.get()).cores()
  hue_cores = Core.objects.all()

  search_form = QueryForm(request.GET)
  response = {}
  solr_query = {}

  if search_form.is_valid():
    core = search_form.cleaned_data['cores']
    solr_query['core'] = core
    solr_query['q'] = search_form.cleaned_data['query']
    solr_query['fq'] = search_form.cleaned_data['fq']
    solr_query['sort'] = search_form.cleaned_data['sort'] or 'created_at desc'
    solr_query['rows'] = search_form.cleaned_data['rows'] or 15
    solr_query['start'] = search_form.cleaned_data['start'] or 0
    solr_query['facets'] = search_form.cleaned_data['facets'] or 1

    hue_core = Core.objects.get(name=core)

    response = SolrApi(SOLR_URL.get()).query(solr_query, hue_core)

  return render('index.mako', request, {
    'search_form': search_form,
    'response': response,
    'solr_query': solr_query,
    'hue_core': hue_core,
    'hue_cores': hue_cores,
    'rr': json.dumps(response),
    'json': json,
  })


@allow_admin_only
def admin(request):
  # To cross check both
  cores = SolrApi(SOLR_URL.get()).cores()
  hue_cores = Core.objects.all()

  return render('admin.mako', request, {
    'cores': cores,
    'hue_cores': hue_cores,
  })


@allow_admin_only
def admin_core_properties(request, core):
  solr_core = SolrApi(SOLR_URL.get()).core(core)
  hue_core = Core.objects.get(name=core)
  hue_cores = Core.objects.all()

  return render('admin_core_properties.mako', request, {
    'solr_core': solr_core,
    'hue_core': hue_core,
    'hue_cores': hue_cores,
  })


@allow_admin_only
def admin_core_schema(request, core):
  solr_schema = SolrApi(SOLR_URL.get()).schema(core)
  hue_core = Core.objects.get(name=core)
  hue_cores = Core.objects.all()

  return render('admin_core_schema.mako', request, {
    'solr_schema': solr_schema,
    'hue_core': hue_core,
    'hue_cores': hue_cores,
  })


@allow_admin_only
def admin_core_template(request, core):
  solr_core = SolrApi(SOLR_URL.get()).core(core)
  hue_core = Core.objects.get(name=core)
  hue_cores = Core.objects.all()

  if request.method == 'POST':
    hue_core.result.update_from_post(request.POST)
    hue_core.result.save()
    return HttpResponse(json.dumps({}), mimetype="application/json")

  solr_query = {}
  solr_query['core'] = core
  solr_query['q'] = ''
  solr_query['fq'] = ''
  solr_query['rows'] = 10
  solr_query['start'] = 0
  solr_query['facets'] = 0

  response = SolrApi(SOLR_URL.get()).query(solr_query, hue_core)

  return render('admin_core_template.mako', request, {
    'solr_core': solr_core,
    'hue_core': hue_core,
    'hue_cores': hue_cores,
    'sample_data': json.dumps(response["response"]["docs"]),
  })


@allow_admin_only
def admin_core_facets(request, core):
  solr_core = SolrApi(SOLR_URL.get()).core(core)
  hue_core = Core.objects.get(name=core)
  hue_cores = Core.objects.all()

  if request.method == 'POST':
    hue_core.facets.update_from_post(request.POST)
    hue_core.facets.save()
    return HttpResponse(json.dumps({}), mimetype="application/json")

  return render('admin_core_facets.mako', request, {
    'solr_core': solr_core,
    'hue_core': hue_core,
    'hue_cores': hue_cores,
  })


@allow_admin_only
def admin_core_sorting(request, core):
  solr_core = SolrApi(SOLR_URL.get()).core(core)
  hue_core = Core.objects.get(name=core)
  hue_cores = Core.objects.all()

  if request.method == 'POST':
    hue_core.sorting.update_from_post(request.POST)
    hue_core.sorting.save()
    return HttpResponse(json.dumps({}), mimetype="application/json")

  return render('admin_core_sorting.mako', request, {
    'solr_core': solr_core,
    'hue_core': hue_core,
    'hue_cores': hue_cores,
  })
