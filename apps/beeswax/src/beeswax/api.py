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

from builtins import str
from builtins import zip
import logging
import json
import re

from django.contrib.auth.models import User
from django.urls import reverse
from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from thrift.transport.TTransport import TTransportException
from desktop.context_processors import get_app_name
from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions import StructuredThriftTransportException
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode
from desktop.lib.parameterization import substitute_variables
from metastore import parser
from notebook.models import escape_rows, MockedDjangoRequest, make_notebook

import beeswax.models

from beeswax.data_export import upload
from beeswax.design import HQLdesign
from beeswax.conf import USE_GET_LOG_API
from beeswax.forms import QueryForm
from beeswax.models import Session, QueryHistory
from beeswax.server import dbms
from beeswax.server.dbms import expand_exception, get_query_server_config, QueryServerException, QueryServerTimeoutException,\
  SubQueryTable
from beeswax.views import authorized_get_design, authorized_get_query_history, make_parameterization_form,\
                          safe_get_design, save_design, massage_columns_for_json, _get_query_handle_and_state, \
                          parse_out_jobs
from metastore.conf import FORCE_HS2_METADATA
from metastore.views import _get_db, _get_servername

from desktop.auth.backend import is_admin

LOG = logging.getLogger(__name__)


def error_handler(view_fn):
  def decorator(request, *args, **kwargs):
    try:
      return view_fn(request, *args, **kwargs)
    except Http404 as e:
      raise e
    except Exception as e:
      LOG.exception('error in %s' % view_fn)

      if not hasattr(e, 'message') or not e.message:
        message = str(e)
      else:
        message = force_unicode(e.message, strings_only=True, errors='replace')

        if 'Invalid OperationHandle' in message and 'id' in kwargs:
          # Expired state.
          query_history = authorized_get_query_history(request, kwargs['id'], must_exist=False)
          if query_history:
            query_history.set_to_expired()
            query_history.save()

      response = {
        'status': -1,
        'message': message,
      }

      if re.search('database is locked|Invalid query handle|not JSON serializable', message, re.IGNORECASE):
        response['status'] = 2 # Frontend will not display this type of error
        LOG.warn('error_handler silencing the exception: %s' % e)
      return JsonResponse(response)
  return decorator


@error_handler
def autocomplete(request, database=None, table=None, column=None, nested=None):
  cluster = request.POST.get('cluster')
  app_name = None if FORCE_HS2_METADATA.get() else get_app_name(request)

  do_as = request.user
  if (is_admin(request.user) or request.user.has_hue_permission(action="impersonate", app="security")) and 'doas' in request.GET:
    do_as = User.objects.get(username=request.GET.get('doas'))

  db = _get_db(user=do_as, source_type=app_name, cluster=cluster)

  response = _autocomplete(db, database, table, column, nested, cluster=cluster)
  return JsonResponse(response)


def _autocomplete(db, database=None, table=None, column=None, nested=None, query=None, cluster=None):
  response = {}

  try:
    if database is None:
      response['databases'] = db.get_databases()
    elif table is None:
      tables_meta = db.get_tables_meta(database=database)
      response['tables_meta'] = tables_meta
    elif column is None:
      if query is not None:
        table = SubQueryTable(db, query)
      else:
        table = db.get_table(database, table)
      response['hdfs_link'] = table.hdfs_link
      response['comment'] = table.comment

      cols_extended = massage_columns_for_json(table.cols)

      if table.is_impala_only:
        if db.client.query_server['server_name'] != 'impala': # Expand Kudu columns information
          query_server = get_query_server_config('impala', cluster=cluster)
          db = dbms.get(db.client.user, query_server, cluster=cluster)

        col_options = db.get_table_describe(database, table.name)
        extra_col_options = dict([(col[0], dict(list(zip(col_options.cols(), col)))) for col in col_options.rows()])

        for col_props in cols_extended:
          col_props.update(extra_col_options.get(col_props['name'], {}))

      response['support_updates'] = table.is_impala_only
      response['columns'] = [column.name for column in table.cols]
      response['extended_columns'] = cols_extended
      response['is_view'] = table.is_view
      response['partition_keys'] = [{'name': part.name, 'type': part.type} for part in table.partition_keys]
    else:
      col = db.get_column(database, table, column)
      if col:
        parse_tree = parser.parse_column(col.name, col.type, col.comment)
        if nested:
          parse_tree = _extract_nested_type(parse_tree, nested)
        response = parse_tree
        # If column or nested type is scalar/primitive, add sample of values
        if parser.is_scalar_type(parse_tree['type']):
          sample = _get_sample_data(db, database, table, column, cluster=cluster)
          if 'rows' in sample:
            response['sample'] = sample['rows']
      else:
        raise Exception('Could not find column `%s`.`%s`.`%s`' % (database, table, column))
  except (QueryServerTimeoutException, TTransportException) as e:
    response['code'] = 503
    response['error'] = e.message
  except Exception as e:
    LOG.warn('Autocomplete data fetching error: %s' % e)
    response['code'] = 500
    response['error'] = e.message

  return response


