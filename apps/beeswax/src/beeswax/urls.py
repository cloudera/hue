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

urlpatterns = patterns('beeswax',
  url(r'^$', 'views.index'),
  url(r'^tables$', 'views.show_tables'),
  url(r'^table/(?P<table>\w+)$', 'views.describe_table'),
  url(r'^table/(?P<table>\w+)/partitions$', 'views.describe_partitions'),
  url(r'^table/(?P<table>\w+)/load$', 'views.load_table'),
  url(r'^table/(?P<table>\w+)/read$', 'views.read_table'),
  url(r'^table/(?P<table>\w+)/drop$', 'views.drop_table'),
  url(r'^create$', 'create_table.index'),
  url(r'^create/create_table$', 'create_table.create_table'),
  url(r'^create/import_wizard$', 'create_table.import_wizard'),
  url(r'^create/auto_load$', 'create_table.load_after_create'),
  url(r'^execute$', 'views.execute_query'),
  url(r'^execute/(?P<design_id>\d+)$', 'views.execute_query'),
  url(r'^explain_parameterized/(?P<design_id>\d+)$', 'views.explain_parameterized_query'),
  url(r'^execute_parameterized/(?P<design_id>\d+)$', 'views.execute_parameterized_query'),
  url(r'^my_queries$', 'views.my_queries'),
  url(r'^list_designs$', 'views.list_designs'),
  url(r'^delete_design/(?P<design_id>\d+)$', 'views.delete_design'),
  url(r'^clone_design/(?P<design_id>\d+)$', 'views.clone_design'),
  url(r'^query_history$', 'views.list_query_history'),
  url(r'^report_gen$', 'views.edit_report'),
  url(r'^report_gen/(?P<design_id>\d+)$', 'views.edit_report'),
  url(r'^watch/(?P<id>\d+)$', 'views.watch_query'),
  url(r'^results/(?P<id>\d+)/(?P<first_row>\d+)$', 'views.view_results'),
  url(r'^download/(?P<id>\d+)/(?P<format>\w+)$', 'views.download'),
  url(r'^configuration$', 'views.configuration'),
  url(r'^install_examples$', 'views.install_examples'),
  url(r'^save_results/(?P<id>\d+)$', 'views.save_results'),
  url(r'^query_cb/done/(?P<server_id>\S+)$', 'views.query_done_cb'),
)
