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

from desktop.lib.django_util import render

from search.forms import QueryForm
from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from django.http import HttpResponse


# http://lucene.apache.org/solr/api-4_0_0-BETA/doc-files/tutorial.html#Getting+Started
SOLR_URL = 'http://localhost:8983/solr/'

LOG = logging.getLogger(__name__)


def index(request):
  search_form = QueryForm(request.GET)
  response = {}
  
  if search_form.is_valid():
    response = SolrApi(SOLR_URL).query(search_form.cleaned_data['query'])
    response = json.loads(response)

  return render('index.mako', request, {'search_form': search_form, 'response': response, 'rr': json.dumps(response)})

# Simple API for now
class SolrApi(object):
  def __init__(self, solr_url):
    self._url = solr_url
    self._client = HttpClient(self._url, logger=LOG)
    self._root = Resource(self._client)

  def query(self, query):    
    return self._root.get('collection1/browse', {'q': query, 'wt': 'json'})
