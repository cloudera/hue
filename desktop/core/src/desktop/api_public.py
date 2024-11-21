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

import json
import logging

from django.http import HttpResponse, QueryDict
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from beeswax import api as beeswax_api
from desktop import api2 as desktop_api
from desktop.auth.backend import rewrite_user
from desktop.lib import fsmanager
from desktop.lib.connectors import api as connector_api
from filebrowser import api as filebrowser_api, views as filebrowser_views
from indexer import api3 as indexer_api3
from metadata import optimizer_api
from notebook import api as notebook_api
from notebook.conf import get_ordered_interpreters
from useradmin import api as useradmin_api, views as useradmin_views

LOG = logging.getLogger()


# Core


@api_view(["POST"])
def get_config(request):
  django_request = get_django_request(request)
  return desktop_api.get_config(django_request)


@api_view(["GET"])
def get_context_namespaces(request, interface):
  django_request = get_django_request(request)
  return desktop_api.get_context_namespaces(django_request, interface)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_banners(request):
  return desktop_api.get_banners(request)


# Editor


@api_view(["POST"])
def create_notebook(request):
  django_request = get_django_request(request)
  return notebook_api.create_notebook(django_request)


@api_view(["POST"])
def create_session(request):
  django_request = get_django_request(request)
  return notebook_api.create_session(django_request)


@api_view(["POST"])
def close_session(request):
  django_request = get_django_request(request)
  return notebook_api.close_session(django_request)


@api_view(["POST"])
def execute(request, dialect=None):
  django_request = get_django_request(request)

  if not request.POST.get('notebook'):
    interpreter = _get_interpreter_from_dialect(dialect=dialect, user=django_request.user)
    LOG.debug("API using interpreter: %(name)s %(dialect)s %(type)s" % interpreter)

    params = {
      'statement': django_request.POST.get('statement'),
      'interpreter': '%(type)s' % interpreter,
      # If connectors off, we expect a string
      'interpreter_id': ('%(type)s' if interpreter['type'].isdigit() else '"%(type)s"') % interpreter,
      'dialect': '%(dialect)s' % interpreter,
    }

    data = {
      'notebook': '{"type":"query-%(interpreter)s","snippets":[{"id":%(interpreter_id)s,"statement_raw":"",'
      '"type":"%(interpreter)s","status":"","variables":[],"properties":{}}],"name":"","isSaved":false,"sessions":[]}' % params,
      'snippet': '{"id":%(interpreter_id)s,"type":"%(interpreter)s","result":{},"statement":"%(statement)s","properties":{}}' % params,
    }

    # Optional database param for specific query statements like "show tables;"
    if django_request.POST.get('database'):
      database = django_request.POST.get('database')
      snippet = json.loads(data['snippet'])
      snippet['database'] = database

      data['snippet'] = json.dumps(snippet)

    django_request.POST = QueryDict(mutable=True)
    django_request.POST.update(data)

  return notebook_api.execute(django_request, dialect)


@api_view(["POST"])
def check_status(request):
  django_request = get_django_request(request)

  _patch_operation_id_request(django_request)

  return notebook_api.check_status(django_request)


@api_view(["POST"])
def fetch_result_data(request):
  django_request = get_django_request(request)

  _patch_operation_id_request(django_request)

  return notebook_api.fetch_result_data(django_request)


@api_view(["POST"])
def fetch_result_metadata(request):
  django_request = get_django_request(request)
  return notebook_api.fetch_result_metadata(django_request)


@api_view(["POST"])
def fetch_result_size(request):
  django_request = get_django_request(request)
  return notebook_api.fetch_result_size(django_request)


@api_view(["POST"])
def cancel_statement(request):
  django_request = get_django_request(request)
  return notebook_api.cancel_statement(django_request)


@api_view(["POST"])
def close_statement(request):
  django_request = get_django_request(request)
  return notebook_api.close_statement(django_request)


@api_view(["POST"])
def get_logs(request):
  django_request = get_django_request(request)

  _patch_operation_id_request(django_request)

  return notebook_api.get_logs(django_request)


@api_view(["POST"])
def get_sample_data(request, server=None, database=None, table=None, column=None, nested=None):
  django_request = get_django_request(request)

  _patch_operation_id_request(django_request)

  return notebook_api.get_sample_data(django_request, server, database, table, column, nested)


@api_view(["POST"])
def autocomplete(request, server=None, database=None, table=None, column=None, nested=None):
  django_request = get_django_request(request)

  _patch_operation_id_request(django_request)

  return notebook_api.autocomplete(django_request, server, database, table, column, nested)


@api_view(["POST"])
def describe(request, database, table=None, column=None):
  django_request = get_django_request(request)
  return notebook_api.describe(django_request, database, table, column)


@api_view(["GET"])
def get_history(request):
  django_request = get_django_request(request)
  return notebook_api.get_history(django_request)


