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

from django.conf.urls import patterns, url


# Views
urlpatterns = patterns('rdbms.views',
  url(r'^$', 'index', name='index'),
  url(r'^execute/?$', 'execute_query', name='execute_query'),
  url(r'^execute/design/(?P<design_id>\d+)$', 'execute_query', name='execute_design'),
  url(r'^execute/query/(?P<query_history_id>\d+)$', 'execute_query', name='watch_query_history')
)

# APIs
urlpatterns += patterns('rdbms.api',
  url(r'^api/servers/?$', 'servers', name='api_servers'),
  url(r'^api/servers/(?P<server>\w+)/databases/?$', 'databases', name='api_databases'),
  url(r'^api/servers/(?P<server>\w+)/databases/(?P<database>.+?)/tables/?$', 'tables', name='api_tables'),
  url(r'^api/servers/(?P<server>\w+)/databases/(?P<database>.+?)/tables/(?P<table>\w+)/columns/?$', 'columns', name='api_columns'),
  url(r'^api/query/((?P<design_id>\d+)/?)?$', 'save_query', name='api_save_query'),
  url(r'^api/query/(?P<design_id>\d+)/get$', 'fetch_saved_query', name='api_fetch_saved_query'),
  url(r'^api/execute/(?P<design_id>\d+)?$', 'execute_query', name='api_execute_query'),
  url(r'^api/explain/?$', 'explain_query', name='api_explain_query'),
  url(r'^api/results/(?P<id>\d+)/(?P<first_row>\d+)$', 'fetch_results', name='api_fetch_results')
)

urlpatterns += patterns('beeswax.views',
  url(r'^my_queries$', 'my_queries', name='my_queries'),
  url(r'^list_designs$', 'list_designs', name='list_designs'),
  url(r'^list_trashed_designs$', 'list_trashed_designs', name='list_trashed_designs'),
  url(r'^delete_designs$', 'delete_design', name='delete_design'),
  url(r'^restore_designs$', 'restore_design', name='restore_design'),
  url(r'^clone_design/(?P<design_id>\d+)$', 'clone_design', name='clone_design'),
  url(r'^query_history$', 'list_query_history', name='list_query_history')
)

urlpatterns += patterns('beeswax.api',
  url(r'^autocomplete/$', 'autocomplete', name='api_autocomplete_databases'),
  url(r'^autocomplete/(?P<database>\w+)/$', 'autocomplete', name='api_autocomplete_tables'),
  url(r'^autocomplete/(?P<database>\w+)/(?P<table>\w+)$', 'autocomplete', name='api_autocomplete_columns')
)