@error_handler
def parameters(request, design_id=None):
  response = {'status': -1, 'message': ''}

  # Use POST request to not confine query length.
  if request.method != 'POST':
    response['message'] = _('A POST request is required.')

  parameterization_form_cls = make_parameterization_form(request.POST.get('query-query', ''))
  if parameterization_form_cls:
    parameterization_form = parameterization_form_cls(prefix="parameterization")

    response['parameters'] = [{'parameter': field.html_name, 'name': field.name} for field in parameterization_form]
    response['status']= 0
  else:
    response['parameters'] = []
    response['status']= 0

  return JsonResponse(response)


@error_handler
def execute_directly(request, query, design, query_server, tablename=None, **kwargs):
  if design is not None:
    design = authorized_get_design(request, design.id)
  parameters = kwargs.pop('parameters', None)

  db = dbms.get(request.user, query_server)
  database = query.query.get('database', 'default')
  db.use(database)

  history_obj = db.execute_query(query, design)
  watch_url = reverse(get_app_name(request) + ':api_watch_query_refresh_json', kwargs={'id': history_obj.id})

  if parameters is not None:
    history_obj.update_extra('parameters', parameters)
    history_obj.save()

  response = {
    'status': 0,
    'id': history_obj.id,
    'watch_url': watch_url,
    'statement': history_obj.get_current_statement(),
    'is_redacted': history_obj.is_redacted
  }

  return JsonResponse(response)


@error_handler
def watch_query_refresh_json(request, id):
  query_history = authorized_get_query_history(request, id, must_exist=True)
  db = dbms.get(request.user, query_history.get_query_server_config())

  if not request.POST.get('next'): # We need this as multi query would fail as current query is closed
    handle, state = _get_query_handle_and_state(query_history)
    query_history.save_state(state)

  # Go to next statement if asked to continue or when a statement with no dataset finished.
  try:
    if request.POST.get('next') or (not query_history.is_finished() and query_history.is_success() and not query_history.has_results):
      close_operation(request, id)
      query_history = db.execute_next_statement(query_history, request.POST.get('query-query'))
      handle, state = _get_query_handle_and_state(query_history)
  except QueryServerException as ex:
    raise ex
  except Exception as ex:
    LOG.exception(ex)
    handle, state = _get_query_handle_and_state(query_history)

  try:
    start_over = request.POST.get('log-start-over') == 'true'
    log = db.get_log(handle, start_over=start_over)
  except Exception as ex:
    log = str(ex)

  jobs = parse_out_jobs(log)
  job_urls = massage_job_urls_for_json(jobs)

  result = {
    'status': -1,
    'log': log,
    'jobs': jobs,
    'jobUrls': job_urls,
    'isSuccess': query_history.is_success(),
    'isFailure': query_history.is_failure(),
    'id': id,
    'statement': query_history.get_current_statement(),
    'watch_url': reverse(get_app_name(request) + ':api_watch_query_refresh_json', kwargs={'id': query_history.id}),
    'oldLogsApi': USE_GET_LOG_API.get()
  }

  # Run time error
  if query_history.is_failure():
    res = db.get_operation_status(handle)
    if query_history.is_canceled(res):
      result['status'] = 0
    elif hasattr(res, 'errorMessage') and res.errorMessage:
      result['message'] = res.errorMessage
    else:
      result['message'] = _('Bad status for request %s:\n%s') % (id, res)
  else:
    result['status'] = 0

  return JsonResponse(result)