@api_view(["POST"])
def analyze_table(request, dialect, database, table, columns=None):
  django_request = get_django_request(request)

  if dialect in ["impala", "beeswax"]:
    return beeswax_api.analyze_table(django_request, database, table, columns=None)
  else:
    return HttpResponse(status=204)


# Storage


@api_view(["GET"])
def storage_get_filesystems(request):
  django_request = get_django_request(request)
  return filebrowser_api.get_filesystems_with_home_dirs(django_request)


@api_view(["GET"])
def storage_view(request, path):
  django_request = get_django_request(request)
  return filebrowser_views.view(django_request, path)


@api_view(["GET"])
def storage_stat(request):
  django_request = get_django_request(request)
  return filebrowser_api.stat(django_request)


@api_view(["GET"])
def storage_listdir_paged(request):
  django_request = get_django_request(request)
  return filebrowser_api.listdir_paged(django_request)


@api_view(["GET"])
def storage_display(request):
  django_request = get_django_request(request)
  return filebrowser_api.display(django_request)


@api_view(["GET"])
def storage_download(request):
  django_request = get_django_request(request)
  return filebrowser_api.download(django_request)


@api_view(["POST"])
def storage_save_file(request):
  django_request = get_django_request(request)
  return filebrowser_api.save_file(django_request)


@api_view(["POST"])
def storage_upload_file(request):
  django_request = get_django_request(request)
  return filebrowser_api.upload_file(django_request)


@api_view(["POST"])
def storage_upload_chunks(request):
  django_request = get_django_request(request)
  return filebrowser_api.upload_chunks(django_request)


@api_view(["POST"])
def storage_upload_complete(request):
  django_request = get_django_request(request)
  return filebrowser_api.upload_complete(django_request)


@api_view(["POST"])
def storage_mkdir(request):
  django_request = get_django_request(request)
  return filebrowser_api.mkdir(django_request)


@api_view(["POST"])
def storage_touch(request):
  django_request = get_django_request(request)
  return filebrowser_api.touch(django_request)


@api_view(["POST"])
def storage_rename(request):
  django_request = get_django_request(request)
  return filebrowser_api.rename(django_request)


@api_view(["GET"])
def storage_content_summary(request):
  django_request = get_django_request(request)
  return filebrowser_api.content_summary(django_request)


@api_view(["POST"])
def storage_bulk_move(request):
  django_request = get_django_request(request)
  return filebrowser_api.bulk_op(django_request, filebrowser_api.move)


@api_view(["POST"])
def storage_move(request):
  django_request = get_django_request(request)
  return filebrowser_api.move(django_request)


@api_view(["POST"])
def storage_bulk_copy(request):
  django_request = get_django_request(request)
  return filebrowser_api.bulk_op(django_request, filebrowser_api.copy)


@api_view(["POST"])
def storage_copy(request):
  django_request = get_django_request(request)
  return filebrowser_api.copy(django_request)


@api_view(["POST"])
def storage_set_replication(request):
  django_request = get_django_request(request)
  return filebrowser_api.set_replication(django_request)


@api_view(["POST"])
def storage_rmtree(request):
  django_request = get_django_request(request)
  return filebrowser_api.rmtree(django_request)


@api_view(["POST"])
def storage_bulk_rmtree(request):
  django_request = get_django_request(request)
  return filebrowser_api.bulk_op(django_request, filebrowser_api.rmtree)


@api_view(["GET"])
def storage_get_trash_path(request):
  django_request = get_django_request(request)
  return filebrowser_api.get_trash_path(django_request)


@api_view(["POST"])
def storage_trash_restore(request):
  django_request = get_django_request(request)
  return filebrowser_api.trash_restore(django_request)


@api_view(["POST"])
def storage_trash_bulk_restore(request):
  django_request = get_django_request(request)
  return filebrowser_api.bulk_op(django_request, filebrowser_api.trash_restore)


@api_view(["DELETE"])
def storage_trash_purge(request):
  django_request = get_django_request(request)
  return filebrowser_api.trash_purge(django_request)


@api_view(["POST"])
def storage_compress_files_using_batch_job(request):
  django_request = get_django_request(request)
  return filebrowser_api.compress_files_using_batch_job(django_request)


@api_view(["POST"])
def storage_extract_archive_using_batch_job(request):
  django_request = get_django_request(request)
  return filebrowser_api.extract_archive_using_batch_job(django_request)


@api_view(["POST"])
def storage_chown(request):
  django_request = get_django_request(request)
  return filebrowser_api.chown(django_request)


@api_view(["POST"])
def storage_chmod(request):
  django_request = get_django_request(request)
  return filebrowser_api.chmod(django_request)


@api_view(["POST"])
def storage_bulk_chown(request):
  django_request = get_django_request(request)
  return filebrowser_api.bulk_op(django_request, filebrowser_api.chown)


@api_view(["POST"])
def storage_bulk_chmod(request):
  django_request = get_django_request(request)
  return filebrowser_api.bulk_op(django_request, filebrowser_api.chmod)


