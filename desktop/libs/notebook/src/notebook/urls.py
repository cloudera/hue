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

from notebook import views as notebook_views
from notebook import api as notebook_api

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path

# Views
urlpatterns = [
  re_path(r'^$', notebook_views.notebook, name='index'),
  re_path(r'^notebook/?$', notebook_views.notebook, name='notebook'),
  re_path(r'^notebook_embeddable/?$', notebook_views.notebook_embeddable, name='notebook_embeddable'),
  re_path(r'^notebooks/?$', notebook_views.notebooks, name='notebooks'),
  re_path(r'^new/?$', notebook_views.new, name='new'),
  re_path(r'^download/?$', notebook_views.download, name='download'),
  re_path(r'^install_examples/?$', notebook_views.install_examples, name='install_examples'),
  re_path(r'^delete/?$', notebook_views.delete, name='delete'),
  re_path(r'^copy/?$', notebook_views.copy, name='copy'),

  re_path(r'^editor/?$', notebook_views.editor, name='editor'),
  re_path(r'^editor_m/?$', notebook_views.editor_m, name='editor_m'),
  re_path(r'^browse/(?P<database>[^/?]+)/(?P<table>\w+)(?:/(?P<partition_spec>.+?))?/?$', notebook_views.browse, name='browse'),
  re_path(r'^execute_and_watch/?$', notebook_views.execute_and_watch, name='execute_and_watch'),
]

# APIs
urlpatterns += [
  re_path(r'^api/create_notebook/?$', notebook_api.create_notebook, name='create_notebook'),
  re_path(r'^api/create_session/?$', notebook_api.create_session, name='create_session'),
  re_path(r'^api/close_session/?$', notebook_api.close_session, name='close_session'),
  re_path(r'^api/execute(?:/(?P<dialect>.+))?/?$', notebook_api.execute, name='execute'),
  re_path(r'^api/check_status/?$', notebook_api.check_status, name='check_status'),
  re_path(r'^api/fetch_result_data/?$', notebook_api.fetch_result_data, name='fetch_result_data'),
  re_path(r'^api/fetch_result_metadata/?$', notebook_api.fetch_result_metadata, name='fetch_result_metadata'),
  re_path(r'^api/fetch_result_size/?$', notebook_api.fetch_result_size, name='fetch_result_size'),
  re_path(r'^api/cancel_statement/?$', notebook_api.cancel_statement, name='cancel_statement'),
  re_path(r'^api/close_statement/?$', notebook_api.close_statement, name='close_statement'),
  re_path(r'^api/get_logs/?$', notebook_api.get_logs, name='get_logs'),

  re_path(r'^api/explain/?$', notebook_api.explain, name='explain'),
  re_path(r'^api/format/?$', notebook_api.format, name='format'),
  re_path(r'^api/get_external_statement/?$', notebook_api.get_external_statement, name='get_external_statement'),

  re_path(r'^api/get_history/?', notebook_api.get_history, name='get_history'),
  re_path(r'^api/clear_history/?', notebook_api.clear_history, name='clear_history'),

  re_path(r'^api/notebook/save/?$', notebook_api.save_notebook, name='save_notebook'),
  re_path(r'^api/notebook/open/?$', notebook_api.open_notebook, name='open_notebook'),
  re_path(r'^api/notebook/close/?$', notebook_api.close_notebook, name='close_notebook'),

  re_path(r'^api/notebook/export_result/?$', notebook_api.export_result, name='export_result'),

  re_path(r'^api/optimizer/statement/risk/?$', notebook_api.statement_risk, name='statement_risk'),
  re_path(r'^api/optimizer/statement/compatibility/?$', notebook_api.statement_compatibility, name='statement_compatibility'),
  re_path(r'^api/optimizer/statement/similarity/?$', notebook_api.statement_similarity, name='statement_similarity'),
]

# Assist API
urlpatterns += [
  # HS2, RDBMS, JDBC
  re_path(r'^api/autocomplete/?$', notebook_api.autocomplete, name='api_autocomplete_databases'),
  re_path(r'^api/autocomplete/(?P<database>[^/?]*)/?$', notebook_api.autocomplete, name='api_autocomplete_tables'),
  re_path(r'^api/autocomplete/(?P<database>[^/?]*)/(?P<table>[\w_\-]+)/?$', notebook_api.autocomplete, name='api_autocomplete_columns'),
  re_path(
    r'^api/autocomplete/(?P<database>[^/?]*)/(?P<table>[\w_\-]+)/(?P<column>\w+)/?$',
    notebook_api.autocomplete,
    name='api_autocomplete_column'
  ),
  re_path(
    r'^api/autocomplete/(?P<database>[^/?]*)/(?P<table>[\w_\-]+)/(?P<column>\w+)/(?P<nested>.+)/?$',
    notebook_api.autocomplete,
    name='api_autocomplete_nested'
  ),
  re_path(r'^api/sample/(?P<database>[^/?]*)/(?P<table>[\w_\-]+)/?$', notebook_api.get_sample_data, name='api_sample_data'),
  re_path(
    r'^api/sample/(?P<database>[^/?]*)/(?P<table>[\w_\-]+)/(?P<column>\w+)/?$',
    notebook_api.get_sample_data,
    name='api_sample_data_column'
  ),

  # SQLite
  re_path(r'^api/autocomplete//?(?P<server>[\w_\-/]+)/(?P<database>[^/?]*)/?$', notebook_api.autocomplete, name='api_autocomplete_tables'),
  re_path(
    r'^api/autocomplete//?(?P<server>[\w_\-/]+)/(?P<database>[^/?]*)/(?P<table>\w+)/?$',
    notebook_api.autocomplete,
    name='api_autocomplete_columns'
  ),
  re_path(
    r'^api/autocomplete//?(?P<server>[\w_\-/]+)/(?P<database>[^/?]*)/(?P<table>\w+)/(?P<column>\w+)/?$',
    notebook_api.autocomplete,
    name='api_autocomplete_column'
  ),
  re_path(
    r'^api/sample/(?P<server>[\w_\-/]+)/(?P<database>[^/?]*)/(?P<table>\w+)/?$', notebook_api.get_sample_data, name='api_sample_data'
  ),
  re_path(
    r'^api/sample/(?P<server>[\w_\-/]+)/(?P<database>[^/?]*)/(?P<table>\w+)/(?P<column>\w+)/?$',
    notebook_api.get_sample_data,
    name='api_sample_data_column'
  ),
]

# Table API
urlpatterns += [
  re_path(r'^api/describe/(?P<database>[^/]*)/?$', notebook_api.describe, name='api_describe_database'),
  re_path(r'^api/describe/(?P<database>[^/]*)/(?P<table>[\w_\-]+)/?$', notebook_api.describe, name='api_describe_table'),
  re_path(
    r'^api/describe/(?P<database>[^/]*)/(?P<table>\w+)/stats(?:/(?P<column>\w+))?/?$', notebook_api.describe, name='api_describe_column'
  ),
]
