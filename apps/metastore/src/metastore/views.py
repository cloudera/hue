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
import urllib

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.functional import wraps
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods

from desktop.context_processors import get_app_name
from desktop.lib.django_util import JsonResponse, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document, Document2

from metadata.conf import has_optimizer, get_optimizer_url, get_navigator_url

from beeswax.design import hql_query
from beeswax.models import SavedQuery, MetaInstall
from beeswax.server import dbms
from beeswax.server.dbms import get_query_server_config
from filebrowser.views import location_to_url
from metastore.forms import LoadDataForm, DbForm
from metastore.settings import DJANGO_APPS
from notebook.connectors.base import Notebook


LOG = logging.getLogger(__name__)

SAVE_RESULTS_CTAS_TIMEOUT = 300         # seconds


def check_has_write_access_permission(view_func):
  """
  Decorator ensuring that the user is not a read only user.
  """
  def decorate(request, *args, **kwargs):
    if not has_write_access(request.user):
      raise PopupException(_('You are not allowed to modify the metastore.'), detail=_('You have must have metastore:write permissions'), error_code=301)

    return view_func(request, *args, **kwargs)
  return wraps(view_func)(decorate)


def index(request):
  return redirect(reverse('metastore:show_tables', kwargs={'database': ''}))


"""
Database Views
"""

def databases(request):
  search_filter = request.GET.get('filter', '')

  db = dbms.get(request.user)
  databases = db.get_databases(search_filter)

  return render("metastore.mako", request, {
    'breadcrumbs': [],
    'database': None,
    'databases': databases,
    'partitions': [],
    'has_write_access': has_write_access(request.user),
    'is_optimizer_enabled': has_optimizer(),
    'optimizer_url': get_optimizer_url(),
    'navigator_url': get_navigator_url(),
  })


@check_has_write_access_permission
def drop_database(request):
  db = dbms.get(request.user)

  if request.method == 'POST':
    databases = request.POST.getlist('database_selection')

    try:
      # Can't be simpler without an important refactoring
      design = SavedQuery.create_empty(app_name='beeswax', owner=request.user, data=hql_query('').dumps())
      query_history = db.drop_databases(databases, design)
      url = reverse('beeswax:watch_query_history', kwargs={'query_history_id': query_history.id}) + '?on_success_url=' + reverse('metastore:databases')
      return redirect(url)
    except Exception, ex:
      error_message, log = dbms.expand_exception(ex, db)
      error = _("Failed to remove %(databases)s.  Error: %(error)s") % {'databases': ','.join(databases), 'error': error_message}
      raise PopupException(error, title=_("Hive Error"), detail=log)
  else:
    title = _("Do you really want to delete the database(s)?")
    return render('confirm.mako', request, {'url': request.path, 'title': title})


def get_database_metadata(request, database):
  db = dbms.get(request.user)
  response = {'status': -1, 'data': ''}
  try:
    db_metadata = db.get_database(database)
    response['status'] = 0
    db_metadata['hdfs_link'] = location_to_url(db_metadata['location'])
    response['data'] = db_metadata
  except Exception, ex:
    response['status'] = 1
    response['data'] = _("Cannot get metadata for database %s: %s") % (database, ex)

  return JsonResponse(response)


def table_queries(request, database, table):
  qfilter = Q(data__icontains=table) | Q(data__icontains='%s.%s' % (database, table))

  response = {'status': -1, 'queries': []}
  try:
    queries = [{'doc': d.to_dict(), 'data': Notebook(document=d).get_data()}
              for d in Document2.objects.filter(qfilter, owner=request.user, type='query', is_history=False)[:50]]
    response['status'] = 0
    response['queries'] = queries
  except Exception, ex:
    response['status'] = 1
    response['data'] = _("Cannot get queries related to table %s.%s: %s") % (database, table, ex)

  return JsonResponse(response)