# Task Server


@api_view(["GET"])
def taskserver_get_available_space_for_upload(request):
  django_request = get_django_request(request)
  return filebrowser_api.get_available_space_for_upload(django_request)


# Importer


@api_view(["POST"])
def guess_format(request):
  django_request = get_django_request(request)
  return indexer_api3.guess_format(django_request)


@api_view(["POST"])
def guess_field_types(request):
  django_request = get_django_request(request)
  return indexer_api3.guess_field_types(django_request)


@api_view(["POST"])
def importer_submit(request):
  django_request = get_django_request(request)
  return indexer_api3.importer_submit(django_request)


# Connector


@api_view(["GET"])
def get_connector_types(request):
  django_request = get_django_request(request)
  return connector_api.get_connector_types(django_request)


@api_view(["GET"])
def get_connectors_instances(request):
  django_request = get_django_request(request)
  return connector_api.get_connectors_instances(django_request)


@api_view(["POST"])
def new_connector(request, dialect, interface):
  django_request = get_django_request(request)
  return connector_api.new_connector(django_request, dialect, interface)


@api_view(["GET"])
def get_connector(request, id):
  django_request = get_django_request(request)
  return connector_api.get_connector(django_request, id)


@api_view(["POST"])
def update_connector(request):
  django_request = get_django_request(request)
  return connector_api.update_connector(django_request)


@api_view(["POST"])
def delete_connector(request):
  django_request = get_django_request(request)
  return connector_api.delete_connector(django_request)


@api_view(["POST"])
def test_connector(request):
  django_request = get_django_request(request)
  return connector_api.test_connector(django_request)


@api_view(["POST"])
def install_connector_examples(request):
  django_request = get_django_request(request)
  return connector_api.install_connector_examples(django_request)


# Metadata


@api_view(["POST"])
def predict(request):
  django_request = get_django_request(request)
  return optimizer_api.predict(django_request)


@api_view(["POST"])
def query_risk(request):
  django_request = get_django_request(request)
  return optimizer_api.query_risk(django_request)


@api_view(["POST"])
def query_compatibility(request):
  django_request = get_django_request(request)
  return optimizer_api.query_compatibility(django_request)


@api_view(["POST"])
def similar_queries(request):
  django_request = get_django_request(request)
  return optimizer_api.similar_queries(django_request)


@api_view(["POST"])
def top_databases(request):
  django_request = get_django_request(request)
  return optimizer_api.top_databases(django_request)


@api_view(["POST"])
def top_tables(request):
  django_request = get_django_request(request)
  return optimizer_api.top_tables(django_request)


@api_view(["POST"])
def top_columns(request):
  django_request = get_django_request(request)
  return optimizer_api.top_columns(django_request)


@api_view(["POST"])
def top_joins(request):
  django_request = get_django_request(request)
  return optimizer_api.top_joins(django_request)


@api_view(["POST"])
def top_filters(request):
  django_request = get_django_request(request)
  return optimizer_api.top_filters(django_request)


@api_view(["POST"])
def top_aggs(request):
  django_request = get_django_request(request)
  return optimizer_api.top_aggs(django_request)


@api_view(["POST"])
def search_entities_interactive(request):
  django_request = get_django_request(request)
  return desktop_api.search_entities_interactive(django_request)


# IAM


@api_view(["GET"])
def list_for_autocomplete(request):
  django_request = get_django_request(request)
  return useradmin_views.list_for_autocomplete(django_request)


@api_view(["GET"])
def get_users_by_id(request):
  django_request = get_django_request(request)
  return useradmin_views.get_users_by_id(django_request)


@api_view(["GET"])
def get_users(request):
  django_request = get_django_request(request)
  return useradmin_api.get_users(django_request)


# Utils


def _get_interpreter_from_dialect(dialect, user):
  if not dialect:
    interpreter = get_ordered_interpreters(user=user)[0]
  elif '-' in dialect:
    interpreter = {
      'dialect': dialect.split('-')[0],
      'type': dialect.split('-')[1],  # Id
    }
  else:
    interpreter = [i for i in get_ordered_interpreters(user=user) if i['dialect'] == dialect][0]

  return interpreter


def _patch_operation_id_request(django_request):
  data = {}

  if not django_request.POST.get('snippet'):
    data['snippet'] = '{"type":"1","result":{}}'

  django_request.POST = django_request.POST.copy()  # Makes it mutable along with copying the object
  django_request.POST.update(data)


def get_django_request(request):
  django_request = request._request

  django_request.user = rewrite_user(django_request.user)

  # Workaround ClusterMiddleware not being applied
  if django_request.path.startswith('/api/') and django_request.fs is None:
    django_request.fs = fsmanager.get_filesystem(django_request.fs_ref)

    if django_request.user.is_authenticated and django_request.fs is not None:
      django_request.fs.setuser(django_request.user.username)

  return django_request
