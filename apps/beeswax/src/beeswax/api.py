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
import re

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext as _

from thrift.transport.TTransport import TTransportException
from desktop.context_processors import get_app_name
from desktop.lib.i18n import force_unicode
from desktop.lib.exceptions_renderable import PopupException
from jobsub.parameterization import substitute_variables

import beeswax.models

from beeswax.forms import QueryForm
from beeswax.data_export import upload
from beeswax.design import HQLdesign
from beeswax.conf import USE_GET_LOG_API
from beeswax.server import dbms
from beeswax.server.dbms import expand_exception, get_query_server_config, QueryServerException
from beeswax.views import authorized_get_design, authorized_get_query_history, make_parameterization_form,\
                          safe_get_design, save_design, massage_columns_for_json, _get_query_handle_and_state,\
                          _parse_out_hadoop_jobs


LOG = logging.getLogger(__name__)


def error_handler(view_fn):
  def decorator(request, *args, **kwargs):
    try:
      return view_fn(request, *args, **kwargs)
    except Http404, e:
      raise e
    except Exception, e:
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

      return HttpResponse(json.dumps(response), mimetype="application/json", status=200)
  return decorator


@error_handler
def autocomplete(request, database=None, table=None):
  app_name = get_app_name(request)
  query_server = get_query_server_config(app_name)
  do_as = request.user
  if (request.user.is_superuser or request.user.has_hue_permission(action="impersonate", app="security")) and 'doas' in request.GET:
    do_as = User.objects.get(username=request.GET.get('doas'))
  db = dbms.get(do_as, query_server)
  response = {}

  try:
    if database is None:
      response['databases'] = db.get_databases()
    elif table is None:
      response['tables'] = db.get_tables(database=database)
    else:
      t = db.get_table(database, table)
      response['hdfs_link'] = t.hdfs_link
      response['columns'] = [column.name for column in t.cols]
      response['extended_columns'] = massage_columns_for_json(t.cols)
  except TTransportException, tx:
    response['code'] = 503
    response['error'] = tx.message
  except Exception, e:
    LOG.warn('Autocomplete data fetching error %s.%s: %s' % (database, table, e))
    response['code'] = 500
    response['error'] = e.message

  return HttpResponse(json.dumps(response), mimetype="application/json")


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

  return HttpResponse(json.dumps(response), mimetype="application/json")


@error_handler
def execute_directly(request, query, design, query_server, tablename=None, **kwargs):
  if design is not None:
    design = authorized_get_design(request, design.id)

  db = dbms.get(request.user, query_server)
  database = query.query.get('database', 'default')
  db.use(database)

  history_obj = db.execute_query(query, design)
  watch_url = reverse(get_app_name(request) + ':api_watch_query_refresh_json', kwargs={'id': history_obj.id})

  response = {
    'status': 0,
    'id': history_obj.id,
    'watch_url': watch_url,
    'statement': history_obj.get_current_statement(),
    'is_redacted': history_obj.is_redacted
  }

  return HttpResponse(json.dumps(response), mimetype="application/json")


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
      query_history = db.execute_next_statement(query_history, request.POST.get('query-query'))
      handle, state = _get_query_handle_and_state(query_history)
  except QueryServerException, ex:
    raise ex
  except Exception, ex:
    LOG.exception(ex)
    handle, state = _get_query_handle_and_state(query_history)

  try:
    start_over = request.POST.get('log-start-over') == 'true'
    log = db.get_log(handle, start_over=start_over)
  except Exception, ex:
    log = str(ex)

  jobs = _parse_out_hadoop_jobs(log)
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

  return HttpResponse(json.dumps(result), mimetype="application/json")

def massage_job_urls_for_json(jobs):
  massaged_jobs = []
  for job in jobs:
    massaged_jobs.append({
      'name': job,
      'url': reverse('jobbrowser.views.single_job', kwargs={'job': job})
    })
  return massaged_jobs


def close_operation(request, query_history_id):
  response = {
    'status': -1,
    'message': ''
  }

  if request.method != 'POST':
    response['message'] = _('A POST request is required.')
  else:
    try:
      query_history = authorized_get_query_history(request, query_history_id, must_exist=True)
      db = dbms.get(query_history.owner, query_history.get_query_server_config())
      handle = query_history.get_handle()
      db.close_operation(handle)
      query_history.set_to_expired()
      query_history.save()
      response['status'] = 0
    except Exception, e:
      response['message'] = unicode(e)

  return HttpResponse(json.dumps(response), mimetype="application/json")


@error_handler
def explain_directly(request, query, design, query_server):
  explanation = dbms.get(request.user, query_server).explain(query)

  response = {
    'status': 0,
    'explanation': explanation.textual,
    'statement': query.get_query_statement(0),
  }

  return HttpResponse(json.dumps(response), mimetype="application/json")


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
          parameterization_form = parameterization_form_cls(request.REQUEST, prefix="parameterization")

          if parameterization_form.is_valid():
            real_query = substitute_variables(query_str, parameterization_form.cleaned_data)
            query = HQLdesign(query_form, query_type=query_type)
            query._data_dict['query']['query'] = real_query

            try:
              if explain:
                return explain_directly(request, query, design, query_server)
              else:
                return execute_directly(request, query, design, query_server)

            except Exception, ex:
              db = dbms.get(request.user, query_server)
              error_message, log = expand_exception(ex, db)
              response['message'] = error_message
              return HttpResponse(json.dumps(response), mimetype="application/json")
          else:
            response['errors'] = parameterization_form.errors
            return HttpResponse(json.dumps(response), mimetype="application/json")

      # Non-parameterized query
      query = HQLdesign(query_form, query_type=query_type)
      if request.GET.get('explain', 'false').lower() == 'true':
        return explain_directly(request, query, design, query_server)
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
  except RuntimeError, e:
    response['message']= str(e)

  return HttpResponse(json.dumps(response), mimetype="application/json")


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
        'functions': query_form.functions.errors
      }
  except RuntimeError, e:
    response['message'] = str(e)

  return HttpResponse(json.dumps(response), mimetype="application/json")


