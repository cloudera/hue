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

from django.urls import re_path

from desktop import api_public
from desktop.lib.botserver import api as botserver_api

# "New" query API (i.e. connector based, lean arguments).
# e.g. https://demo.gethue.com/api/query/execute/hive
urlpatterns = [
  re_path(r'^query/create_notebook/?$', api_public.create_notebook, name='query_create_notebook'),
  re_path(r'^query/autocomplete/?$', api_public.autocomplete, name='query_autocomplete_databases'),
]

# Compatibility with "old" private API.
# e.g. https://demo.gethue.com/notebook/api/execute/hive
urlpatterns += [
  re_path(r'^banners/?$', api_public.get_banners, name='core_get_banners'),
  re_path(r'^logs/?$', api_public.get_hue_logs, name='core_get_hue_logs'),
  re_path(r'^logs/download/?$', api_public.download_hue_logs, name='core_download_hue_logs'),
  re_path(r'^get_config/?$', api_public.get_config),
  re_path(r'^get_namespaces/(?P<interface>[\w\-]+)/?$', api_public.get_context_namespaces),  # To remove
]

urlpatterns += [
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
  re_path(r'^editor/get_history/?', api_public.get_history, name='editor_get_history'),
  re_path(r'^editor/describe/(?P<database>[^/?]*)/?$', api_public.describe, name='editor_describe_database'),
  re_path(r'^editor/describe/(?P<database>[^/?]*)/(?P<table>[^/?]+)/?$', api_public.describe, name='editor_describe_table'),
  re_path(
    r'^editor/describe/(?P<database>[^/?]*)/(?P<table>[^/?]+)/stats(?:/(?P<column>[^/?]+))?/?$',
    api_public.describe,
    name='editor_describe_column',
  ),
  re_path(r'^editor/autocomplete/?$', api_public.autocomplete, name='editor_autocomplete_databases'),
  re_path(
    r"^editor/autocomplete/(?P<database>[^/?]*)/?$",
    api_public.autocomplete,
    name="editor_autocomplete_tables",
  ),
  re_path(
    r"^editor/autocomplete/(?P<database>[^/?]*)/(?P<table>[^/?]+)/?$",
    api_public.autocomplete,
    name="editor_autocomplete_columns",
  ),
  re_path(
    r"^editor/autocomplete/(?P<database>[^/?]*)/(?P<table>[^/?]+)/(?P<column>[^/?]+)/?$",
    api_public.autocomplete,
    name="editor_autocomplete_column",
  ),
  re_path(
    r"^editor/autocomplete/(?P<database>[^/?]*)/(?P<table>[^/?]+)/(?P<column>[^/?]+)/(?P<nested>.+)/?$",
    api_public.autocomplete,
    name="editor_autocomplete_nested",
  ),
  re_path(r'^editor/sample/(?P<database>[^/?]*)/(?P<table>[^/?]+)/?$', api_public.get_sample_data, name='editor_sample_data'),
  re_path(
    r'^editor/sample/(?P<database>[^/?]*)/(?P<table>[^/?]+)/(?P<column>[^/?]+)/?$',
    api_public.get_sample_data,
    name='editor_sample_data_column',
  ),
  re_path(
    r"^editor/sample/(?P<database>[^/?]*)/(?P<table>[^/?]+)/(?P<column>[^/?]+)/(?P<nested>.+)/?$",
    api_public.get_sample_data,
    name="editor_sample_data_nested",
  ),
]

urlpatterns += [
  re_path(r'^storage/view=(?P<path>.*)$', api_public.storage_view, name='storage_view'),
  re_path(
    r'^taskserver/upload/available_space/?$',
    api_public.taskserver_get_available_space_for_upload,
    name='taskserver_get_available_space_for_upload',
  ),
]

