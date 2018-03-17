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

import datetime
import decimal
import json
import logging

from django.http import Http404
from django.utils.translation import ugettext as _
from django.utils.html import escape

from desktop.lib.django_util import JsonResponse
from desktop.context_processors import get_app_name

from librdbms import conf
from librdbms.server import dbms
from librdbms.design import SQLdesign

from beeswax import models as beeswax_models
from beeswax.forms import SaveForm
from beeswax.views import authorized_get_query_history, safe_get_design

from rdbms.forms import SQLForm
from rdbms.views import save_design


LOG = logging.getLogger(__name__)


class ResultEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime.datetime):
      return obj.strftime('%Y-%m-%d %H:%M:%S %Z')
    elif isinstance(obj, datetime.date):
      return obj.strftime('%Y-%m-%d %Z')
    elif isinstance(obj, decimal.Decimal):
      return float(obj)
    return super(ResultEncoder, self).default(obj)


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except Http404, e:
      raise e
    except Exception, e:
      LOG.exception('error in %s' % view_fn)

      response = {
        'error': str(e)
      }

      return JsonResponse(response, status=500)
  return decorator


def servers(request):
  servers = conf.get_server_choices()
  servers_dict = dict(servers)
  response = {
    'servers': servers_dict
  }

  return JsonResponse(response)


@error_handler
def databases(request, server):
  query_server = dbms.get_query_server_config(server)

  if not query_server:
    raise Http404

  db = dbms.get(request.user, query_server)

  response = {
    'status': 0,
    'databases': db.get_databases()
  }

  return JsonResponse(response)


@error_handler
def tables(request, server, database):
  query_server = dbms.get_query_server_config(server)

  if not query_server:
    raise Http404

  db = dbms.get(request.user, query_server)
  db.use(database)

  response = {
    'tables': db.get_tables(database)
  }

  return JsonResponse(response)


@error_handler
def columns(request, server, database, table):
  query_server = dbms.get_query_server_config(server)

  if not query_server:
    raise Http404

  db = dbms.get(request.user, query_server)
  db.use(database)

  response = {
    'columns': db.get_columns(database, table)
  }

  return JsonResponse(response)


@error_handler
def execute_query(request, design_id=None):
  response = {'status': -1, 'message': ''}

  if request.method != 'POST':
    response['message'] = _('A POST request is required.')

  app_name = get_app_name(request)
  query_type = beeswax_models.SavedQuery.TYPES_MAPPING[app_name]
  design = safe_get_design(request, query_type, design_id)

  try:
    form = get_query_form(request, design_id)

    if form.is_valid():
      design = save_design(request, SaveForm(), form, query_type, design)

      query = SQLdesign(form, query_type=query_type)
      query_server = dbms.get_query_server_config(request.POST.get('server'))
      db = dbms.get(request.user, query_server)
      query_history = db.execute_query(query, design)
      query_history.last_state = beeswax_models.QueryHistory.STATE.expired.value
      query_history.save()

      try:
        db.use(form.cleaned_data['database'])
        datatable = db.execute_and_wait(query)
        results = db.client.create_result(datatable)

        response['status'] = 0
        response['results'] = results_to_dict(results)
        response['design'] = design.id
      except Exception, e:
        response['status'] = -1
        response['message'] = str(e)

    else:
      response['message'] = _('There was an error with your query.')
      response['errors'] = form.errors
  except RuntimeError, e:
    response['message']= str(e)

  return JsonResponse(response, encoder=ResultEncoder)


@error_handler
def explain_query(request):
  response = {'status': -1, 'message': ''}

  if request.method != 'POST':
    response['message'] = _('A POST request is required.')

  app_name = get_app_name(request)
  query_type = beeswax_models.SavedQuery.TYPES_MAPPING[app_name]

  try:
    form = get_query_form(request)

    if form.is_valid():
      query = SQLdesign(form, query_type=query_type)
      query_server = dbms.get_query_server_config(request.POST.get('server'))
      db = dbms.get(request.user, query_server)

      try:
        db.use(form.cleaned_data['database'])
        datatable = db.explain(query)
        results = db.client.create_result(datatable)

        response['status'] = 0
        response['results'] = results_to_dict(results)
      except Exception, e:
        response['status'] = -1
        response['message'] = str(e)

    else:
      response['message'] = _('There was an error with your query.')
      response['errors'] = form.errors
  except RuntimeError, e:
    response['message']= str(e)

  return JsonResponse(response)