def massage_job_urls_for_json(jobs):
  massaged_jobs = []
  for job in jobs:
    massaged_jobs.append({
      'name': job,
      'url': reverse('jobbrowser.views.single_job', kwargs={'job': job})
    })
  return massaged_jobs


@error_handler
def close_operation(request, query_history_id):
  response = {
    'status': -1,
    'message': ''
  }

  if request.method != 'POST':
    response['message'] = _('A POST request is required.')
  else:
    query_history = authorized_get_query_history(request, query_history_id, must_exist=True)
    db = dbms.get(query_history.owner, query_history.get_query_server_config())
    handle = query_history.get_handle()
    db.close_operation(handle)
    query_history.set_to_expired()
    query_history.save()
    response['status'] = 0

  return JsonResponse(response)


@error_handler
def explain_directly(request, query_server, query):
  explanation = dbms.get(request.user, query_server).explain(query)

  response = {
    'status': 0,
    'explanation': explanation.textual,
    'statement': query.get_query_statement(0),
  }

  return JsonResponse(response)


@error_handler
def execute(request, design_id=None):
  response = {'status': -1, 'message': ''}

  if request.method != 'POST':
    response['message'] = _('A POST request is required.')

  app_name = get_app_name(request)
  query_server = get_query_server_config(app_name)
  query_type = beeswax.models.SavedQuery.TYPES_MAPPING[app_name]
  design = safe_get_design(request, query_type, design_id)

  try:
    query_form = get_query_form(request)

    if query_form.is_valid():
      query_str = query_form.query.cleaned_data["query"]
      explain = request.GET.get('explain', 'false').lower() == 'true'
      design = save_design(request, query_form, query_type, design, False)

      if query_form.query.cleaned_data['is_parameterized']:
        # Parameterized query
        parameterization_form_cls = make_parameterization_form(query_str)
        if parameterization_form_cls:
          parameterization_form = parameterization_form_cls(request.POST.get('query-query', ''), prefix="parameterization")

          if parameterization_form.is_valid():
            parameters = parameterization_form.cleaned_data
            real_query = substitute_variables(query_str, parameters)
            query = HQLdesign(query_form, query_type=query_type)
            query._data_dict['query']['query'] = real_query

            try:
              if explain:
                return explain_directly(request, query_server, query)
              else:
                return execute_directly(request, query, design, query_server, parameters=parameters)

            except Exception as ex:
              db = dbms.get(request.user, query_server)
              error_message, log = expand_exception(ex, db)
              response['message'] = error_message
              return JsonResponse(response)
          else:
            response['errors'] = parameterization_form.errors
            return JsonResponse(response)

      # Non-parameterized query
      query = HQLdesign(query_form, query_type=query_type)
      if request.GET.get('explain', 'false').lower() == 'true':
        return explain_directly(request, query_server, query)
      else:
        return execute_directly(request, query, design, query_server)
    else:
      response['message'] = _('There was an error with your query.')
      response['errors'] = {
        'query': [query_form.query.errors],
        'settings': query_form.settings.errors,
        'file_resources': query_form.file_resources.errors,
        'functions': query_form.functions.errors,
      }
  except RuntimeError as e:
    response['message']= str(e)

  return JsonResponse(response)


@error_handler
def save_query_design(request, design_id=None):
  response = {'status': -1, 'message': ''}

  if request.method != 'POST':
    response['message'] = _('A POST request is required.')

  app_name = get_app_name(request)
  query_type = beeswax.models.SavedQuery.TYPES_MAPPING[app_name]
  design = safe_get_design(request, query_type, design_id)

  try:
    query_form = get_query_form(request)

    if query_form.is_valid():
      design = save_design(request, query_form, query_type, design, True)
      response['design_id'] = design.id
      response['status'] = 0
    else:
      response['errors'] = {
        'query': [query_form.query.errors],
        'settings': query_form.settings.errors,
        'file_resources': query_form.file_resources.errors,
        'functions': query_form.functions.errors,
        'saveform': query_form.saveform.errors,
      }
  except RuntimeError as e:
    response['message'] = str(e)

  return JsonResponse(response)