"""
Table Views
"""
def show_tables(request, database=None):
  if database is None:
    database = 'default' # Assume always 'default'

  if request.REQUEST.get("format", "html") == "json":
    db = dbms.get(request.user)

    try:
      databases = db.get_databases()

      if database not in databases:
        database = 'default'

      if request.method == 'POST':
        db_form = DbForm(request.POST, databases=databases)
        if db_form.is_valid():
          database = db_form.cleaned_data['database']
      else:
        db_form = DbForm(initial={'database': database}, databases=databases)

      search_filter = request.GET.get('filter', '')

      tables = db.get_tables_meta(database=database, table_names=search_filter) # SparkSql returns []
      table_names = [table['name'] for table in tables]
    except Exception, e:
      raise PopupException(_('Failed to retrieve tables for database: %s' % database), detail=e)

    resp = JsonResponse({
        'status': 0,
        'database_meta': db.get_database(database),
        'tables': tables,
        'table_names': table_names,
        'search_filter': search_filter
    })
  else:
    resp = render("metastore.mako", request, {
    'breadcrumbs': [],
    'database': None,
    'partitions': [],
    'has_write_access': has_write_access(request.user),
    'is_optimizer_enabled': has_optimizer(),
    'optimizer_url': get_optimizer_url(),
    'navigator_url': get_navigator_url(),
    })

  return resp


def get_table_metadata(request, database, table):
  db = dbms.get(request.user)
  response = {'status': -1, 'data': ''}
  try:
    table_metadata = db.get_table(database, table)
    response['status'] = 0
    response['data'] = {
      'comment': table_metadata.comment,
      'hdfs_link': table_metadata.hdfs_link,
      'is_view': table_metadata.is_view
    }
  except Exception, ex:
    response['status'] = 1
    response['data'] = _("Cannot get metadata for table: `%s`.`%s`") % (database, table)

  return JsonResponse(response)


def describe_table(request, database, table):
  app_name = get_app_name(request)
  query_server = get_query_server_config(app_name)
  db = dbms.get(request.user, query_server)

  try:
    table = db.get_table(database, table)
  except Exception, e:
    LOG.exception("Describe table error")
    if hasattr(e, 'message') and e.message:
      raise PopupException(_("Hive Error"), detail=e.message)
    else:
      raise PopupException(_("Hive Error"), detail=e)

  if request.REQUEST.get("format", "html") == "json":
    return JsonResponse({
        'status': 0,
        'name': table.name,
        'partition_keys': [{'name': part.name, 'type': part.type} for part in table.partition_keys],
        'cols': [{'name': col.name, 'type': col.type, 'comment': col.comment} for col in table.cols],
        'path_location': table.path_location,
        'hdfs_link': table.hdfs_link,
        'comment': table.comment,
        'is_view': table.is_view,
        'properties': table.properties,
        'details': table.details,
        'stats': table.stats
    })
  else:  # Render HTML
    renderable = "metastore.mako"

    partitions = None
    if app_name != 'impala' and table.partition_keys:
      partitions = [_massage_partition(database, table, partition) for partition in db.get_partitions(database, table)]

    return render(renderable, request, {
      'breadcrumbs': [{
          'name': database,
          'url': reverse('metastore:show_tables', kwargs={'database': database})
        }, {
          'name': str(table.name),
          'url': reverse('metastore:describe_table', kwargs={'database': database, 'table': table.name})
        },
      ],
      'table': table,
      'partitions': partitions,
      'database': database,
      'has_write_access': has_write_access(request.user),
      'is_optimizer_enabled': has_optimizer(),
      'optimizer_url': get_optimizer_url(),
      'navigator_url': get_navigator_url(),
    })


@check_has_write_access_permission
@require_http_methods(["POST"])
def alter_table(request, database, table):
  db = dbms.get(request.user)
  response = {'status': -1, 'data': ''}
  try:
    new_table_name = request.POST.get('new_table_name', None)
    comment = request.POST.get('comment', None)

    # Cannot modify both name and comment at same time, name will get precedence
    if new_table_name and comment:
      LOG.warn('Cannot alter both table name and comment at the same time, will perform rename.')

    table_obj = db.alter_table(database, table, new_table_name=new_table_name, comment=comment)

    response['status'] = 0
    response['data'] = {
      'name': table_obj.name,
      'comment': table_obj.comment,
      'is_view': table_obj.is_view,
      'location': table_obj.path_location,
      'properties': table_obj.properties
    }
  except Exception, ex:
    response['status'] = 1
    response['data'] = _("Failed to alter table `%s`.`%s`: %s") % (database, table, str(ex))

  return JsonResponse(response)


