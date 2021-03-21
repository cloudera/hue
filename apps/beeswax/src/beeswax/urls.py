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

import sys

from beeswax import views as beeswax_views
from beeswax import create_database as beeswax_create_database
from beeswax import create_table as beeswax_create_table
from beeswax import api as beeswax_api

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path

urlpatterns = [
  re_path(r'^$', beeswax_views.index, name='index'),

  re_path(r'^execute/?$', beeswax_views.execute_query, name='execute_query'),
  re_path(r'^execute/design/(?P<design_id>\d+)$', beeswax_views.execute_query, name='execute_design'),
  re_path(r'^execute/query/(?P<query_history_id>\d+)$', beeswax_views.execute_query, name='watch_query_history'),
  re_path(r'^results/(?P<id>\d+)/(?P<first_row>\d+)$', beeswax_views.view_results, name='view_results'),
  re_path(r'^download/(?P<id>\d+)/(?P<format>\w+)$', beeswax_views.download, name='download'),

  re_path(r'^my_queries$', beeswax_views.my_queries, name='my_queries'),
  re_path(r'^list_designs$', beeswax_views.list_designs, name='list_designs'),
  re_path(r'^list_trashed_designs$', beeswax_views.list_trashed_designs, name='list_trashed_designs'),
  re_path(r'^delete_designs$', beeswax_views.delete_design, name='delete_design'),
  re_path(r'^restore_designs$', beeswax_views.restore_design, name='restore_design'),
  re_path(r'^clone_design/(?P<design_id>\d+)$', beeswax_views.clone_design, name='clone_design'),
  re_path(r'^query_history$', beeswax_views.list_query_history, name='list_query_history'),

  re_path(r'^configuration/?$', beeswax_views.configuration, name='configuration'),
  re_path(r'^install_examples$', beeswax_views.install_examples, name='install_examples'),
  re_path(r'^query_cb/done/(?P<server_id>\S+)$', beeswax_views.query_done_cb, name='query_done_cb'),
]

urlpatterns += [
  re_path(r'^create/database$', beeswax_create_database.create_database, name='create_database'),
]

urlpatterns += [
  re_path(r'^create/create_table/(?P<database>\w+)$', beeswax_create_table.create_table, name='create_table'),
  re_path(r'^create/import_wizard/(?P<database>\w+)$', beeswax_create_table.import_wizard, name='import_wizard'),
  re_path(r'^create/auto_load/(?P<database>\w+)$', beeswax_create_table.load_after_create, name='load_after_create'),
]

urlpatterns += [
  re_path(r'^api/session/?$', beeswax_api.get_session, name='api_get_session'),
  re_path(r'^api/session/(?P<session_id>\d+)/?$', beeswax_api.get_session, name='api_get_session'),
  re_path(r'^api/session/(?P<session_id>\d+)/close/?$', beeswax_api.close_session, name='api_close_session'),
  re_path(r'^api/settings/?$', beeswax_api.get_settings, name='get_settings'),
  re_path(r'^api/functions/?$', beeswax_api.get_functions, name='get_functions'),

  # Deprecated by Notebook API
  re_path(r'^api/autocomplete/?$', beeswax_api.autocomplete, name='api_autocomplete_databases'),
  re_path(r'^api/autocomplete/(?P<database>\w+)/?$', beeswax_api.autocomplete, name='api_autocomplete_tables'),
  re_path(r'^api/autocomplete/(?P<database>\w+)/(?P<table>\w+)/?$', beeswax_api.autocomplete, name='api_autocomplete_columns'),
  re_path(
    r'^api/autocomplete/(?P<database>\w+)/(?P<table>\w+)/(?P<column>\w+)/?$', beeswax_api.autocomplete, name='api_autocomplete_column'
  ),
  re_path(
    r'^api/autocomplete/(?P<database>\w+)/(?P<table>\w+)/(?P<column>\w+)/(?P<nested>.+)/?$',
    beeswax_api.autocomplete,
    name='api_autocomplete_nested'
  ),

  re_path(r'^api/design(?:/(?P<design_id>\d+))?/?$', beeswax_api.save_query_design, name='api_save_design'),
  re_path(r'^api/design/(?P<design_id>\d+)/get$', beeswax_api.fetch_saved_design, name='api_fetch_saved_design'),

  re_path(r'^api/query/(?P<query_history_id>\d+)/get$', beeswax_api.fetch_query_history, name='api_fetch_query_history'),
  re_path(r'^api/query/parameters$', beeswax_api.parameters, name='api_parameters'),
  re_path(r'^api/query/execute(?:/(?P<design_id>\d+))?/?$', beeswax_api.execute, name='api_execute'),
  re_path(r'^api/query/(?P<query_history_id>\d+)/cancel/?$', beeswax_api.cancel_query, name='api_cancel_query'),
  re_path(r'^api/query/(?P<query_history_id>\d+)/close/?$', beeswax_api.close_operation, name='api_close_operation'),
  re_path(
    r'^api/query/(?P<query_history_id>\d+)/results/save/hive/table/?$',
    beeswax_api.save_results_hive_table,
    name='api_save_results_hive_table'
  ),
  re_path(
    r'^api/query/(?P<query_history_id>\d+)/results/save/hdfs/file/?$',
    beeswax_api.save_results_hdfs_file,
    name='api_save_results_hdfs_file'
  ),
  re_path(
    r'^api/query/(?P<query_history_id>\d+)/results/save/hdfs/directory/?$',
    beeswax_api.save_results_hdfs_directory,
    name='api_save_results_hdfs_directory'
  ),
  re_path(r'^api/watch/json/(?P<id>\d+)/?$', beeswax_api.watch_query_refresh_json, name='api_watch_query_refresh_json'),

  re_path(r'^api/query/clear_history/?$', beeswax_api.clear_history, name='clear_history'),

  re_path(r'^api/table/(?P<database>\w+)/(?P<table>\w+)/?$', beeswax_api.describe_table, name='describe_table'),
  re_path(r'^api/table/(?P<database>\w+)/(?P<table>\w+)/indexes/?$', beeswax_api.get_indexes, name='get_indexes'),
  re_path(r'^api/table/(?P<database>\w+)/(?P<table>\w+)/sample/?$', beeswax_api.get_sample_data, name='get_sample_data'),
  re_path(
    r'^api/table/(?P<database>\w+)/(?P<table>\w+)/(?P<column>\w+)/sample/?$', beeswax_api.get_sample_data, name='get_sample_data_column'
  ),
  re_path(
    r'^api/table/(?P<database>\w+)/(?P<table>\w+)/stats(?:/(?P<column>\w+))?/?$', beeswax_api.get_table_stats, name='get_table_stats'
  ),
  re_path(
    r'^api/table/(?P<database>\w+)/(?P<table>\w+)/terms/(?P<column>\w+)(?:/(?P<prefix>\w+))?/?$',
    beeswax_api.get_top_terms,
    name='get_top_terms'
  ),

  re_path(r'^api/analyze/(?P<database>\w+)/(?P<table>\w+)(?:/(?P<columns>\w+))?/?$', beeswax_api.analyze_table, name='analyze_table'),
]
