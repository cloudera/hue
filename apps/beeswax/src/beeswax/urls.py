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

from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('beeswax.views',
  url(r'^$', 'index', name='index'),

  url(r'^execute/?$', 'execute_query', name='execute_query'),
  url(r'^execute/design/(?P<design_id>\d+)$', 'execute_query', name='execute_design'),
  url(r'^execute/query/(?P<query_history_id>\d+)$', 'execute_query', name='watch_query_history'),
  url(r'^results/(?P<id>\d+)/(?P<first_row>\d+)$', 'view_results', name='view_results'),
  url(r'^download/(?P<id>\d+)/(?P<format>\w+)$', 'download', name='download'),

  url(r'^my_queries$', 'my_queries', name='my_queries'),
  url(r'^list_designs$', 'list_designs', name='list_designs'),
  url(r'^list_trashed_designs$', 'list_trashed_designs', name='list_trashed_designs'),
  url(r'^delete_designs$', 'delete_design', name='delete_design'),
  url(r'^restore_designs$', 'restore_design', name='restore_design'),
  url(r'^clone_design/(?P<design_id>\d+)$', 'clone_design', name='clone_design'),
  url(r'^query_history$', 'list_query_history', name='list_query_history'),

  url(r'^configuration$', 'configuration', name='configuration'),
  url(r'^install_examples$', 'install_examples', name='install_examples'),
  url(r'^query_cb/done/(?P<server_id>\S+)$', 'query_done_cb', name='query_done_cb'),
)

urlpatterns += patterns(
  'beeswax.create_database',

  url(r'^create/database$', 'create_database', name='create_database'),
)

urlpatterns += patterns(
  'beeswax.create_table',

  url(r'^create/create_table/(?P<database>\w+)$', 'create_table', name='create_table'),
  url(r'^create/import_wizard/(?P<database>\w+)$', 'import_wizard', name='import_wizard'),
  url(r'^create/auto_load/(?P<database>\w+)$', 'load_after_create', name='load_after_create'),
)

urlpatterns += patterns(
  'beeswax.api',

  url(r'^api/autocomplete/$', 'autocomplete', name='api_autocomplete_databases'),
  url(r'^api/autocomplete/(?P<database>\w+)/$', 'autocomplete', name='api_autocomplete_tables'),
  url(r'^api/autocomplete/(?P<database>\w+)/(?P<table>\w+)$', 'autocomplete', name='api_autocomplete_columns'),
  url(r'^api/design/(?P<design_id>\d+)?$', 'save_query_design', name='api_save_design'),
  url(r'^api/design/(?P<design_id>\d+)/get$', 'fetch_saved_design', name='api_fetch_saved_design'),
  url(r'^api/query/(?P<query_history_id>\d+)/get$', 'fetch_query_history', name='api_fetch_query_history'),
  url(r'^api/query/parameters$', 'parameters', name='api_parameters'),
  url(r'^api/query/execute/(?P<design_id>\d+)?$', 'execute', name='api_execute'),
  url(r'^api/query/(?P<query_history_id>\d+)/cancel$', 'cancel_query', name='api_cancel_query'),
  url(r'^api/query/(?P<query_history_id>\d+)/close/?$', 'close_operation', name='api_close_operation'),
  url(r'^api/query/(?P<query_history_id>\d+)/results/save/hive/table$', 'save_results_hive_table', name='api_save_results_hive_table'),
  url(r'^api/query/(?P<query_history_id>\d+)/results/save/hdfs/file$', 'save_results_hdfs_file', name='api_save_results_hdfs_file'),
  url(r'^api/query/(?P<query_history_id>\d+)/results/save/hdfs/directory$', 'save_results_hdfs_directory', name='api_save_results_hdfs_directory'),
  url(r'^api/watch/json/(?P<id>\d+)$', 'watch_query_refresh_json', name='api_watch_query_refresh_json'),

  url(r'^api/table/(?P<database>\w+)/(?P<table>\w+)$', 'describe_table', name='describe_table'),
)

urlpatterns += patterns(
  'libsentry.views',

  url(r'^api/sentry/autocomplete/roles$', 'roles', name='api_sentry_roles')
)
