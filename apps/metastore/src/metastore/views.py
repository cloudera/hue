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
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.functional import wraps
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods

from desktop.context_processors import get_app_name
from desktop.lib.django_util import JsonResponse, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document2, get_cluster_config, _get_apps

from beeswax.design import hql_query
from beeswax.models import SavedQuery
from beeswax.server import dbms
from beeswax.server.dbms import get_query_server_config
from desktop.lib.view_util import location_to_url
from metadata.conf import has_optimizer, has_catalog, get_optimizer_url, get_catalog_url
from notebook.connectors.base import Notebook, QueryError
from notebook.models import make_notebook

from metastore.conf import FORCE_HS2_METADATA
from metastore.forms import LoadDataForm, DbForm
from metastore.settings import DJANGO_APPS

from desktop.auth.backend import is_admin


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
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = _get_db(user=request.user, cluster=cluster)
  databases = db.get_databases(search_filter)
  apps_list = _get_apps(request.user, '')

  return render("metastore.mako", request, {
    'apps': apps_list,
    'breadcrumbs': [],
    'database': None,
    'databases': databases,
    'partitions': [],
    'has_write_access': has_write_access(request.user),
    'is_optimizer_enabled': has_optimizer(),
    'is_navigator_enabled': has_catalog(request.user),
    'optimizer_url': get_optimizer_url(),
    'navigator_url': get_catalog_url(),
    'is_embeddable': request.GET.get('is_embeddable', False),
    'source_type': _get_servername(db),
  })


@check_has_write_access_permission
def drop_database(request):
  source_type = request.POST.get('source_type', request.GET.get('source_type', 'hive'))
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = _get_db(user=request.user, source_type=source_type, cluster=cluster)

  if request.method == 'POST':
    databases = request.POST.getlist('database_selection')

    try:
      if request.POST.get('is_embeddable'):
        design = SavedQuery.create_empty(app_name=source_type if source_type != 'hive' else 'beeswax', owner=request.user, data=hql_query('').dumps())
        last_executed = json.loads(request.POST.get('start_time'), '-1')
        cluster = json.loads(request.POST.get('cluster', '{}'))
        namespace = request.POST.get('namespace')
        sql = db.drop_databases(databases, design, generate_ddl_only=True)
        job = make_notebook(
            name=_('Drop database %s') % ', '.join(databases)[:100],
            editor_type=source_type,
            statement=sql.strip(),
            status='ready',
            database=None,
            namespace=namespace,
            compute=cluster,
            on_success_url='assist.db.refresh',
            is_task=True,
            last_executed=last_executed
        )
        return JsonResponse(job.execute(request))
      else:
        design = SavedQuery.create_empty(app_name='beeswax', owner=request.user, data=hql_query('').dumps())
        query_history = db.drop_databases(databases, design)
        url = reverse('beeswax:watch_query_history', kwargs={'query_history_id': query_history.id}) + '?on_success_url=' + reverse('metastore:databases')
        return redirect(url)
    except Exception, ex:
      error_message, log = dbms.expand_exception(ex, db)
      error = _("Failed to remove %(databases)s.  Error: %(error)s") % {'databases': ','.join(databases), 'error': error_message}
      raise PopupException(error, title=_("DB Error"), detail=log)
  else:
    title = _("Do you really want to delete the database(s)?")
    return render('confirm.mako', request, {'url': request.path, 'title': title})


@check_has_write_access_permission
@require_http_methods(["POST"])
def alter_database(request, database):
  response = {'status': -1, 'data': ''}

  source_type = request.POST.get('source_type', 'hive')
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = _get_db(user=request.user, source_type=source_type, cluster=cluster)

  try:
    properties = request.POST.get('properties')

    if not properties:
      raise PopupException(_("Alter database requires a properties value of key-value pairs."))

    properties = json.loads(properties)
    db.alter_database(database, properties=properties)

    db_metadata = db.get_database(database)
    db_metadata['hdfs_link'] = location_to_url(db_metadata['location'])
    response['status'] = 0
    response['data'] = db_metadata
  except Exception, ex:
    response['status'] = 1
    response['data'] = _("Failed to alter database `%s`: %s") % (database, ex)

  return JsonResponse(response)