@error_handler
def fetch_results(request, id, first_row=0):
  """
  Returns the results of the QueryHistory with the given id.

  The query results MUST be ready.

  If ``first_row`` is 0, restarts (if necessary) the query read.  Otherwise, just
  spits out a warning if first_row doesn't match the servers conception.
  Multiple readers will produce a confusing interaction here, and that's known.
  """
  first_row = long(first_row)
  results = type('Result', (object,), {
                'rows': 0,
                'columns': [],
                'has_more': False,
                'start_row': 0,
            })
  fetch_error = False
  error_message = ''

  query_history = authorized_get_query_history(request, id, must_exist=True)
  query_server = query_history.get_query_server_config()
  design = SQLdesign.loads(query_history.design.data)
  db = dbms.get(request.user, query_server)

  try:
    database = design.query.get('database', 'default')
    db.use(database)
    datatable = db.execute_and_wait(design)
    results = db.client.create_result(datatable)
    status = 0
  except Exception, e:
    fetch_error = True
    error_message = str(e)
    status = -1

  response = {
    'status': status,
    'message': fetch_error and error_message or '',
    'results': results_to_dict(results)
  }
  return JsonResponse(response)


@error_handler
def save_query(request, design_id=None):
  response = {'status': -1, 'message': ''}

  if request.method != 'POST':
    response['message'] = _('A POST request is required.')

  app_name = get_app_name(request)
  query_type = beeswax_models.SavedQuery.TYPES_MAPPING[app_name]
  design = safe_get_design(request, query_type, design_id)

  try:
    save_form = SaveForm(request.POST.copy())
    query_form = get_query_form(request, design_id)

    if query_form.is_valid() and save_form.is_valid():
      design = save_design(request, save_form, query_form, query_type, design, True)
      response['design_id'] = design.id
      response['status'] = 0
    else:
      response['errors'] = query_form.errors
  except RuntimeError, e:
    response['message'] = str(e)

  return JsonResponse(response)


@error_handler
def fetch_saved_query(request, design_id):
  response = {'status': -1, 'message': ''}

  if request.method != 'GET':
    response['message'] = _('A GET request is required.')

  app_name = get_app_name(request)
  query_type = beeswax_models.SavedQuery.TYPES_MAPPING[app_name]
  design = safe_get_design(request, query_type, design_id)

  response['design'] = design_to_dict(design)
  return JsonResponse(response)


def results_to_dict(results):
  data = {}
  rows = []
  for row in results.rows():
    rows.append(dict(zip(results.columns, [escape(r) if isinstance(r, (str, unicode)) else r for r in row])))
  data['rows'] = rows
  data['start_row'] = results.start_row
  data['has_more'] = results.has_more
  data['columns'] = results.columns
  return data


def design_to_dict(design):
  sql_design = SQLdesign.loads(design.data)
  return {
    'id': design.id,
    'query': sql_design.sql_query,
    'name': design.name,
    'desc': design.desc,
    'server': sql_design.server,
    'database': sql_design.database
  }


def get_query_form(request, design_id=None):
  servers = conf.get_server_choices()

  # Get database choices
  query_server = dbms.get_query_server_config(request.POST.get('server'))

  if not query_server:
    raise RuntimeError(_("Server specified doesn't exist."))

  db = dbms.get(request.user, query_server)
  databases = [(database, database) for database in db.get_databases()]

  if not databases:
    raise RuntimeError(_("No databases are available. Permissions could be missing."))

  form = SQLForm(request.POST)
  form.fields['server'].choices = servers # Could not do it in the form
  form.fields['database'].choices = databases # Could not do it in the form

  return form
