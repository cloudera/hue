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

try:
  import json
except ImportError:
  import simplejson as json
import logging

from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException

from beeswax.models import SavedQuery, MetaInstall
from beeswax.server import dbms

from catalog.forms import LoadDataForm, DbForm

LOG = logging.getLogger(__name__)
SAVE_RESULTS_CTAS_TIMEOUT = 300         # seconds


def index(request):
  return redirect(reverse('catalog:show_tables'))


"""
Table Views
"""

def show_tables(request, database=None):
  if database is None:
    database = request.COOKIES.get('hueBeeswaxLastDatabase', 'default') # Assume always 'default'
  db = dbms.get(request.user)

  databases = db.get_databases()

  if request.method == 'POST':
    db_form = DbForm(request.POST, databases=databases)
    if db_form.is_valid():
      database = db_form.cleaned_data['database']
  else:
    db_form = DbForm(initial={'database': database}, databases=databases)

  tables = db.get_tables(database=database)
  examples_installed = MetaInstall.get().installed_example

  return render("tables.mako", request, {
      'tables': tables,
      'examples_installed': examples_installed,
      'db_form': db_form,
      'database': database,
      'tables_json': json.dumps(tables),
  })


def describe_table(request, database, table):
  db = dbms.get(request.user)
  error_message = ''
  table_data = ''

  table = db.get_table(database, table)

  try:
    table_data = db.get_sample(database, table)
  except Exception, ex:
    error_message, logs = dbms.expand_exception(ex, db)

  return render("describe_table.mako", request, {
      'table': table,
      'sample': table_data and table_data.rows(),
      'error_message': error_message,
      'database': database,
  })


def drop_table(request, database):
  db = dbms.get(request.user)

  if request.method == 'POST':
    tables = request.POST.getlist('table_selection')
    tables_objects = [db.get_table(database, table) for table in tables]
    try:
      # Can't be simpler without an important refactoring
      design = SavedQuery.create_empty(app_name='beeswax', owner=request.user)
      query_history = db.drop_tables(database, tables_objects, design)
      url = reverse('beeswax:watch_query', args=[query_history.id]) + '?on_success_url=' + reverse('catalog:show_tables')
      return redirect(url)
    except Exception, ex:
      error_message, log = dbms.expand_exception(ex, db)
      error = _("Failed to remove %(tables)s.  Error: %(error)s") % {'tables': ','.join(tables), 'error': error_message}
      raise PopupException(error, title=_("Beeswax Error"), detail=log)
  else:
    title = _("Do you really want to delete the table(s)?")
    return render('confirm.html', request, dict(url=request.path, title=title))


def read_table(request, database, table):
  db = dbms.get(request.user)

  table = db.get_table(database, table)

  try:
    history = db.select_star_from(database, table)
    url = reverse('beeswax:watch_query', args=[history.id]) + '?context=table:%s:%s' % (table.name, database)
    return redirect(url)
  except Exception, e:
    raise PopupException(_('Can read table'), detail=e)


def load_table(request, database, table):
  db = dbms.get(request.user)
  table = db.get_table(database, table)
  response = {'status': -1, 'data': 'None'}

  if request.method == "POST":
    load_form = LoadDataForm(table, request.POST)

    if load_form.is_valid():
      on_success_url = reverse('catalog:describe_table', kwargs={'database': database, 'table': table.name})
      try:
        design = SavedQuery.create_empty(app_name='beeswax', owner=request.user)
        query_history = db.load_data(database, table, load_form, design)
        url = reverse('beeswax:watch_query', args=[query_history.id]) + '?on_success_url=' + on_success_url
        response['status'] = 0
        response['data'] = url
      except Exception, e:
        response['status'] = 1
        response['data'] = _("Can't load the data: ") + str(e)
  else:
    load_form = LoadDataForm(table)

  if response['status'] == -1:
    popup = render('popups/load_data.mako', request, {
                     'table': table,
                     'load_form': load_form,
                     'database': database,
                     'app_name': 'beeswax'
                 }, force_template=True).content
    response['data'] = popup

  return HttpResponse(json.dumps(response), mimetype="application/json")


def describe_partitions(request, database, table):
  db = dbms.get(request.user)

  table_obj = db.get_table(database, table)
  if not table_obj.partition_keys:
    raise PopupException(_("Table '%(table)s' is not partitioned.") % {'table': table})

  partitions = db.get_partitions(database, table_obj, max_parts=None)

  return render("describe_partitions.mako", request,
                dict(table=table_obj, partitions=partitions, request=request))