def get_database_metadata(request, database):
  response = {'status': -1, 'data': ''}

  source_type = request.POST.get('source_type', 'hive')
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = _get_db(user=request.user, source_type=source_type, cluster=cluster)

  try:
    db_metadata = db.get_database(database)
    response['status'] = 0
    if not db_metadata.get('owner_name'):
      db_metadata['owner_name'] = ''
    if not db_metadata.get('owner_type'):
      db_metadata['owner_type'] = ''
    if not db_metadata.get('parameters'):
      db_metadata['parameters'] = ''
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
    queries = [
        {'doc': d.to_dict(), 'data': Notebook(document=d).get_data()}
        for d in Document2.objects.filter(qfilter, owner=request.user, type='query', is_history=False)[:50]
    ]
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
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = _get_db(user=request.user, cluster=cluster)

  if database is None:
    database = 'default' # Assume always 'default'

  if request.GET.get("format", "html") == "json":
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
    apps_list = _get_apps(request.user, '')
    resp = render("metastore.mako", request, {
    'apps': apps_list,
    'breadcrumbs': [],
    'database': None,
    'partitions': [],
    'has_write_access': has_write_access(request.user),
    'is_optimizer_enabled': has_optimizer(),
    'is_navigator_enabled': has_catalog(request.user),
    'optimizer_url': get_optimizer_url(),
    'navigator_url': get_catalog_url(),
    'is_embeddable': request.GET.get('is_embeddable', False),
    'source_type': _get_servername(db),
    })

  return resp


def get_table_metadata(request, database, table):
  cluster = json.loads(request.POST.get('cluster', '{}'))
  source_type = request.POST.get('source_type')

  db = _get_db(user=request.user, source_type=source_type, cluster=cluster)
  response = {'status': -1, 'data': ''}
  try:
    table_metadata = db.get_table(database, table)
    response['status'] = 0
    response['data'] = {
      'comment': table_metadata.comment,
      'hdfs_link': table_metadata.hdfs_link,
      'is_view': table_metadata.is_view
    }
  except:
    msg = "Cannot get metadata for table: `%s`.`%s`"
    LOG.exception(msg) % (database, table)
    response['status'] = 1
    response['data'] = _(msg) % (database, table)

  return JsonResponse(response)


def describe_table(request, database, table):
  app_name = get_app_name(request)
  cluster = json.loads(request.POST.get('cluster', '{}'))
  source_type = request.POST.get('source_type', request.GET.get('source_type', 'hive'))
  db = _get_db(user=request.user, source_type=source_type, cluster=cluster)

  try:
    table = db.get_table(database, table)
  except Exception, e:
    LOG.exception("Describe table error")
    raise PopupException(_("DB Error"), detail=e.message if hasattr(e, 'message') and e.message else e)

  if request.POST.get("format", "html") == "json":
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
    apps_list = _get_apps(request.user, '')

    partitions = None
    if app_name != 'impala' and table.partition_keys:
      try:
        partitions = [_massage_partition(database, table, partition) for partition in db.get_partitions(database, table)]
      except:
        LOG.exception('Table partitions could not be retrieved')

    return render(renderable, request, {
      'apps': apps_list,
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
      'is_navigator_enabled': has_catalog(request.user),
      'optimizer_url': get_optimizer_url(),
      'navigator_url': get_catalog_url(),
      'is_embeddable': request.GET.get('is_embeddable', False),
      'source_type': _get_servername(db),
    })


@check_has_write_access_permission
@require_http_methods(["POST"])
def alter_table(request, database, table):
  response = {'status': -1, 'data': ''}

  source_type = request.POST.get('source_type', 'hive')
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = _get_db(user=request.user, source_type=source_type, cluster=cluster)

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
  response = {'status': -1, 'message': ''}

  source_type = request.POST.get('source_type', 'hive')
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = _get_db(user=request.user, source_type=source_type, cluster=cluster)

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
  source_type = request.POST.get('source_type', request.GET.get('source_type', 'hive'))
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = _get_db(user=request.user, source_type=source_type, cluster=cluster)

  if request.method == 'POST':
    try:
      tables = request.POST.getlist('table_selection')
      tables_objects = [db.get_table(database, table) for table in tables]
      skip_trash = request.POST.get('skip_trash') == 'on'
      cluster = json.loads(request.POST.get('cluster', '{}'))
      namespace = request.POST.get('namespace')

      if request.POST.get('is_embeddable'):
        last_executed = json.loads(request.POST.get('start_time'), '-1')
        sql = db.drop_tables(database, tables_objects, design=None, skip_trash=skip_trash, generate_ddl_only=True)
        job = make_notebook(
            name=_('Drop table %s') % ', '.join([table.name for table in tables_objects])[:100],
            editor_type=source_type,
            statement=sql.strip(),
            status='ready',
            database=database,
            namespace=namespace,
            compute=cluster,
            on_success_url='assist.db.refresh',
            is_task=True,
            last_executed=last_executed
        )
        return JsonResponse(job.execute(request))
      else:
        # Can't be simpler without an important refactoring
        design = SavedQuery.create_empty(app_name='beeswax', owner=request.user, data=hql_query('').dumps())
        query_history = db.drop_tables(database, tables_objects, design, skip_trash=skip_trash)
        url = reverse('beeswax:watch_query_history', kwargs={'query_history_id': query_history.id}) + '?on_success_url=' + reverse('metastore:show_tables', kwargs={'database': database})
        return redirect(url)
    except Exception, ex:
      error_message, log = dbms.expand_exception(ex, db)
      error = _("Failed to remove %(tables)s.  Error: %(error)s") % {'tables': ','.join(tables), 'error': error_message}
      raise PopupException(error, title=_("DB Error"), detail=log)
  else:
    title = _("Do you really want to delete the table(s)?")
    return render('confirm.mako', request, {'url': request.path, 'title': title})