@error_handler
def fetch_saved_design(request, design_id):
  response = {'status': 0, 'message': ''}

  if request.method != 'GET':
    response['message'] = _('A GET request is required.')

  app_name = get_app_name(request)
  query_type = beeswax.models.SavedQuery.TYPES_MAPPING[app_name]
  design = safe_get_design(request, query_type, design_id)

  response['design'] = design_to_dict(design)
  return JsonResponse(response)


@error_handler
def fetch_query_history(request, query_history_id):
  response = {'status': 0, 'message': ''}

  if request.method != 'GET':
    response['message'] = _('A GET request is required.')

  query = authorized_get_query_history(request, query_history_id, must_exist=True)

  response['query_history'] = query_history_to_dict(request, query)
  return JsonResponse(response)


@error_handler
def cancel_query(request, query_history_id):
  response = {'status': -1, 'message': ''}

  if request.method != 'POST':
    response['message'] = _('A POST request is required.')
  else:
    try:
      query_history = authorized_get_query_history(request, query_history_id, must_exist=True)
      db = dbms.get(request.user, query_history.get_query_server_config())
      db.cancel_operation(query_history.get_handle())
      query_history.set_to_expired()
      response['status'] = 0
    except Exception as e:
      response['message'] = str(e)

  return JsonResponse(response)


@error_handler
def save_results_hdfs_directory(request, query_history_id):
  """
  Save the results of a query to an HDFS directory.

  Rerun the query.
  """
  response = {'status': 0, 'message': ''}

  query_history = authorized_get_query_history(request, query_history_id, must_exist=True)
  server_id, state = _get_query_handle_and_state(query_history)
  query_history.save_state(state)
  error_msg, log = None, None

  if request.method != 'POST':
    response['message'] = _('A POST request is required.')
  else:
    if not query_history.is_success():
      response['message'] = _('This query is %(state)s. Results unavailable.') % {'state': state}
      response['status'] = -1
      return JsonResponse(response)

    db = dbms.get(request.user, query_history.get_query_server_config())

    form = beeswax.forms.SaveResultsDirectoryForm({
      'target_dir': request.POST.get('path')
    }, fs=request.fs)

    if form.is_valid():
      target_dir = request.POST.get('path')
      try:
        response['type'] = 'hdfs-dir'
        response['id'] = query_history.id
        response['query'] = query_history.query
        response['path'] = target_dir
        response['success_url'] = '/filebrowser/view=%s' % target_dir
        query_history = db.insert_query_into_directory(query_history, target_dir)
        response['watch_url'] = reverse(get_app_name(request) + ':api_watch_query_refresh_json', kwargs={'id': query_history.id})
      except Exception as ex:
        error_msg, log = expand_exception(ex, db)
        response['message'] = _('The result could not be saved: %s.') % error_msg
        response['status'] = -3
    else:
      response['status'] = 1
      response['errors'] = form.errors

  return JsonResponse(response)


@error_handler
def save_results_hdfs_file(request, query_history_id):
  """
  Save the results of a query to an HDFS file.

  Do not rerun the query.
  """
  response = {'status': 0, 'message': ''}

  query_history = authorized_get_query_history(request, query_history_id, must_exist=True)
  server_id, state = _get_query_handle_and_state(query_history)
  query_history.save_state(state)
  error_msg, log = None, None

  if request.method != 'POST':
    response['message'] = _('A POST request is required.')
  else:
    if not query_history.is_success():
      response['message'] = _('This query is %(state)s. Results unavailable.') % {'state': state}
      response['status'] = -1
      return JsonResponse(response)

    db = dbms.get(request.user, query_history.get_query_server_config())

    form = beeswax.forms.SaveResultsFileForm({
      'target_file': request.POST.get('path'),
      'overwrite': request.POST.get('overwrite', False),
    })

    if form.is_valid():
      target_file = form.cleaned_data['target_file']
      overwrite = form.cleaned_data['overwrite']

      try:
        handle, state = _get_query_handle_and_state(query_history)
      except Exception as ex:
        response['message'] = _('Cannot find query handle and state: %s') % str(query_history)
        response['status'] = -2
        return JsonResponse(response)

      try:
        if overwrite and request.fs.exists(target_file):
          if request.fs.isfile(target_file):
            request.fs.do_as_user(request.user.username, request.fs.rmtree, target_file)
          else:
            raise PopupException(_("The target path is a directory"))

        upload(target_file, handle, request.user, db, request.fs)

        response['type'] = 'hdfs-file'
        response['id'] = query_history.id
        response['query'] = query_history.query
        response['path'] = target_file
        response['success_url'] = '/filebrowser/view=%s' % target_file
        response['watch_url'] = reverse(get_app_name(request) + ':api_watch_query_refresh_json', kwargs={'id': query_history.id})
      except Exception as ex:
        error_msg, log = expand_exception(ex, db)
        response['message'] = _('The result could not be saved: %s.') % error_msg
        response['status'] = -3
    else:
      response['status'] = 1
      response['errors'] = form.errors

  return JsonResponse(response)


