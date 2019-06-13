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

# FIXME: This could be replaced with hooking into the `AppConfig.ready()`
# signal in Django 1.7:
#
# https://docs.djangoproject.com/en/1.7/ref/applications/#django.apps.AppConfig.ready
#
# For now though we have to load in the monkey patches here because we know
# this file has been loaded after `desktop.settings` has been loaded.

# Start DBProxy server
from notebook import views as notebook_views
from notebook import api as notebook_api

# Views
urlpatterns = [
  url(r'^$', notebook_views.notebook, name='index'),
  url(r'^notebook/?$', notebook_views.notebook, name='notebook'),
  url(r'^notebook_embeddable/?$', notebook_views.notebook_embeddable, name='notebook_embeddable'),
  url(r'^notebooks/?$', notebook_views.notebooks, name='notebooks'),
  url(r'^new/?$', notebook_views.new, name='new'),
  url(r'^download/?$', notebook_views.download, name='download'),
  url(r'^install_examples/?$', notebook_views.install_examples, name='install_examples'),
  url(r'^delete/?$', notebook_views.delete, name='delete'),
  url(r'^copy/?$', notebook_views.copy, name='copy'),

  url(r'^editor/?$', notebook_views.editor, name='editor'),
  url(r'^editor_m/?$', notebook_views.editor_m, name='editor_m'),
  url(r'^browse/(?P<database>\w+)/(?P<table>\w+)(?:/(?P<partition_spec>.+?))?/?$', notebook_views.browse, name='browse'),
  url(r'^execute_and_watch/?$', notebook_views.execute_and_watch, name='execute_and_watch'),
]

# APIs
urlpatterns += [
  url(r'^api/create_notebook/?$', notebook_api.create_notebook, name='create_notebook'),
  url(r'^api/create_session/?$', notebook_api.create_session, name='create_session'),
  url(r'^api/close_session/?$', notebook_api.close_session, name='close_session'),
  url(r'^api/execute(?:/(?P<engine>.+))?/?$', notebook_api.execute, name='execute'),
  url(r'^api/check_status/?$', notebook_api.check_status, name='check_status'),
  url(r'^api/fetch_result_data/?$', notebook_api.fetch_result_data, name='fetch_result_data'),
  url(r'^api/fetch_result_metadata/?$', notebook_api.fetch_result_metadata, name='fetch_result_metadata'),
  url(r'^api/fetch_result_size/?$', notebook_api.fetch_result_size, name='fetch_result_size'),
  url(r'^api/cancel_statement/?$', notebook_api.cancel_statement, name='cancel_statement'),
  url(r'^api/close_statement/?$', notebook_api.close_statement, name='close_statement'),
  url(r'^api/get_logs/?$', notebook_api.get_logs, name='get_logs'),
  
  url(r'^api/explain/?$', notebook_api.explain, name='explain'),
  url(r'^api/format/?$', notebook_api.format, name='format'),
  url(r'^api/get_external_statement/?$', notebook_api.get_external_statement, name='get_external_statement'),

  url(r'^api/get_history/?', notebook_api.get_history, name='get_history'),
  url(r'^api/clear_history/?', notebook_api.clear_history, name='clear_history'),

  url(r'^api/notebook/save/?$', notebook_api.save_notebook, name='save_notebook'),
  url(r'^api/notebook/open/?$', notebook_api.open_notebook, name='open_notebook'),
  url(r'^api/notebook/close/?$', notebook_api.close_notebook, name='close_notebook'),

  url(r'^api/notebook/export_result/?$', notebook_api.export_result, name='export_result'),

  url(r'^api/optimizer/statement/risk/?$', notebook_api.statement_risk, name='statement_risk'),
  url(r'^api/optimizer/statement/compatibility/?$', notebook_api.statement_compatibility, name='statement_compatibility'),
  url(r'^api/optimizer/statement/similarity/?$', notebook_api.statement_similarity, name='statement_similarity'),
]

# Assist API
urlpatterns += [
  # HS2, RDBMS, JDBC
  url(r'^api/autocomplete/?$', notebook_api.autocomplete, name='api_autocomplete_databases'),
  url(r'^api/autocomplete/(?P<database>\w+)/?$', notebook_api.autocomplete, name='api_autocomplete_tables'),
  url(r'^api/autocomplete/(?P<database>\w+)/(?P<table>[\w_\-]+)/?$', notebook_api.autocomplete, name='api_autocomplete_columns'),
  url(r'^api/autocomplete/(?P<database>\w+)/(?P<table>[\w_\-]+)/(?P<column>\w+)/?$', notebook_api.autocomplete, name='api_autocomplete_column'),
  url(r'^api/autocomplete/(?P<database>\w+)/(?P<table>[\w_\-]+)/(?P<column>\w+)/(?P<nested>.+)/?$', notebook_api.autocomplete, name='api_autocomplete_nested'),
  url(r'^api/sample/(?P<database>\w+)/(?P<table>[\w_\-]+)/?$', notebook_api.get_sample_data, name='api_sample_data'),
  url(r'^api/sample/(?P<database>\w+)/(?P<table>[\w_\-]+)/(?P<column>\w+)/?$', notebook_api.get_sample_data, name='api_sample_data_column'),

  # SQLite
  url(r'^api/autocomplete//?(?P<server>[\w_\-/]+)/(?P<database>[\w._\-0-9]+)/?$', notebook_api.autocomplete, name='api_autocomplete_tables'),
  url(r'^api/autocomplete//?(?P<server>[\w_\-/]+)/(?P<database>[\w._\-0-9]+)/(?P<table>\w+)/?$', notebook_api.autocomplete, name='api_autocomplete_columns'),
  url(r'^api/autocomplete//?(?P<server>[\w_\-/]+)/(?P<database>[\w._\-0-9]+)/(?P<table>\w+)/(?P<column>\w+)/?$', notebook_api.autocomplete, name='api_autocomplete_column'),
  url(r'^api/sample/(?P<server>[\w_\-/]+)/(?P<database>[\w._\-0-9]+)/(?P<table>\w+)/?$', notebook_api.get_sample_data, name='api_sample_data'),
  url(r'^api/sample/(?P<server>[\w_\-/]+)/(?P<database>[\w._\-0-9]+)/(?P<table>\w+)/(?P<column>\w+)/?$', notebook_api.get_sample_data, name='api_sample_data_column'),
]

# Table API
urlpatterns += [
  url(r'^api/describe/(?P<database>\w+)/?$', notebook_api.describe, name='api_describe_database'),
  url(r'^api/describe/(?P<database>\w+)/(?P<table>[\w_\-]+)/?$', notebook_api.describe, name='api_describe_table'),
  url(r'^api/describe/(?P<database>\w+)/(?P<table>\w+)/stats(?:/(?P<column>\w+))?/?$', notebook_api.describe, name='api_describe_column'),
]