# Deprecated
def read_table(request, database, table):
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = dbms.get(request.user, cluster=cluster)
  table = db.get_table(database, table)

  try:
    query_history = db.select_star_from(database, table)
    url = reverse('beeswax:watch_query_history', kwargs={'query_history_id': query_history.id}) + '?on_success_url=&context=table:%s:%s' % (table.name, database)
    return redirect(url)
  except Exception, e:
    raise PopupException(_('Cannot read table'), detail=e)

@check_has_write_access_permission
def load_table(request, database, table):
  response = {'status': -1, 'data': 'None'}

  source_type = request.POST.get('source_type', request.GET.get('source_type', 'hive'))
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = _get_db(user=request.user, source_type=source_type, cluster=cluster)

  table = db.get_table(database, table)

  if request.method == "POST":
    load_form = LoadDataForm(table, request.POST)

    if load_form.is_valid():
      on_success_url = reverse('metastore:describe_table', kwargs={'database': database, 'table': table.name})
      generate_ddl_only = request.POST.get('is_embeddable', 'false') == 'true'
      try:
        design = SavedQuery.create_empty(app_name=source_type if source_type != 'hive' else 'beeswax', owner=request.user, data=hql_query('').dumps())
        form_data = {
          'path': load_form.cleaned_data['path'],
          'overwrite': load_form.cleaned_data['overwrite'],
          'partition_columns': [(column_name, load_form.cleaned_data[key]) for key, column_name in load_form.partition_columns.iteritems()],
        }
        query_history = db.load_data(database, table.name, form_data, design, generate_ddl_only=generate_ddl_only)
        if generate_ddl_only:
          last_executed = json.loads(request.POST.get('start_time'), '-1')
          job = make_notebook(
            name=_('Load data in %s.%s') % (database, table.name),
            editor_type=source_type,
            statement=query_history.strip(),
            status='ready',
            database=database,
            on_success_url='assist.db.refresh',
            is_task=True,
            last_executed=last_executed
          )
          response = job.execute(request)
        else:
          url = reverse('beeswax:watch_query_history', kwargs={'query_history_id': query_history.id}) + '?on_success_url=' + on_success_url
          response['status'] = 0
          response['data'] = url
          response['query_history_id'] = query_history.id
      except QueryError, ex:
        response['status'] = 1
        response['data'] = _("Can't load the data: ") + ex.message
      except Exception, e:
        response['status'] = 1
        response['data'] = _("Can't load the data: ") + str(e)
  else:
    load_form = LoadDataForm(table)

  if response['status'] == -1:
    popup = render('popups/load_data.mako', request, {
           'table': table,
           'load_form': load_form,
           'source_type': source_type,
           'database': database,
           'app_name': 'beeswax'
       }, force_template=True).content
    response['data'] = popup

  return JsonResponse(response)