@error_handler
def save_results_hive_table(request, query_history_id):
  """
  Save the results of a query to a hive table.

  Rerun the query.
  """
  response = {'status': 0, 'message': ''}

  query_history = authorized_get_query_history(request, query_history_id, must_exist=True)
  server_id, state = _get_query_handle_and_state(query_history)
  query_history.save_state(state)
  error_msg, log = None, None

  if request.method != 'POST':
    response['message'] = _('A POST request is required.')
  else:
    if not query_history.is_success():
      response['message'] = _('This query is %(state)s. Results unavailable.') % {'state': state}
      response['status'] = -1
      return JsonResponse(response)

    db = dbms.get(request.user, query_history.get_query_server_config())
    database = query_history.design.get_design().query.get('database', 'default')
    form = beeswax.forms.SaveResultsTableForm({
      'target_table': request.POST.get('table')
    }, db=db, database=database)

    if form.is_valid():
      try:
        handle, state = _get_query_handle_and_state(query_history)
        result_meta = db.get_results_metadata(handle)
      except Exception as ex:
        response['message'] = _('Cannot find query handle and state: %s') % str(query_history)
        response['status'] = -2
        return JsonResponse(response)

      try:
        query_history = db.create_table_as_a_select(request, query_history, form.target_database, form.cleaned_data['target_table'], result_meta)
        response['id'] = query_history.id
        response['query'] = query_history.query
        response['type'] = 'hive-table'
        response['path'] = form.cleaned_data['target_table']
        response['success_url'] = reverse('metastore:describe_table', kwargs={'database': form.target_database, 'table': form.cleaned_data['target_table']})
        response['watch_url'] = reverse(get_app_name(request) + ':api_watch_query_refresh_json', kwargs={'id': query_history.id})
      except Exception as ex:
        error_msg, log = expand_exception(ex, db)
        response['message'] = _('The result could not be saved: %s.') % error_msg
        response['status'] = -3

    else:
      response['status'] = 1
      response['message'] = '\n'.join(list(form.errors.values())[0])

  return JsonResponse(response)


@error_handler
def clear_history(request):
  response = {'status': -1, 'message': ''}

  if request.method != 'POST':
    response['message'] = _('A POST request is required.')
  else:
    response['count'] = QueryHistory.objects.filter(owner=request.user, is_cleared=False).update(is_cleared=True)
    response['status'] = 0

  return JsonResponse(response)


@error_handler
def get_sample_data(request, database, table, column=None):
  app_name = get_app_name(request)
  cluster = json.loads(request.POST.get('cluster', '{}'))

  query_server = get_query_server_config(app_name, cluster=cluster)
  db = dbms.get(request.user, query_server)

  response = _get_sample_data(db, database, table, column, cluster=cluster)
  return JsonResponse(response)


def _get_sample_data(db, database, table, column, async=False, cluster=None, operation=None):
  table_obj = db.get_table(database, table)
  if table_obj.is_impala_only and db.client.query_server['server_name'] != 'impala':
    query_server = get_query_server_config('impala', cluster=cluster)
    db = dbms.get(db.client.user, query_server, cluster=cluster)

  sample_data = db.get_sample(database, table_obj, column, generate_sql_only=async, operation=operation)
  response = {'status': -1}

  if sample_data:
    response['status'] = 0
    if async:
      notebook = make_notebook(
          name=_('Table sample for `%(database)s`.`%(table)s`.`%(column)s`') % {'database': database, 'table': table, 'column': column},
          editor_type=_get_servername(db),
          statement=sample_data,
          status='ready-execute',
          skip_historify=True,
          is_task=False,
          compute=cluster if cluster else None
      )
      response['result'] = notebook.execute(request=MockedDjangoRequest(user=db.client.user), batch=False)
      if table_obj.is_impala_only:
        response['result']['type'] = 'impala'
    else:
      sample = escape_rows(sample_data.rows(), nulls_only=True)
      if column:
        sample = set([row[0] for row in sample])
        sample = [[item] for item in sorted(list(sample))]

      response['headers'] = sample_data.cols()
      response['full_headers'] = sample_data.full_cols()
      response['rows'] = sample
  else:
    response['message'] = _('Failed to get sample data.')

  return response