@check_has_write_access_permission
@require_http_methods(["POST"])
def alter_column(request, database, table):
  db = dbms.get(request.user)
  response = {'status': -1, 'message': ''}
  try:
    column = request.POST.get('column', None)

    if column is None:
      raise PopupException(_('alter_column requires a column parameter'))

    column_obj = db.get_column(database, table, column)
    if column_obj:
      new_column_name = request.POST.get('new_column_name', column_obj.name)
      new_column_type = request.POST.get('new_column_type', column_obj.type)
      comment = request.POST.get('comment', None)
      partition_spec = request.POST.get('partition_spec', None)

      column_obj = db.alter_column(database, table, column, new_column_name, new_column_type, comment=comment, partition_spec=partition_spec)

      response['status'] = 0
      response['data'] = {
        'name': column_obj.name,
        'type': column_obj.type,
        'comment': column_obj.comment
      }
    else:
      raise PopupException(_('Column `%s`.`%s` `%s` not found') % (database, table, column))
  except Exception, ex:
    response['status'] = 1
    response['message'] = _("Failed to alter column `%s`.`%s` `%s`: %s") % (database, table, column, str(ex))

  return JsonResponse(response)


@check_has_write_access_permission
def drop_table(request, database):
  db = dbms.get(request.user)

  if request.method == 'POST':
    tables = request.POST.getlist('table_selection')
    tables_objects = [db.get_table(database, table) for table in tables]
    try:
      # Can't be simpler without an important refactoring
      design = SavedQuery.create_empty(app_name='beeswax', owner=request.user, data=hql_query('').dumps())
      query_history = db.drop_tables(database, tables_objects, design)
      url = reverse('beeswax:watch_query_history', kwargs={'query_history_id': query_history.id}) + '?on_success_url=' + reverse('metastore:show_tables', kwargs={'database': database})
      return redirect(url)
    except Exception, ex:
      error_message, log = dbms.expand_exception(ex, db)
      error = _("Failed to remove %(tables)s.  Error: %(error)s") % {'tables': ','.join(tables), 'error': error_message}
      raise PopupException(error, title=_("Hive Error"), detail=log)
  else:
    title = _("Do you really want to delete the table(s)?")
    return render('confirm.mako', request, {'url': request.path, 'title': title})


def read_table(request, database, table):
  db = dbms.get(request.user)

  table = db.get_table(database, table)

  try:
    query_history = db.select_star_from(database, table)
    url = reverse('beeswax:watch_query_history', kwargs={'query_history_id': query_history.id}) + '?on_success_url=&context=table:%s:%s' % (table.name, database)
    return redirect(url)
  except Exception, e:
    raise PopupException(_('Cannot read table'), detail=e)


@check_has_write_access_permission
def load_table(request, database, table):
  db = dbms.get(request.user)
  table = db.get_table(database, table)
  response = {'status': -1, 'data': 'None'}

  if request.method == "POST":
    load_form = LoadDataForm(table, request.POST)

    if load_form.is_valid():
      on_success_url = reverse('metastore:describe_table', kwargs={'database': database, 'table': table.name})
      try:
        design = SavedQuery.create_empty(app_name='beeswax', owner=request.user, data=hql_query('').dumps())
        query_history = db.load_data(database, table, load_form, design)
        url = reverse('beeswax:watch_query_history', kwargs={'query_history_id': query_history.id}) + '?on_success_url=' + on_success_url
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

  return JsonResponse(response)


