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

from search.conf import SOLR_URL
from search.models import augment_solr_response


LOG = logging.getLogger(__name__)


def get_engine(user, name='solr'):
  if name == 'db':
    return DBApi(user)
  else:
    return SearchApi(user)


class DashboardApi(object):

  def __init__(self, user):
    self.user = user

  def query(self, collection, query): pass

  def suggest(self, collection, query): pass

  def schema_fields(self, collection): pass

  def fields(self, collection): pass

  def luke(self, collection, query): pass

  def get(self, collection, doc_id): pass

  def update(self, collection, json_edits, content_type, version): pass

  def stats(self, collection, field, query, facet): pass

  def terms(self, collection, field, properties): pass


class SearchApi(DashboardApi):

  def query(self, collection, query):
    response = SolrApi(SOLR_URL.get(), self.user).query(collection, query)
    return augment_solr_response(response, collection, query)


class DBApi(DashboardApi):
  pass