@error_handler
def get_indexes(request, database, table):
  query_server = dbms.get_query_server_config(get_app_name(request))
  db = dbms.get(request.user, query_server)
  response = {'status': -1}

  indexes = db.get_indexes(database, table)
  if indexes:
    response['status'] = 0
    response['headers'] = indexes.cols()
    response['rows'] = escape_rows(indexes.rows(), nulls_only=True)
  else:
    response['message'] = _('Failed to get indexes.')

  return JsonResponse(response)


@error_handler
def get_settings(request):
  query_server = dbms.get_query_server_config(get_app_name(request))
  db = dbms.get(request.user, query_server)
  response = {'status': -1}

  settings = db.get_configuration()
  if settings:
    response['status'] = 0
    response['settings'] = settings
  else:
    response['message'] = _('Failed to get settings.')

  return JsonResponse(response)


@error_handler
def get_functions(request):
  query_server = dbms.get_query_server_config(get_app_name(request))
  db = dbms.get(request.user, query_server)
  response = {'status': -1}

  prefix = request.GET.get('prefix', None)
  functions = db.get_functions(prefix)
  if functions:
    response['status'] = 0
    rows = escape_rows(functions.rows(), nulls_only=True)
    response['functions'] = [row[0] for row in rows]
  else:
    response['message'] = _('Failed to get functions.')

  return JsonResponse(response)


@error_handler
def analyze_table(request, database, table, columns=None):
  app_name = get_app_name(request)
  cluster = json.loads(request.POST.get('cluster', '{}'))

  query_server = get_query_server_config(app_name, cluster=cluster)
  db = dbms.get(request.user, query_server)

  table_obj = db.get_table(database, table)
  if table_obj.is_impala_only and app_name != 'impala':
    query_server = get_query_server_config('impala')
    db = dbms.get(request.user, query_server)

  response = {'status': -1, 'message': '', 'redirect': ''}

  if request.method == "POST":
    if columns is None:
      query_history = db.analyze_table(database, table)
    else:
      query_history = db.analyze_table_columns(database, table)

    response['watch_url'] = reverse('beeswax:api_watch_query_refresh_json', kwargs={'id': query_history.id})
    response['status'] = 0
  else:
    response['message'] = _('A POST request is required.')

  return JsonResponse(response)


@error_handler
def get_table_stats(request, database, table, column=None):
  app_name = get_app_name(request)
  cluster = json.loads(request.POST.get('cluster', '{}'))

  query_server = get_query_server_config(app_name, cluster=cluster)
  db = dbms.get(request.user, query_server)

  response = {'status': -1, 'message': '', 'redirect': ''}

  if column is not None:
    stats = db.get_table_columns_stats(database, table, column)
  else:
    table = db.get_table(database, table)
    stats = table.stats
    response['columns'] = [column.name for column in table.cols]

  response['stats'] = stats
  response['status'] = 0

  return JsonResponse(response)


@error_handler
def get_top_terms(request, database, table, column, prefix=None):
  app_name = get_app_name(request)
  cluster = json.loads(request.POST.get('cluster', '{}'))

  query_server = get_query_server_config(app_name, cluster=cluster)
  db = dbms.get(request.user, query_server)

  response = {'status': -1, 'message': '', 'redirect': ''}

  terms = db.get_top_terms(database, table, column, prefix=prefix, limit=int(request.GET.get('limit', 30)))

  response['terms'] = terms
  response['status'] = 0

  return JsonResponse(response)


