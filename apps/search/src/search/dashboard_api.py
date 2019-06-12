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

import logging

from libsolr.api import SolrApi
from indexer.solr_client import SolrClient
from search.conf import SOLR_URL

from dashboard.dashboard_api import DashboardApi
from dashboard.models import augment_solr_response


LOG = logging.getLogger(__name__)


class SearchApi(DashboardApi):

  def __init__(self, user, cluster):
    DashboardApi.__init__(self, user, cluster)
    self.api = SolrApi(SOLR_URL.get(), self.user)

  def query(self, collection, query, facet=None):
    if facet:
      collection['template']['rows'] = 0
      collection['facets'] = [facet]
    response = self.api.query(collection, query)
    return augment_solr_response(response, collection, query)

  def datasets(self, show_all=False): # True if non Solr Cloud
    client = SolrClient(user=self.user)
    show_all = show_all or not client.is_solr_cloud_mode()
    return [index['name'] for index in client.get_indexes(include_cores=show_all)]

  def fields(self, collection):
    return self.api.fields(collection)

  def schema_fields(self, collection):
    return self.api.fields(collection)

  def luke(self, collection):
    return self.api.luke(collection)

  def stats(self, collection, field, query=None, facet=''):
    return self.api.stats(collection, field, query, facet)

  def get(self, collection, doc_id):
    return self.api.get(collection, doc_id)
