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

from django.conf.urls import url
from rdbms import views as rdbms_views
from rdbms import api as rdbms_api
from beeswax import views as beeswax_views
from beeswax import api as beeswax_api

# Views
urlpatterns = [
  url(r'^$', rdbms_views.index, name='index'),
  url(r'^execute/?$', rdbms_views.execute_query, name='execute_query'),
  url(r'^execute/design/(?P<design_id>\d+)$', rdbms_views.execute_query, name='execute_design'),
  url(r'^execute/query/(?P<query_history_id>\d+)$', rdbms_views.execute_query, name='watch_query_history')
]

# APIs
urlpatterns += [
  url(r'^api/servers/?$', rdbms_api.servers, name='api_servers'),
  url(r'^api/servers/(?P<server>\w+)/databases/?$', rdbms_api.databases, name='api_databases'),
  url(r'^api/servers/(?P<server>\w+)/databases/(?P<database>.+?)/tables/?$', rdbms_api.tables, name='api_tables'),
  url(r'^api/servers/(?P<server>\w+)/databases/(?P<database>.+?)/tables/(?P<table>\w+)/columns/?$', rdbms_api.columns, name='api_columns'),
  url(r'^api/query(?:/(?P<design_id>\d+))?/?$', rdbms_api.save_query, name='api_save_query'),
  url(r'^api/query/(?P<design_id>\d+)/get$', rdbms_api.fetch_saved_query, name='api_fetch_saved_query'),
  url(r'^api/execute(?:/(?P<design_id>\d+))?/?$', rdbms_api.execute_query, name='api_execute_query'),
  url(r'^api/explain/?$', rdbms_api.explain_query, name='api_explain_query'),
  url(r'^api/results/(?P<id>\d+)/(?P<first_row>\d+)$', rdbms_api.fetch_results, name='api_fetch_results')
]

urlpatterns += [
  url(r'^my_queries$', beeswax_views.my_queries, name='my_queries'),
  url(r'^list_designs$', beeswax_views.list_designs, name='list_designs'),
  url(r'^list_trashed_designs$', beeswax_views.list_trashed_designs, name='list_trashed_designs'),
  url(r'^delete_designs$', beeswax_views.delete_design, name='delete_design'),
  url(r'^restore_designs$', beeswax_views.restore_design, name='restore_design'),
  url(r'^clone_design/(?P<design_id>\d+)$', beeswax_views.clone_design, name='clone_design'),
  url(r'^query_history$', beeswax_views.list_query_history, name='list_query_history')
]

urlpatterns += [
  url(r'^autocomplete/$', beeswax_api.autocomplete, name='api_autocomplete_databases'),
  url(r'^autocomplete/(?P<database>\w+)/$', beeswax_api.autocomplete, name='api_autocomplete_tables'),
  url(r'^autocomplete/(?P<database>\w+)/(?P<table>\w+)$', beeswax_api.autocomplete, name='api_autocomplete_columns')
]
