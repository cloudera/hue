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
  url(r'^$', 'index'),

  url(r'^tables$', 'show_tables'),
  url(r'^table/(?P<table>\w+)$', 'describe_table'),
  url(r'^table/(?P<table>\w+)/partitions$', 'describe_partitions'),
  url(r'^table/(?P<table>\w+)/load$', 'load_table'),
  url(r'^table/(?P<table>\w+)/read$', 'read_table'),
  url(r'^table/(?P<table>\w+)/drop$', 'drop_table'),

  url(r'^execute$', 'execute_query'),
  url(r'^execute/(?P<design_id>\d+)$', 'execute_query'),
  url(r'^explain_parameterized/(?P<design_id>\d+)$', 'explain_parameterized_query'),
  url(r'^execute_parameterized/(?P<design_id>\d+)$', 'execute_parameterized_query'),
  url(r'^watch/(?P<id>\d+)$', 'watch_query'),
  url(r'^watch/json/(?P<id>\d+)$', 'watch_query_refresh_json'),
  url(r'^results/(?P<id>\d+)/(?P<first_row>\d+)$', 'view_results'),
  url(r'^download/(?P<id>\d+)/(?P<format>\w+)$', 'download'),
  url(r'^save_results/(?P<id>\d+)$', 'save_results'),

  url(r'^my_queries$', 'my_queries'),
  url(r'^list_designs$', 'list_designs'),
  url(r'^delete_design/(?P<design_id>\d+)$', 'delete_design'),
  url(r'^clone_design/(?P<design_id>\d+)$', 'clone_design'),
  url(r'^query_history$', 'list_query_history'),

  url(r'^configuration$', 'configuration'),
  url(r'^install_examples$', 'install_examples'),
  url(r'^query_cb/done/(?P<server_id>\S+)$', 'query_done_cb'),
)

urlpatterns += patterns(
  'beeswax.create_table',

  url(r'^create$', 'index'),
  url(r'^create/create_table$', 'create_table'),
  url(r'^create/import_wizard$', 'import_wizard'),
  url(r'^create/auto_load$', 'load_after_create'),
)
