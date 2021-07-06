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

from desktop import api_public
from desktop.lib.botserver import api as botserver_api

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path


# "New" query API (i.e. connector based, lean arguments).
# e.g. https://demo.gethue.com/api/query/execute/hive
urlpatterns = [
  re_path(r'^query/create_notebook/?$', api_public.create_notebook, name='query_create_notebook'),
  re_path(r'^query/autocomplete/?$', api_public.autocomplete, name='query_autocomplete_databases'),
]

# Compatibility with "old" private API.
# e.g. https://demo.gethue.com/notebook/api/execute/hive
urlpatterns += [
  re_path(r'^get_config/?$', api_public.get_config),
  re_path(r'^get_namespaces/(?P<interface>[\w\-]+)/?$', api_public.get_context_namespaces),  # To remove

  re_path(r'^editor/create_notebook/?$', api_public.create_notebook, name='editor_create_notebook'),
  re_path(r'^editor/create_session/?$', api_public.create_session, name='editor_create_session'),
  re_path(r'^editor/close_session/?$', api_public.close_session, name='editor_close_session'),
  re_path(r'^editor/execute(?:/(?P<dialect>.+))?/?$', api_public.execute, name='editor_execute'),
  re_path(r'^editor/check_status/?$', api_public.check_status, name='editor_check_status'),
  re_path(r'^editor/fetch_result_data/?$', api_public.fetch_result_data, name='editor_fetch_result_data'),
  re_path(r'^editor/fetch_result_metadata/?$', api_public.fetch_result_metadata, name='editor_fetch_result_metadata'),
  re_path(r'^editor/fetch_result_size/?$', api_public.fetch_result_size, name='editor_fetch_result_size'),
  re_path(r'^editor/cancel_statement/?$', api_public.cancel_statement, name='editor_cancel_statement'),
  re_path(r'^editor/close_statement/?$', api_public.close_statement, name='editor_close_statement'),
  re_path(r'^editor/get_logs/?$', api_public.get_logs, name='editor_get_logs'),

  re_path(r'^editor/describe/(?P<database>[^/]*)/?$', api_public.describe, name='editor_describe_database'),
  re_path(r'^editor/describe/(?P<database>[^/]*)/(?P<table>[\w_\-]+)/?$', api_public.describe, name='editor_describe_table'),
  re_path(r'^editor/describe/(?P<database>[^/]*)/(?P<table>\w+)/stats(?:/(?P<column>\w+))?/?$', api_public.describe, name='editor_describe_column'),

  re_path(r'^editor/autocomplete/?$', api_public.autocomplete, name='editor_autocomplete_databases'),
  re_path(
      r"^editor/autocomplete/(?P<database>[^/?]*)/?$",
      api_public.autocomplete,
      name="editor_autocomplete_tables",
  ),
  re_path(
      r"^editor/autocomplete/(?P<database>[^/?]*)/(?P<table>[\w_\-]+)/?$",
      api_public.autocomplete,
      name="editor_autocomplete_columns",
  ),
  re_path(
      r"^editor/autocomplete/(?P<database>[^/?]*)/(?P<table>[\w_\-]+)/(?P<column>\w+)/?$",
      api_public.autocomplete,
      name="editor_autocomplete_column",
  ),
  re_path(
      r"^editor/autocomplete/(?P<database>[^/?]*)/(?P<table>[\w_\-]+)/(?P<column>\w+)/(?P<nested>.+)/?$",
      api_public.autocomplete,
      name="editor_autocomplete_nested",
  ),

  # HS2, RDBMS, JDBC
  re_path(r'^editor/sample/(?P<database>[^/?]*)/(?P<table>[\w_\-]+)/?$', api_public.get_sample_data, name='api_sample_data'),
  re_path(
    r'^editor/sample/(?P<database>[^/?]*)/(?P<table>[\w_\-]+)/(?P<column>\w+)/?$',
    api_public.get_sample_data,
    name='api_sample_data_column'
  ),
]

urlpatterns += [
  re_path(r'^storage/view=(?P<path>.*)$', api_public.storage_view, name='storage_view'),
  re_path(r'^storage/download=(?P<path>.*)$', api_public.storage_download, name='storage_download'),
  re_path(r'^storage/upload/file/?$', api_public.storage_upload_file, name='storage_upload_file'),
]

# Slack install API for using CORS by default
urlpatterns += [
  re_path(r'^slack/install/?$', botserver_api.generate_slack_install_link, name='botserver.api.slack_install_link'),
]
