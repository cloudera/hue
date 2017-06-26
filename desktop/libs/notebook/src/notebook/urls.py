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

# FIXME: This could be replaced with hooking into the `AppConfig.ready()`
# signal in Django 1.7:
#
# https://docs.djangoproject.com/en/1.7/ref/applications/#django.apps.AppConfig.ready
#
# For now though we have to load in the monkey patches here because we know
# this file has been loaded after `desktop.settings` has been loaded.

# Start DBProxy server
import notebook.monkey_patches


# Views
urlpatterns = patterns('notebook.views',
  url(r'^$', 'notebook', name='index'),
  url(r'^notebook/?$', 'notebook', name='notebook'),
  url(r'^notebook_embeddable/?$', 'notebook_embeddable', name='notebook_embeddable'),
  url(r'^notebooks/?$', 'notebooks', name='notebooks'),
  url(r'^new/?$', 'new', name='new'),
  url(r'^download/?$', 'download', name='download'),
  url(r'^install_examples/?$', 'install_examples', name='install_examples'),
  url(r'^delete/?$', 'delete', name='delete'),
  url(r'^copy/?$', 'copy', name='copy'),

  url(r'^editor/?$', 'editor', name='editor'),
  url(r'^editor_m/?$', 'editor_m', name='editor_m'),
  url(r'^browse/(?P<database>\w+)/(?P<table>\w+)/(?P<partition_spec>.+?)?$', 'browse', name='browse'),
  url(r'^execute_and_watch/?$', 'execute_and_watch', name='execute_and_watch'),
)

# APIs
urlpatterns += patterns('notebook.api',
  url(r'^api/create_notebook/?$', 'create_notebook', name='create_notebook'),
  url(r'^api/create_session/?$', 'create_session', name='create_session'),
  url(r'^api/close_session/?$', 'close_session', name='close_session'),
  url(r'^api/execute/?(?P<engine>.+)?$', 'execute', name='execute'),
  url(r'^api/check_status/?$', 'check_status', name='check_status'),
  url(r'^api/fetch_result_data/?$', 'fetch_result_data', name='fetch_result_data'),
  url(r'^api/fetch_result_metadata/?$', 'fetch_result_metadata', name='fetch_result_metadata'),
  url(r'^api/fetch_result_size/?$', 'fetch_result_size', name='fetch_result_size'),
  url(r'^api/cancel_statement/?$', 'cancel_statement', name='cancel_statement'),
  url(r'^api/close_statement/?$', 'close_statement', name='close_statement'),
  url(r'^api/get_logs/?$', 'get_logs', name='get_logs'),

  url(r'^api/explain/?$', 'explain', name='explain'),
  url(r'^api/format/?$', 'format', name='format'),
  url(r'^api/get_external_statement/?$', 'get_external_statement', name='get_external_statement'),

  url(r'^api/get_history/?', 'get_history', name='get_history'),
  url(r'^api/clear_history/?', 'clear_history', name='clear_history'),

  url(r'^api/notebook/save/?$', 'save_notebook', name='save_notebook'),
  url(r'^api/notebook/open/?$', 'open_notebook', name='open_notebook'),
  url(r'^api/notebook/close/?$', 'close_notebook', name='close_notebook'),

  url(r'^api/notebook/export_result/?$', 'export_result', name='export_result'),

  url(r'^api/optimizer/statement/risk/?$', 'statement_risk', name='statement_risk'),
  url(r'^api/optimizer/statement/compatibility/?$', 'statement_compatibility', name='statement_compatibility'),
  url(r'^api/optimizer/statement/similarity/?$', 'statement_similarity', name='statement_similarity'),
)

# Assist API
urlpatterns += patterns('notebook.api',
  # HS2, RDBMS, JDBC
  url(r'^api/autocomplete/?$', 'autocomplete', name='api_autocomplete_databases'),
  url(r'^api/autocomplete/(?P<database>\w+)/?$', 'autocomplete', name='api_autocomplete_tables'),
  url(r'^api/autocomplete/(?P<database>\w+)/(?P<table>\w+)/?$', 'autocomplete', name='api_autocomplete_columns'),
  url(r'^api/autocomplete/(?P<database>\w+)/(?P<table>\w+)/(?P<column>\w+)/?$', 'autocomplete', name='api_autocomplete_column'),
  url(r'^api/autocomplete/(?P<database>\w+)/(?P<table>\w+)/(?P<column>\w+)/(?P<nested>.+)/?$', 'autocomplete', name='api_autocomplete_nested'),
  url(r'^api/sample/(?P<database>\w+)/(?P<table>\w+)/?$', 'get_sample_data', name='api_sample_data'),
  url(r'^api/sample/(?P<database>\w+)/(?P<table>\w+)/(?P<column>\w+)/?$', 'get_sample_data', name='api_sample_data_column'),

  # SQLite
  url(r'^api/autocomplete//?(?P<server>[\w_\-/]+)/(?P<database>[\w._\-0-9]+)/?$', 'autocomplete', name='api_autocomplete_tables'),
  url(r'^api/autocomplete//?(?P<server>[\w_\-/]+)/(?P<database>[\w._\-0-9]+)/(?P<table>\w+)/?$', 'autocomplete', name='api_autocomplete_columns'),
  url(r'^api/autocomplete//?(?P<server>[\w_\-/]+)/(?P<database>[\w._\-0-9]+)/(?P<table>\w+)/(?P<column>\w+)/?$', 'autocomplete', name='api_autocomplete_column'),
  url(r'^api/sample/(?P<server>[\w_\-/]+)/(?P<database>[\w._\-0-9]+)/(?P<table>\w+)/?$', 'get_sample_data', name='api_sample_data'),
  url(r'^api/sample/(?P<server>[\w_\-/]+)/(?P<database>[\w._\-0-9]+)/(?P<table>\w+)/(?P<column>\w+)/?$', 'get_sample_data', name='api_sample_data_column'),
)