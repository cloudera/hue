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


def get_engine(user, engine='solr', facet=None, source='data', cluster='""'):
  if isinstance(engine, dict):
    if source == 'data':
      source = engine.get('source')
    engine = engine.get('engine', 'solr')

  if engine == 'report' and facet:
    engine = facet['properties'].get('engine')

  if engine != 'solr':
    if engine == 'impala':
      from impala.dashboard_api import ImpalaDashboardApi
      return ImpalaDashboardApi(user, engine, source=source, cluster=cluster)
    elif engine == 'hive':
      from beeswax.dashboard_api import HiveDashboardApi
      return HiveDashboardApi(user, engine, source=source, cluster=cluster)
    else:
      from notebook.dashboard_api import SQLDashboardApi
      return SQLDashboardApi(user, engine, source=source, cluster=cluster)
  else:
    from search.dashboard_api import SearchApi
    # Could add source to Solr at some point, to behave like a 'view', but need state in query history or URL params
    return SearchApi(user, cluster)


class DashboardApi(object):

  def __init__(self, user, cluster):
    self.user = user
    self.cluster = cluster

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