def describe_partitions(request, database, table):
  db = dbms.get(request.user)

  table_obj = db.get_table(database, table)

  if not table_obj.partition_keys:
    raise PopupException(_("Table '%(table)s' is not partitioned.") % {'table': table})

  reverse_sort = request.REQUEST.get("sort", "desc").lower() == "desc"

  if request.method == "POST":
    partition_filters = {}
    for part in table_obj.partition_keys:
      if request.REQUEST.get(part.name):
        partition_filters[part.name] = request.REQUEST.get(part.name)
    partition_spec = ','.join(["%s='%s'" % (k, v) for k, v in partition_filters.items()])
  else:
    partition_spec = ''

  partitions = db.get_partitions(database, table_obj, partition_spec, reverse_sort=reverse_sort)
  massaged_partitions = [_massage_partition(database, table_obj, partition) for partition in partitions]

  if request.method == "POST" or request.GET.get('format', 'html') == 'json':
    return JsonResponse({
      'partition_keys_json': [partition.name for partition in table_obj.partition_keys],
      'partition_values_json': massaged_partitions,
    })
  else:
    return render("describe_partitions.mako", request, {
      'breadcrumbs': [{
            'name': database,
            'url': reverse('metastore:show_tables', kwargs={'database': database})
          }, {
            'name': table,
            'url': reverse('metastore:describe_table', kwargs={'database': database, 'table': table})
          },{
            'name': 'partitions',
            'url': reverse('metastore:describe_partitions', kwargs={'database': database, 'table': table})
          },
        ],
        'database': database,
        'table': table_obj,
        'partitions': partitions,
        'partition_keys_json': json.dumps([partition.name for partition in table_obj.partition_keys]),
        'partition_values_json': json.dumps(massaged_partitions),
        'request': request,
        'has_write_access': has_write_access(request.user),
        'is_optimizer_enabled': has_optimizer(),
    })


def _massage_partition(database, table, partition):
  return {
    'columns': partition.values,
    'partitionSpec': partition.partition_spec,
    'readUrl': reverse('metastore:read_partition', kwargs={
        'database': database,
        'table': table.name,
        'partition_spec': urllib.quote(partition.partition_spec)
    }),
    'browseUrl': reverse('metastore:browse_partition', kwargs={
        'database': database,
        'table': table.name,
        'partition_spec': urllib.quote(partition.partition_spec)
    })
  }


def browse_partition(request, database, table, partition_spec):
  db = dbms.get(request.user)
  try:
    decoded_spec = urllib.unquote(partition_spec)
    partition_table = db.describe_partition(database, table, decoded_spec)
    uri_path = location_to_url(partition_table.path_location)
    return redirect(uri_path)
  except Exception, e:
    raise PopupException(_('Cannot browse partition'), detail=e.message)


def read_partition(request, database, table, partition_spec):
  db = dbms.get(request.user)
  try:
    decoded_spec = urllib.unquote(partition_spec)
    query = db.get_partition(database, table, decoded_spec)
    url = reverse('beeswax:watch_query_history', kwargs={'query_history_id': query.id}) + '?on_success_url=&context=table:%s:%s' % (table, database)
    return redirect(url)
  except Exception, e:
    raise PopupException(_('Cannot read partition'), detail=e.message)

@require_http_methods(["GET", "POST"])
@check_has_write_access_permission
def drop_partition(request, database, table):
  db = dbms.get(request.user)

  if request.method == 'POST':
    partition_specs = request.POST.getlist('partition_selection')
    partition_specs = [spec for spec in partition_specs]
    try:
      design = SavedQuery.create_empty(app_name='beeswax', owner=request.user, data=hql_query('').dumps())
      query_history = db.drop_partitions(database, table, partition_specs, design)
      url = reverse('beeswax:watch_query_history', kwargs={'query_history_id': query_history.id}) + '?on_success_url=' + \
            reverse('metastore:describe_partitions', kwargs={'database': database, 'table': table})
      return redirect(url)
    except Exception, ex:
      error_message, log = dbms.expand_exception(ex, db)
      error = _("Failed to remove %(partition)s.  Error: %(error)s") % {'partition': '\n'.join(partition_specs), 'error': error_message}
      raise PopupException(error, title=_("Hive Error"), detail=log)
  else:
    title = _("Do you really want to delete the partition(s)?")
    return render('confirm.mako', request, {'url': request.path, 'title': title})


def has_write_access(user):
  return user.is_superuser or user.has_hue_permission(action="write", app=DJANGO_APPS[0])