urlpatterns += [
  re_path(r'^storage/filesystems/?$', api_public.storage_get_filesystems, name='storage_get_filesystems'),
  re_path(r'^storage/list/?$', api_public.storage_listdir_paged, name='storage_listdir_paged'),
  re_path(r'^storage/create/file/?$', api_public.storage_touch, name='storage_touch'),
  re_path(r'^storage/create/directory/?$', api_public.storage_mkdir, name='storage_mkdir'),
  re_path(r'^storage/save/?$', api_public.storage_save_file, name="storage_save_file"),
  re_path(r'^storage/rename/?$', api_public.storage_rename, name='storage_rename'),
  re_path(r'^storage/move/?$', api_public.storage_move, name='storage_move'),
  re_path(r'^storage/copy/?$', api_public.storage_copy, name='storage_copy'),
  re_path(r'^storage/upload/file/?$', api_public.storage_upload_file, name='storage_upload_file'),
  re_path(r'^storage/upload/chunks/?$', api_public.storage_upload_chunks, name='storage_upload_chunks'),
  re_path(r'^storage/upload/complete/?$', api_public.storage_upload_complete, name='storage_upload_complete'),
  re_path(r'^storage/stat/?$', api_public.storage_stat, name='storage_stat'),
  re_path(r'^storage/display/?$', api_public.storage_display, name='storage_display'),
  re_path(r'^storage/download/?$', api_public.storage_download, name='storage_download'),
  re_path(r'^storage/delete/?$', api_public.storage_rmtree, name='storage_rmtree'),
  re_path(r'^storage/content_summary/?$', api_public.storage_content_summary, name='storage_content_summary'),
  re_path(r'^storage/replication/?$', api_public.storage_set_replication, name='storage_set_replication'),
  re_path(r'^storage/trash/path/?$', api_public.storage_get_trash_path, name='storage_get_trash_path'),
  re_path(r'^storage/trash/restore/?$', api_public.storage_trash_restore, name='storage_trash_restore'),
  re_path(r'^storage/trash/purge/?$', api_public.storage_trash_purge, name='storage_trash_purge'),
  re_path(r'^storage/chown/?$', api_public.storage_chown, name='storage_chown'),
  re_path(r'^storage/chmod/?$', api_public.storage_chmod, name='storage_chmod'),
  re_path(
    r'^storage/extract_archive/?$', api_public.storage_extract_archive_using_batch_job, name='storage_extract_archive_using_batch_job'
  ),
  re_path(r'^storage/compress_files/?$', api_public.storage_compress_files_using_batch_job, name='storage_compress_files_using_batch_job'),
  re_path(r'^storage/move/bulk/?$', api_public.storage_bulk_move, name='storage_bulk_move'),
  re_path(r'^storage/copy/bulk/?$', api_public.storage_bulk_copy, name='storage_bulk_copy'),
  re_path(r'^storage/delete/bulk/?$', api_public.storage_bulk_rmtree, name='storage_bulk_rmtree'),
  re_path(r'^storage/trash/restore/bulk/?$', api_public.storage_trash_bulk_restore, name='storage_trash_bulk_restore'),
  re_path(r'^storage/chown/bulk/?$', api_public.storage_bulk_chown, name='storage_bulk_chown'),
  re_path(r'^storage/chmod/bulk/?$', api_public.storage_bulk_chmod, name='storage_bulk_chmod'),
]

urlpatterns += [
  re_path(
    r'^(?P<dialect>.+)/analyze/(?P<database>\w+)/(?P<table>\w+)(?:/(?P<columns>\w+))?/?$',
    api_public.analyze_table,
    name='dialect_analyze_table',
  ),
]

# Slack install API for using CORS by default
urlpatterns += [
  re_path(r'^slack/install/?$', botserver_api.generate_slack_install_link, name='botserver.api.slack_install_link'),
]

urlpatterns += [
  re_path(r'^indexer/guess_format/?$', api_public.guess_format, name='indexer_guess_format'),
  re_path(r'^indexer/guess_field_types/?$', api_public.guess_field_types, name='indexer_guess_field_types'),
  re_path(r'^indexer/importer/submit', api_public.importer_submit, name='indexer_importer_submit'),
]

urlpatterns += [
  re_path(r'^connector/types/?$', api_public.get_connector_types, name='connector_get_types'),
  re_path(r'^connector/instances/?$', api_public.get_connectors_instances, name='connector_get_instances'),
  re_path(r'^connector/instance/new/(?P<dialect>[\w\-]+)/(?P<interface>[\w\-]+)$', api_public.new_connector, name='connector_new'),
  re_path(r'^connector/instance/get/(?P<id>\d+)$', api_public.get_connector, name='connector_get'),
  re_path(r'^connector/instance/delete/?$', api_public.delete_connector, name='connector_delete'),
  re_path(r'^connector/instance/update/?$', api_public.update_connector, name='connector_update'),
  re_path(r'^connector/instance/test/?$', api_public.test_connector, name='connector_test'),
  re_path(r'^connector/examples/install/?$', api_public.install_connector_examples, name='connector_install_examples'),
]

urlpatterns += [
  re_path(r'^optimizer/top_databases/?$', api_public.top_databases, name='optimizer_top_databases'),
  re_path(r'^optimizer/top_tables/?$', api_public.top_tables, name='optimizer_top_tables'),
  re_path(r'^optimizer/top_columns/?$', api_public.top_columns, name='optimizer_top_columns'),
  re_path(r'^optimizer/top_joins/?$', api_public.top_joins, name='optimizer_top_joins'),
  re_path(r'^optimizer/top_filters/?$', api_public.top_filters, name='optimizer_top_filters'),
  re_path(r'^optimizer/top_aggs/?$', api_public.top_aggs, name='optimizer_top_aggs'),
  re_path(r'^optimizer/query_risk/?$', api_public.query_risk, name='optimizer_query_risk'),
  re_path(r'^optimizer/predict/?$', api_public.predict, name='optimizer_predict'),
  re_path(r'^optimizer/query_compatibility/?$', api_public.query_compatibility, name='optimizer_query_compatibility'),
  re_path(r'^optimizer/similar_queries/?$', api_public.similar_queries, name='optimizer_similar_queries'),
]

urlpatterns += [
  re_path(r'^metadata/search/entities_interactive/?$', api_public.search_entities_interactive, name='metadata_entities_interactive'),
]

urlpatterns += [
  re_path(r'^iam/users/autocomplete', api_public.list_for_autocomplete, name='iam_users_list_for_autocomplete'),
  re_path(r'^iam/users/?$', api_public.get_users_by_id, name='iam_get_users_by_id'),
  re_path(r'^iam/get_users/?', api_public.get_users, name='iam_get_users'),
]