@error_handler
def get_session(request, session_id=None):
  app_name = get_app_name(request)
  query_server = get_query_server_config(app_name)

  response = {'status': -1, 'message': ''}

  if session_id:
    session = Session.objects.get(id=session_id, owner=request.user, application=query_server['server_name'])
  else:  # get the latest session for given user and server type
    session = Session.objects.get_session(request.user, query_server['server_name'])

  if session is not None:
    properties = json.loads(session.properties)
    # Redact passwords
    for key, value in list(properties.items()):
      if 'password' in key.lower():
        properties[key] = '*' * len(value)

    response['status'] = 0
    response['session'] = {'id': session.id, 'application': session.application, 'status': session.status_code}
    response['properties'] = properties
  else:
    response['message'] = _('Could not find session or no open sessions found.')

  return JsonResponse(response)


@require_POST
@error_handler
def close_session(request, session_id):
  app_name = get_app_name(request)
  query_server = get_query_server_config(app_name)

  response = {'status': -1, 'message': ''}

  try:
    filters = {'id': session_id, 'application': query_server['server_name']}
    if not is_admin(request.user):
      filters['owner'] = request.user
    session = Session.objects.get(**filters)
  except Session.DoesNotExist:
    response['message'] = _('Session does not exist or you do not have permissions to close the session.')

  if session:
    session = dbms.get(request.user, query_server).close_session(session)
    response['status'] = 0
    response['message'] = _('Session successfully closed.')
    response['session'] = {'id': session_id, 'application': session.application, 'status': session.status_code}

  return JsonResponse(response)


# Proxy API for Metastore App
def describe_table(request, database, table):
  try:
    from metastore.views import describe_table as metastore_describe_table
    return metastore_describe_table(request, database, table)
  except Exception as e:
    LOG.exception('Describe table failed')
    raise PopupException(_('Problem accessing table metadata'), detail=e)


def design_to_dict(design):
  hql_design = HQLdesign.loads(design.data)
  return {
    'id': design.id,
    'query': hql_design.hql_query,
    'name': design.name,
    'desc': design.desc,
    'database': hql_design.query.get('database', None),
    'settings': hql_design.settings,
    'file_resources': hql_design.file_resources,
    'functions': hql_design.functions,
    'is_parameterized': hql_design.query.get('is_parameterized', True),
    'email_notify': hql_design.query.get('email_notify', True),
    'is_redacted': design.is_redacted
  }


def query_history_to_dict(request, query_history):
  query_history_dict = {
    'id': query_history.id,
    'state': query_history.last_state,
    'query': query_history.query,
    'has_results': query_history.has_results,
    'statement_number': query_history.statement_number,
    'watch_url': reverse(get_app_name(request) + ':api_watch_query_refresh_json', kwargs={'id': query_history.id}),
    'results_url': reverse(get_app_name(request) + ':view_results', kwargs={'id': query_history.id, 'first_row': 0})
  }

  if query_history.design:
    query_history_dict['design'] = design_to_dict(query_history.design)

  return query_history_dict


def get_query_form(request):
  try:
    try:
      # Get database choices
      query_server = dbms.get_query_server_config(get_app_name(request))
      db = dbms.get(request.user, query_server)
      databases = [(database, database) for database in db.get_databases()]
    except StructuredThriftTransportException as e:
      # If Thrift exception was due to failed authentication, raise corresponding message
      if 'TSocket read 0 bytes' in str(e) or 'Error validating the login' in str(e):
        raise PopupException(_('Failed to authenticate to query server, check authentication configurations.'), detail=e)
      else:
        raise e
  except Exception as e:
    raise PopupException(_('Unable to access databases, Query Server or Metastore may be down.'), detail=e)

  if not databases:
    raise RuntimeError(_("No databases are available. Permissions could be missing."))

  query_form = QueryForm()
  query_form.bind(request.POST)
  query_form.query.fields['database'].choices = databases # Could not do it in the form

  return query_form


"""
Utils
"""
def _extract_nested_type(parse_tree, nested_path):
  nested_tokens = nested_path.strip('/').split('/')

  subtree = parse_tree

  for token in nested_tokens:
    if token in subtree:
      subtree = subtree[token]
    elif 'fields' in subtree:
      for field in subtree['fields']:
        if field['name'] == token:
          subtree = field
          break
    else:
      raise Exception('Invalid nested type path: %s' % nested_path)

  return subtree