def describe_partitions(request, database, table):
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = _get_db(user=request.user, cluster=cluster)
  table_obj = db.get_table(database, table)

  if not table_obj.partition_keys:
    raise PopupException(_("Table '%(table)s' is not partitioned.") % {'table': table})

  reverse_sort = request.GET.get("sort", "desc").lower() == "desc"

  if request.method == "POST":
    partition_filters = {}
    for part in table_obj.partition_keys:
      if request.GET.get(part.name):
        partition_filters[part.name] = request.GET.get(part.name)
    partition_spec = ','.join(["%s='%s'" % (k, v) for k, v in partition_filters.items()])
  else:
    partition_spec = ''

  try:
    partitions = db.get_partitions(database, table_obj, partition_spec, reverse_sort=reverse_sort)
  except:
    LOG.exception('Table partitions could not be retrieved')
    partitions = []
  massaged_partitions = [_massage_partition(database, table_obj, partition) for partition in partitions]

  if request.method == "POST" or request.GET.get('format', 'html') == 'json':
    return JsonResponse({
      'partition_keys_json': [partition.name for partition in table_obj.partition_keys],
      'partition_values_json': massaged_partitions,
    })
  else:
    apps_list = _get_apps(request.user, '')
    return render("metastore.mako", request, {
      'apps': apps_list,
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
        'is_navigator_enabled': has_catalog(request.user),
        'optimizer_url': get_optimizer_url(),
        'navigator_url': get_catalog_url(),
        'is_embeddable': request.GET.get('is_embeddable', False),
        'source_type': _get_servername(db),
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
    }),
   'notebookUrl': reverse('notebook:browse', kwargs={
        'database': database,
        'table': table.name,
        'partition_spec': urllib.quote(partition.partition_spec)
    })
  }


def browse_partition(request, database, table, partition_spec):
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = _get_db(user=request.user, cluster=cluster)
  try:
    decoded_spec = urllib.unquote(partition_spec)
    partition_table = db.describe_partition(database, table, decoded_spec)
    uri_path = location_to_url(partition_table.path_location)
    if request.GET.get("format", "html") == "json":
      return JsonResponse({'uri_path': uri_path})
    else:
      return redirect(uri_path)
  except Exception, e:
    raise PopupException(_('Cannot browse partition'), detail=e.message)


# Deprecated
def read_partition(request, database, table, partition_spec):
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = dbms.get(request.user, cluster=cluster)
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
  source_type = request.POST.get('source_type', 'hive')
  cluster = json.loads(request.POST.get('cluster', '{}'))

  db = _get_db(user=request.user, source_type=source_type, cluster=cluster)

  if request.method == 'POST':
    partition_specs = request.POST.getlist('partition_selection')
    partition_specs = [spec for spec in partition_specs]
    try:
      if request.GET.get("format", "html") == "json":
        last_executed = json.loads(request.POST.get('start_time'), '-1')
        sql = db.drop_partitions(database, table, partition_specs, design=None, generate_ddl_only=True)
        job = make_notebook(
            name=_('Drop partition %s') % ', '.join(partition_specs)[:100],
            editor_type=source_type,
            statement=sql.strip(),
            status='ready',
            database=None,
            on_success_url='assist.db.refresh',
            is_task=True,
            last_executed=last_executed
        )
        return JsonResponse(job.execute(request))
      else:
        design = SavedQuery.create_empty(app_name='beeswax', owner=request.user, data=hql_query('').dumps())
        query_history = db.drop_partitions(database, table, partition_specs, design)
        url = reverse('beeswax:watch_query_history', kwargs={'query_history_id': query_history.id}) + '?on_success_url=' + \
              reverse('metastore:describe_partitions', kwargs={'database': database, 'table': table})
        return redirect(url)
    except Exception, ex:
      error_message, log = dbms.expand_exception(ex, db)
      error = _("Failed to remove %(partition)s.  Error: %(error)s") % {'partition': '\n'.join(partition_specs), 'error': error_message}
      raise PopupException(error, title=_("DB Error"), detail=log)
  else:
    title = _("Do you really want to delete the partition(s)?")
    return render('confirm.mako', request, {'url': request.path, 'title': title})


def has_write_access(user):
  return is_admin(user) or user.has_hue_permission(action="write", app=DJANGO_APPS[0])



def _get_db(user, source_type=None, cluster=None):
  if source_type is None:
    cluster_config = get_cluster_config(user)
    if FORCE_HS2_METADATA.get() and cluster_config['app_config'].get('editor') and 'hive' in cluster_config['app_config'].get('editor')['interpreter_names']:
      source_type = 'hive'
    else:
      source_type = cluster_config['default_sql_interpreter']

  name = source_type if source_type != 'hive' else 'beeswax'

  query_server = get_query_server_config(name=name, cluster=cluster)
  return dbms.get(user, query_server)


def _get_servername(db):
  return 'hive' if db.server_name == 'beeswax' else db.server_name.rsplit('-', 1)[0]
