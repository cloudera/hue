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


LOG = logging.getLogger(__name__)


def get_engine(user, engine='solr'):
  if isinstance(engine, dict):
    engine = engine.get('engine', 'solr')

  if engine != 'solr':
    from impala.dashboard_api import SQLApi
    return SQLApi(user, engine)
  else:
    from search.dashboard_api import SearchApi
    return SearchApi(user)


class DashboardApi(object):

  def __init__(self, user):
    self.user = user

  def datasets(self, show_all=False): pass

  def query(self, collection, query, facet=None): pass

  def suggest(self, collection, query): pass

  def schema_fields(self, collection): pass

  def fields(self, collection): pass

  def luke(self, collection, query): pass

  def update(self, collection, json_edits, content_type, version): pass

  def stats(self, collection, field, query=None, facet=''): pass

  def terms(self, collection, field, properties): pass

  def fetch_result(self, collection, query, facet=None): pass

  def get(self, collection, doc_id): pass