@error_handler
def fetch_saved_design(request, design_id):
  response = {'status': 0, 'message': ''}

  if request.method != 'GET':
    response['message'] = _('A GET request is required.')

  app_name = get_app_name(request)
  query_type = beeswax.models.SavedQuery.TYPES_MAPPING[app_name]
  design = safe_get_design(request, query_type, design_id)

  response['design'] = design_to_dict(design)
  return HttpResponse(json.dumps(response), mimetype="application/json")

@error_handler
def fetch_query_history(request, query_history_id):
  response = {'status': 0, 'message': ''}

  if request.method != 'GET':
    response['message'] = _('A GET request is required.')

  query = authorized_get_query_history(request, query_history_id, must_exist=True)

  response['query_history'] = query_history_to_dict(request, query)
  return HttpResponse(json.dumps(response), mimetype="application/json")

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
      _get_query_handle_and_state(query_history)
      response['status'] = 0
    except Exception, e:
      response['message'] = unicode(e)

  return HttpResponse(json.dumps(response), mimetype="application/json")


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
      return HttpResponse(json.dumps(response), mimetype="application/json")

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
        response['success_url'] = '/filebrowser/view%s' % target_dir
        query_history = db.insert_query_into_directory(query_history, target_dir)
        response['watch_url'] = reverse(get_app_name(request) + ':api_watch_query_refresh_json', kwargs={'id': query_history.id})
      except Exception, ex:
        error_msg, log = expand_exception(ex, db)
        response['message'] = _('The result could not be saved: %s.') % error_msg
        response['status'] = -3
    else:
      response['status'] = 1
      response['errors'] = form.errors

  return HttpResponse(json.dumps(response), mimetype="application/json")


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
      return HttpResponse(json.dumps(response), mimetype="application/json")

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
      except Exception, ex:
        response['message'] = _('Cannot find query handle and state: %s') % str(query_history)
        response['status'] = -2
        return HttpResponse(json.dumps(response), mimetype="application/json")

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
        response['success_url'] = '/filebrowser/view%s' % target_file
        response['watch_url'] = reverse(get_app_name(request) + ':api_watch_query_refresh_json', kwargs={'id': query_history.id})
      except Exception, ex:
        error_msg, log = expand_exception(ex, db)
        response['message'] = _('The result could not be saved: %s.') % error_msg
        response['status'] = -3
    else:
      response['status'] = 1
      response['errors'] = form.errors

  return HttpResponse(json.dumps(response), mimetype="application/json")


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
      return HttpResponse(json.dumps(response), mimetype="application/json")

    db = dbms.get(request.user, query_history.get_query_server_config())
    database = query_history.design.get_design().query.get('database', 'default')
    form = beeswax.forms.SaveResultsTableForm({
      'target_table': request.POST.get('table')
    }, db=db, database=database)

    if form.is_valid():
      try:
        handle, state = _get_query_handle_and_state(query_history)
        result_meta = db.get_results_metadata(handle)
      except Exception, ex:
        response['message'] = _('Cannot find query handle and state: %s') % str(query_history)
        response['status'] = -2
        return HttpResponse(json.dumps(response), mimetype="application/json")

      try:
        query_history = db.create_table_as_a_select(request, query_history, form.target_database, form.cleaned_data['target_table'], result_meta)
        response['id'] = query_history.id
        response['query'] = query_history.query
        response['type'] = 'hive-table'
        response['path'] = form.cleaned_data['target_table']
        response['success_url'] = reverse('metastore:describe_table', kwargs={'database': form.target_database, 'table': form.cleaned_data['target_table']})
        response['watch_url'] = reverse(get_app_name(request) + ':api_watch_query_refresh_json', kwargs={'id': query_history.id})
      except Exception, ex:
        error_msg, log = expand_exception(ex, db)
        response['message'] = _('The result could not be saved: %s.') % error_msg
        response['status'] = -3

    else:
      response['status'] = 1
      response['errors'] = form.errors

  return HttpResponse(json.dumps(response), mimetype="application/json")


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


# Proxy API for Metastore App
def describe_table(request, database, table):
  try:
    from metastore.views import describe_table
    return describe_table(request, database, table)
  except Exception, e:
    raise PopupException(_('Problem accessing table metadata'), detail=e)


def get_query_form(request):
  # Get database choices
  query_server = dbms.get_query_server_config(get_app_name(request))
  db = dbms.get(request.user, query_server)
  databases = [(database, database) for database in db.get_databases()]

  if not databases:
    raise RuntimeError(_("No databases are available. Permissions could be missing."))

  query_form = QueryForm()
  query_form.bind(request.POST)
  query_form.query.fields['database'].choices = databases # Could not do it in the form

  return query_form
