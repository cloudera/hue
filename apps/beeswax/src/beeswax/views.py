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
import re

from django import forms
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, QueryDict
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from desktop.context_processors import get_app_name
from desktop.lib.paginator import Paginator
from desktop.lib.django_util import copy_query_dict, format_preserving_redirect, render
from desktop.lib.django_util import login_notrequired, get_desktop_uri_prefix
from desktop.lib.exceptions_renderable import PopupException

from hadoop.fs.exceptions import WebHdfsException
from jobsub.parameterization import find_variables, substitute_variables
from beeswaxd.ttypes import BeeswaxException, QueryNotFoundException

import beeswax.forms
import beeswax.design
import beeswax.management.commands.beeswax_install_examples

from beeswax import common, data_export, models, conf
from beeswax.forms import LoadDataForm, QueryForm, DbForm
from beeswax.design import HQLdesign, hql_query
from beeswax.models import SavedQuery, make_query_context
from beeswax.server import dbms
from beeswax.server.dbms import expand_exception, get_query_server_config


LOG = logging.getLogger(__name__)
SAVE_RESULTS_CTAS_TIMEOUT = 300         # seconds



def index(request):
  try:
    tables = dbms.get(request.user).get_tables()
    if not tables:
      examples_installed = beeswax.models.MetaInstall.get().installed_example
      return render("index.mako", request, {'examples_installed': examples_installed})
  except:
    pass

  return execute_query(request)


"""
Design views
"""

def save_design(request, form, type, design, explicit_save):
  """
  save_design(request, form, type, design, explicit_save) -> SavedQuery

  A helper method to save the design:
    * If ``explicit_save``, then we save the data in the current design.
    * If the user clicked the submit button, we do NOT overwrite the current
      design. Instead, we create a new "auto" design (iff the user modified
      the data). This new design is named after the current design, with the
      AUTO_DESIGN_SUFFIX to signify that it's different.

  Need to return a SavedQuery because we may end up with a different one.
  Assumes that form.saveform is the SaveForm, and that it is valid.
  """
  assert form.saveform.is_valid()

  if type == models.SavedQuery.HQL:
    design_cls = beeswax.design.HQLdesign
  elif type == models.SavedQuery.IMPALA:
    design_cls = beeswax.design.HQLdesign
  else:
    raise ValueError(_('Invalid design type %(type)s') % {'type': type})

  old_design = design
  design_obj = design_cls(form)
  new_data = design_obj.dumps()

  # Auto save if (1) the user didn't click "save", and (2) the data is different.
  # Don't generate an auto-saved design if the user didn't change anything
  if explicit_save:
    design.name = form.saveform.cleaned_data['name']
    design.desc = form.saveform.cleaned_data['desc']
    design.is_auto = False
  elif new_data != old_design.data:
    # Auto save iff the data is different
    if old_design.id is not None:
      # Clone iff the parent design isn't a new unsaved model
      design = old_design.clone()
      if not old_design.is_auto:
        design.name = old_design.name + models.SavedQuery.AUTO_DESIGN_SUFFIX
    else:
      design.name = models.SavedQuery.DEFAULT_NEW_DESIGN_NAME
    design.is_auto = True

  design.type = type
  design.data = new_data

  design.save()

  LOG.info('Saved %s design "%s" (id %s) for %s' %
           (explicit_save and '' or 'auto ', design.name, design.id, design.owner))
  if explicit_save:
    messages.info(request, _('Saved design "%(name)s"') % {'name': design.name})
  # Design may now have a new/different id
  return design



def delete_design(request):
  if request.method == 'POST':
    ids = request.POST.getlist('designs_selection')
    designs = dict([(design_id, authorized_get_design(request, design_id)) for design_id in ids])

    if None in designs.values():
      LOG.error('Cannot delete non-existent design(s) %s' % ','.join([key for key, name in designs.items() if name is None]))
      return list_designs(request)
    for design in designs.values():
      design.delete()
    return redirect(reverse(get_app_name(request) + ':list_designs'))
  else:
    return render('confirm.html', request, dict(url=request.path, title=_('Delete design(s)?')))


def clone_design(request, design_id):
  """Clone a design belonging to any user"""
  design = authorized_get_design(request, design_id)

  if design is None:
    LOG.error('Cannot clone non-existent design %s' % (design_id,))
    return list_designs(request)

  copy = design.clone()
  copy.name = design.name + ' (copy)'
  copy.owner = request.user
  copy.save()
  messages.info(request, _('Copied design: %(name)s') % {'name': design.name})
  return format_preserving_redirect(
      request, reverse(get_app_name(request) + ':execute_query', kwargs={'design_id': copy.id}))


def list_designs(request):
  """
  View function for show all saved queries.

  We get here from /beeswax/list_designs?filterargs, with the options being:
    page=<n>    - Controls pagination. Defaults to 1.
    user=<name> - Show design items belonging to a user. Default to all users.
    type=<type> - <type> is "hql", for saved query type. Default to show all.
    sort=<key>  - Sort by the attribute <key>, which is one of:
                    "date", "name", "desc", and "type" (design type)
                  Accepts the form "-date", which sort in descending order.
                  Default to "-date".
    text=<frag> - Search for fragment "frag" in names and descriptions.

  Depending on Beeswax configuration parameter ``SHOW_ONLY_PERSONAL_SAVED_QUERIES``,
  only the personal queries of the user will be returned (even if another user is
  specified in ``filterargs``).
  """
  DEFAULT_PAGE_SIZE = 10
  app_name= get_app_name(request)

  if conf.SHARE_SAVED_QUERIES.get() or request.user.is_superuser:
    user = None
  else:
    user = request.user

  # Extract the saved query list.
  prefix = 'q-'
  querydict_query = _copy_prefix(prefix, request.GET)
  # Manually limit up the user filter.
  querydict_query[ prefix + 'user' ] = user
  querydict_query[ prefix + 'type' ] = app_name
  page, filter_params = _list_designs(querydict_query, DEFAULT_PAGE_SIZE, prefix)

  return render('list_designs.mako', request, {
    'page': page,
    'filter_params': filter_params,
    'user': request.user,
    'designs_json': json.dumps([query.id for query in page.object_list])
  })


def my_queries(request):
  """
  View a mix of history and saved queries.
  It understands all the GET params in ``list_query_history`` (with a ``h-`` prefix)
  and those in ``list_designs`` (with a ``q-`` prefix). The only thing it disallows
  is the ``user`` filter, since this view only shows what belongs to the user.
  """
  DEFAULT_PAGE_SIZE = 40
  app_name= get_app_name(request)

  # Extract the history list.
  prefix = 'h-'
  querydict_history = _copy_prefix(prefix, request.GET)
  # Manually limit up the user filter.
  querydict_history[ prefix + 'user' ] = request.user.username
  querydict_history[ prefix + 'type' ] = app_name

  hist_page, hist_filter = _list_query_history(request.user,
                                               querydict_history,
                                               DEFAULT_PAGE_SIZE,
                                               prefix)
  # Extract the saved query list.
  prefix = 'q-'
  querydict_query = _copy_prefix(prefix, request.GET)
  # Manually limit up the user filter.
  querydict_query[ prefix + 'user' ] = request.user.username
  querydict_query[ prefix + 'type' ] = app_name

  query_page, query_filter = _list_designs(querydict_query, DEFAULT_PAGE_SIZE, prefix)

  filter_params = hist_filter
  filter_params.update(query_filter)

  return render('my_queries.mako', request, {
    'request': request,
    'h_page': hist_page,
    'q_page': query_page,
    'filter_params': filter_params,
    'designs_json': json.dumps([query.id for query in query_page.object_list])
  })


def list_query_history(request):
  """
  View the history of query (for the current user).
  We get here from /beeswax/query_history?filterargs, with the options being:
    page=<n>            - Controls pagination. Defaults to 1.
    user=<name>         - Show history items from a user. Default to current user only.
                          Also accepts ':all' to show all history items.
    type=<type>         - <type> is "report|hql", for design type. Default to show all.
    design_id=<id>      - Show history for this particular design id.
    sort=<key>          - Sort by the attribute <key>, which is one of:
                            "date", "state", "name" (design name), and "type" (design type)
                          Accepts the form "-date", which sort in descending order.
                          Default to "-date".
    auto_query=<bool>   - Show auto generated actions (drop table, read data, etc). Default False
  """
  DEFAULT_PAGE_SIZE = 20

  share_queries = conf.SHARE_SAVED_QUERIES.get() or request.user.is_superuser

  querydict_query = request.GET.copy()
  if not share_queries:
    querydict_query['user'] = request.user.username

  app_name= get_app_name(request)
  querydict_query['type'] = app_name

  page, filter_params = _list_query_history(request.user, querydict_query, DEFAULT_PAGE_SIZE)

  return render('list_history.mako', request, {
    'request': request,
    'page': page,
    'filter_params': filter_params,
    'share_queries': share_queries,
  })


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
  examples_installed = beeswax.models.MetaInstall.get().installed_example

  return render("show_tables.mako", request, {
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
  except BeeswaxException, ex:
    error_message, logs = expand_exception(ex, db)

  load_form = LoadDataForm(table)

  return render("describe_table.mako", request, {
      'table': table,
      'sample': table_data and table_data.rows(),
      'load_form': load_form,
      'error_message': error_message,
      'database': database,
  })


def drop_table(request, database):
  db = dbms.get(request.user)

  if request.method == 'POST':
    tables = request.POST.getlist('table_selection')
    tables_objects = [db.get_table(database, table) for table in tables]
    app_name = get_app_name(request)
    try:
      # Can't be simpler without an important refactoring
      design = SavedQuery.create_empty(app_name=app_name, owner=request.user)
      query_history = db.drop_tables(database, tables_objects, design)
      url = reverse(app_name + ':watch_query', args=[query_history.id]) + '?on_success_url=' + reverse(app_name + ':show_tables')
      return redirect(url)
    except BeeswaxException, ex:
      error_message, log = expand_exception(ex, db)
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
    get = request.GET.copy()
    get['context'] = 'table:%s:%s' % (table.name, database)
    request.GET = get
    return watch_query(request, history.id)
  except Exception, e:
    raise PopupException(_('Can read table'), detail=e)


def load_table(request, database, table):
  table_obj = dbms.get(request.user).get_table(database, table)

  if request.method == "POST":
    form = beeswax.forms.LoadDataForm(table_obj, request.POST)
    if form.is_valid():
      # TODO(philip/todd): When PathField might refer to non-HDFS,
      # we need a pathfield.is_local function.
      hql = "LOAD DATA INPATH"
      hql += " '%s'" % form.cleaned_data['path']
      if form.cleaned_data['overwrite']:
        hql += " OVERWRITE"
      hql += " INTO TABLE "
      hql += "`%s.%s`" % (database, table,)
      if form.partition_columns:
        hql += " PARTITION ("
        vals = []
        for key, column_name in form.partition_columns.iteritems():
          vals.append("%s='%s'" % (column_name, form.cleaned_data[key]))
        hql += ", ".join(vals)
        hql += ")"

      on_success_url = reverse(get_app_name(request) + ':describe_table', kwargs={'database': database, 'table': table})
      return confirm_query(request, hql, on_success_url)
  else:
    form = beeswax.forms.LoadDataForm(table_obj)
    return render("load_table.mako", request, {'form': form, 'table': table, 'action': request.get_full_path()})


def describe_partitions(request, database, table):
  db = dbms.get(request.user)

  table_obj = db.get_table(database, table)
  if not table_obj.partition_keys:
    raise PopupException(_("Table '%(table)s' is not partitioned.") % {'table': table})

  partitions = db.get_partitions(database, table_obj, max_parts=None)

  return render("describe_partitions.mako", request,
                dict(table=table_obj, partitions=partitions, request=request))


def download(request, id, format):
  assert format in common.DL_FORMATS

  query_history = authorized_get_history(request, id, must_exist=True)
  db = dbms.get(request.user, query_history.get_query_server_config())
  LOG.debug('Download results for query %s: [ %s ]' % (query_history.server_id, query_history.query))

  return data_export.download(query_history.get_handle(), format, db)



"""
Queries Views
"""

def execute_query(request, design_id=None):
  """
  View function for executing an arbitrary query.
  It understands the optional GET/POST params:

    on_success_url
      If given, it will be displayed when the query is successfully finished.
      Otherwise, it will display the view query results page by default.
  """
  authorized_get_design(request, design_id)

  error_message = None
  form = QueryForm()
  action = request.path
  log = None
  app_name = get_app_name(request)
  query_type = SavedQuery.TYPES_MAPPING[app_name]
  design = safe_get_design(request, query_type, design_id)
  on_success_url = request.REQUEST.get('on_success_url')

  query_server = get_query_server_config(app_name, requires_ddl=False)
  db = dbms.get(request.user, query_server)
  databases = ((db, db) for db in db.get_databases())

  if request.method == 'POST':
    form.bind(request.POST)
    form.query.fields['database'].choices =  databases # Could not do it in the form

    to_explain = request.POST.has_key('button-explain')
    to_submit = request.POST.has_key('button-submit')

    # Always validate the saveform, which will tell us whether it needs explicit saving
    if form.is_valid():
      to_save = form.saveform.cleaned_data['save']
      to_saveas = form.saveform.cleaned_data['saveas']

      if to_saveas and not design.is_auto:
        # Save As only affects a previously saved query
        design = design.clone()

      if to_submit or to_save or to_saveas or to_explain:
        explicit_save = to_save or to_saveas
        design = save_design(request, form, query_type, design, explicit_save)
        action = reverse(app_name + ':execute_query', kwargs=dict(design_id=design.id))

      if to_explain or to_submit:
        query_str = form.query.cleaned_data["query"]

        # (Optional) Parameterization.
        parameterization = get_parameterization(request, query_str, form, design, to_explain)
        if parameterization:
          return parameterization

        try:
          query = HQLdesign(form)
          if to_explain:
            return explain_directly(request, query, design, query_server)
          else:
            download = request.POST.has_key('download')
            return execute_directly(request, query, query_server, design, on_success_url=on_success_url, download=download)
        except BeeswaxException, ex:
          print ex.errorCode
          print ex.SQLState
          error_message, log = expand_exception(ex, db)
  else:
    if design.id is not None:
      data = HQLdesign.loads(design.data).get_query_dict()
      form.bind(data)
      form.saveform.set_data(design.name, design.desc)
    else:
      # New design
      form.bind()
    form.query.fields['database'].choices = databases # Could not do it in the form

  return render('execute.mako', request, {
    'action': action,
    'design': design,
    'error_message': error_message,
    'form': form,
    'log': log,
    'on_success_url': on_success_url,
  })


def execute_parameterized_query(request, design_id):
  return _run_parameterized_query(request, design_id, False)


def explain_parameterized_query(request, design_id):
  return _run_parameterized_query(request, design_id, True)


def watch_query(request, id):
  """
  Wait for the query to finish and (by default) displays the results of query id.
  It understands the optional GET params:

    on_success_url
      If given, it will be displayed when the query is successfully finished.
      Otherwise, it will display the view query results page by default.

    context
      A string of "name:data" that describes the context
      that generated this query result. It may be:
        - "table":"<table_name>"
        - "design":<design_id>

  All other GET params will be passed to on_success_url (if present).
  """
  # Coerce types; manage arguments
  query_history = authorized_get_history(request, id, must_exist=True)
  db = dbms.get(request.user, query_history.get_query_server_config())

  # GET param: context.
  context_param = request.GET.get('context', '')

  # GET param: on_success_url. Default to view_results
  results_url = reverse(get_app_name(request) + ':view_results', kwargs={'id': id, 'first_row': 0})
  if request.GET.get('download', ''):
    results_url += '?download=true'
  on_success_url = request.GET.get('on_success_url')
  if not on_success_url:
    on_success_url = results_url

  # Go to next statement if asked to continue or when a statement with no dataset finished.
  if request.method == 'POST' or (not query_history.is_finished() and query_history.is_success() and not query_history.has_results):
    try:
      query_history = db.execute_next_statement(query_history)
    except BeeswaxException, ex:
      pass

  # Check query state
  handle, state = _get_query_handle_and_state(query_history)
  query_history.save_state(state)

  if query_history.is_failure():
    # When we fetch, Beeswax server will throw us a BeeswaxException, which has the
    # log we want to display.
    return format_preserving_redirect(request, results_url, request.GET)
  elif query_history.is_finished() or (query_history.is_success() and query_history.has_results):
    return format_preserving_redirect(request, on_success_url, request.GET)

  # Still running
  log = db.get_log(handle)

  # Keep waiting
  # - Translate context into something more meaningful (type, data)
  query_context = _parse_query_context(context_param)

  return render('watch_wait.mako', request, {
                'query': query_history,
                'fwd_params': request.GET.urlencode(),
                'log': log,
                'hadoop_jobs': _parse_out_hadoop_jobs(log),
                'query_context': query_context,
              })

def watch_query_refresh_json(request, id):
  query_history = authorized_get_history(request, id, must_exist=True)
  db = dbms.get(request.user, query_history.get_query_server_config())
  handle, state = _get_query_handle_and_state(query_history)
  query_history.save_state(state)

  try:
    if not query_history.is_finished() and query_history.is_success() and not query_history.has_results:
      db.execute_next_statement(query_history)
      handle, state = _get_query_handle_and_state(query_history)    
  except BeeswaxException, ex:
    handle, state = _get_query_handle_and_state(query_history)
    
  log = db.get_log(handle)
  jobs = _parse_out_hadoop_jobs(log)
  job_urls = dict([(job, reverse('jobbrowser.views.single_job', kwargs=dict(job=job))) for job in jobs])

  result = {
    'log': log,
    'jobs': jobs,
    'jobUrls': job_urls,
    'isSuccess': query_history.is_finished() or (query_history.is_success() and query_history.has_results),
    'isFailure': query_history.is_failure()
  }

  return HttpResponse(json.dumps(result), mimetype="application/json")


def view_results(request, id, first_row=0):
  """
  Returns the view for the results of the QueryHistory with the given id.

  The query results MUST be ready.
  To display query results, one should always go through the watch_query view.

  If ``first_row`` is 0, restarts (if necessary) the query read.  Otherwise, just
  spits out a warning if first_row doesn't match the servers conception.
  Multiple readers will produce a confusing interaction here, and that's known.

  It understands the ``context`` GET parameter. (See watch_query().)
  """
  first_row = long(first_row)
  start_over = (first_row == 0)
  results = None
  data = None
  fetch_error = False
  error_message = ''
  log = ''
  app_name = get_app_name(request)

  query_history = authorized_get_history(request, id, must_exist=True)
  db = dbms.get(request.user, query_history.get_query_server_config())

  handle, state = _get_query_handle_and_state(query_history)
  context_param = request.GET.get('context', '')
  query_context = _parse_query_context(context_param)

  # To remove in Hue 2.3
  download  = request.GET.get('download', '')

  # Update the status as expired should not be accessible
  # Impala does not support startover for now
  expired = state == models.QueryHistory.STATE.expired
  if expired or app_name == 'impala':
    state = models.QueryHistory.STATE.expired
    query_history.save_state(state)

  # Retrieve query results
  try:
    if not download:
      results = db.fetch(handle, start_over, 100)
      data = list(results.rows()) # Materialize results

      # We display the "Download" button only when we know that there are results:
      downloadable = first_row > 0 or data
    else:
      downloadable = True
      data = []
      results = type('Result', (object,), {
                    'rows': 0,
                    'columns': [],
                    'has_more': False,
                    'start_row': 0, })
    log = db.get_log(handle)
  except Exception, ex:
    fetch_error = True
    error_message, log = expand_exception(ex, db)

  # Handle errors
  error = fetch_error or results is None or expired

  context = {
    'error': error,
    'error_message': error_message,
    'query': query_history,
    'results': data,
    'expected_first_row': first_row,
    'log': log,
    'hadoop_jobs': app_name != 'impala' and _parse_out_hadoop_jobs(log),
    'query_context': query_context,
    'can_save': False,
    'context_param': context_param,
    'expired': expired,
    'app_name': app_name,
    'download': download
  }

  if not error:
    download_urls = {}
    if downloadable:
      for format in common.DL_FORMATS:
        download_urls[format] = reverse(app_name + ':download', kwargs=dict(id=str(id), format=format))

    save_form = beeswax.forms.SaveResultsForm()
    results.start_row = first_row

    context.update({
      'results': data,
      'has_more': results.has_more,
      'next_row': results.start_row + len(data),
      'start_row': results.start_row,
      'expected_first_row': first_row,
      'columns': results.columns,
      'download_urls': download_urls,
      'save_form': save_form,
      'can_save': query_history.owner == request.user and not download,
    })

  return render('watch_results.mako', request, context)


def save_results(request, id):
  """
  Save the results of a query to an HDFS directory
  """
  query_history = authorized_get_history(request, id, must_exist=True)

  server_id, state = _get_query_handle_and_state(query_history)
  query_history.save_state(state)
  error_msg, log = None, None

  if request.method == 'POST':
    # Make sure the result is available.
    # Note that we may still hit errors during the actual save
    if not query_history.is_success():
      if query_history.is_failure():
        msg = _('This query has %(state)s. Results unavailable.') % {'state': state}
      else:
        msg = _('The result of this query is not available yet.')
      raise PopupException(msg)

    db = dbms.get(request.user, query_history.get_query_server_config())
    form = beeswax.forms.SaveResultsForm(request.POST, db=db)

    # Cancel goes back to results
    if request.POST.get('cancel'):
      return format_preserving_redirect(request, '/beeswax/watch/%s' % (id,))

    if form.is_valid():
      # Do save
      # 1. Get the results metadata
      assert request.POST.get('save')
      try:
        handle, state = _get_query_handle_and_state(query_history)
        result_meta = db.get_results_metadata(handle)
      except QueryNotFoundException, ex:
        LOG.exception(ex)
        raise PopupException(_('Cannot find query.'))
      if result_meta.table_dir:
        result_meta.table_dir = request.fs.urlsplit(result_meta.table_dir)[2]

      # 2. Check for partitioned tables
      if result_meta.table_dir is None:
        raise PopupException(_('Saving results from a partitioned table is not supported. You may copy from the HDFS location manually.'))

      # 3. Actual saving of results
      try:
        if form.cleaned_data['save_target'] == form.SAVE_TYPE_DIR:
          # To dir
          if result_meta.in_tablename:
            raise PopupException(_('Saving results from a query with no MapReduce jobs is not supported. '
                                   'You may copy manually from the HDFS location %(path)s.') % {'path': result_meta.table_dir})
          target_dir = form.cleaned_data['target_dir']
          request.fs.rename_star(result_meta.table_dir, target_dir)
          LOG.debug("Moved results from %s to %s" % (result_meta.table_dir, target_dir))
          query_history.save_state(models.QueryHistory.STATE.expired)
          return redirect(reverse('filebrowser.views.view', kwargs={'path': target_dir}))
        elif form.cleaned_data['save_target'] == form.SAVE_TYPE_TBL:
          # To new table
          try:
            return _save_results_ctas(request, query_history, form.cleaned_data['target_table'], result_meta)
          except BeeswaxException, bex:
            LOG.exception(bex)
            error_msg, log = expand_exception(bex, db)
      except WebHdfsException, ex:
        raise PopupException(_('The table could not be saved.'), detail=ex)
      except IOError, ex:
        LOG.exception(ex)
        error_msg = str(ex)
  else:
    form = beeswax.forms.SaveResultsForm()

  if error_msg:
    error_msg = _('Failed to save results from query: %(error)s') % {'error': error_msg}
  return render('save_results.mako', request, dict(
    action=reverse(get_app_name(request) + ':save_results', kwargs={'id': str(id)}),
    form=form,
    error_msg=error_msg,
    log=log,
  ))


def _save_results_ctas(request, query_history, target_table, result_meta):
  """
  Handle saving results as a new table. Returns HTTP response.
  May raise BeeswaxException, IOError.
  """
  query_server = query_history.get_query_server_config() # Query server requires DDL support
  db = dbms.get(request.user)

  # Case 1: The results are straight from an existing table
  if result_meta.in_tablename:
    hql = 'CREATE TABLE `%s` AS SELECT * FROM %s' % (target_table, result_meta.in_tablename)
    query = hql_query(hql)
    # Display the CTAS running. Could take a long time.
    return execute_directly(request, query, query_server, on_success_url=reverse(get_app_name(request) + ':show_tables'))

  # Case 2: The results are in some temporary location
  # 1. Create table
  cols = ''
  schema = result_meta.schema
  for i, field in enumerate(schema.fieldSchemas):
    if i != 0:
      cols += ',\n'
    cols += '`%s` %s' % (field.name, field.type)

  # The representation of the delimiter is messy.
  # It came from Java as a string, which might has been converted from an integer.
  # So it could be "1" (^A), or "10" (\n), or "," (a comma literally).
  delim = result_meta.delim
  if not delim.isdigit():
    delim = str(ord(delim))

  hql = '''
        CREATE TABLE `%s` (
        %s
        )
        ROW FORMAT DELIMITED
        FIELDS TERMINATED BY '\%s'
        STORED AS TextFile
        ''' % (target_table, cols, delim.zfill(3))

  query = hql_query(hql)
  db.execute_and_wait(query)

  try:
    # 2. Move the results into the table's storage
    table_obj = db.get_table('default', target_table)
    table_loc = request.fs.urlsplit(table_obj.path_location)[2]
    request.fs.rename_star(result_meta.table_dir, table_loc)
    LOG.debug("Moved results from %s to %s" % (result_meta.table_dir, table_loc))
    messages.info(request, _('Saved query results as new table %(table)s') % {'table': target_table})
    query_history.save_state(models.QueryHistory.STATE.expired)
  except Exception, ex:
    LOG.error('Error moving data into storage of table %s. Will drop table.' % (target_table,))
    query = hql_query('DROP TABLE `%s`' % (target_table,))
    try:
      db.execute_directly(query)        # Don't wait for results
    except Exception, double_trouble:
      LOG.exception('Failed to drop table "%s" as well: %s' % (target_table, double_trouble))
    raise ex

  # Show tables upon success
  return format_preserving_redirect(request, reverse(get_app_name(request) + ':show_tables'))


def confirm_query(request, query, on_success_url=None):
  """
  Used by other forms to confirm a query before it's executed.
  The form is the same as execute_query below.

  query - The HQL about to be executed
  on_success_url - The page to go to upon successful execution
  """
  mform = QueryForm()
  mform.bind()
  mform.query.initial = dict(query=query)

  return render('execute.mako', request, {
    'form': mform,
    'action': reverse(get_app_name(request) + ':execute_query'),
    'error_message': None,
    'design': None,
    'on_success_url': on_success_url,
    'design': None,
  })


def explain_directly(request, query, design, query_server):
  explanation = dbms.get(request.user, query_server).explain(query)
  context = ("design", design)

  return render('explain.mako', request, dict(query=query, explanation=explanation.textual, query_context=context))


def configuration(request):
  app_name = get_app_name(request)
  query_server = get_query_server_config(app_name)
  config_values = dbms.get(request.user, query_server).get_default_configuration(
                      bool(request.REQUEST.get("include_hadoop", False)))
  for value in config_values:
    if 'password' in value.key.lower():
      value.value = "*" * 10
  return render("configuration.mako", request, {'config_values': config_values})


"""
Other views
"""

def install_examples(request):
  """
  Handle installing sample data and example queries.
  """
  if request.method == 'GET':
    return render('confirm.html', request,
                  dict(url=request.path, title=_('Install sample tables and Beeswax examples?')))
  elif request.method == 'POST':
    result = {}
    result['creationSucceeded'] = False
    result['message'] = ''
    try:
      beeswax.management.commands.beeswax_install_examples.Command().handle_noargs()
      if models.MetaInstall.get().installed_example:
        result['creationSucceeded'] = True
    except Exception, err:
      LOG.exception(err)
      result['message'] = str(err)

    return HttpResponse(json.dumps(result), mimetype="application/json")


@login_notrequired
def query_done_cb(request, server_id):
  """
  A callback for query completion notification. When the query is done,
  BeeswaxServer notifies us by sending a GET request to this view.

  This view should always return a 200 response, to reflect that the
  notification is delivered to the right view.
  """
  message_template = '<html><head></head>%(message)s<body></body></html>'
  message = {'message': 'error'}

  try:
    query_history = models.QueryHistory.objects.get(server_id=server_id)

    # Update the query status
    query_history.set_to_available()

    # Find out details about the query
    if not query_history.notify:
      message['message'] = 'email_notify is false'
      return HttpResponse(message_template % message)

    design = query_history.design
    user = query_history.owner
    subject = _("Beeswax query completed")

    if design:
      subject += ": %s" % (design.name,)

    link = "%s%s" % \
              (get_desktop_uri_prefix(),
               reverse(get_app_name(request) + ':watch_query', kwargs={'id': query_history.id}))
    body = _("%(subject)s. You may see the results here: %(link)s\n\nQuery:\n%(query)s") % {
               'subject': subject, 'link': link, 'query': query_history.query
             }

    user.email_user(subject, body)
    message['message'] = 'sent'
  except Exception, ex:
    msg = "Failed to send query completion notification via e-mail: %s" % (ex)
    LOG.error(msg)
    message['message'] = msg
  return HttpResponse(message_template % message)



"""
Utils
"""

def authorized_get_design(request, design_id, owner_only=False, must_exist=False):
  if design_id is None and not must_exist:
    return None
  try:
    design = models.SavedQuery.objects.get(id=design_id)
  except models.SavedQuery.DoesNotExist:
    if must_exist:
      raise PopupException(_('Design %(id)s does not exist.') % {'id': design_id})
    else:
      return None

  if not conf.SHARE_SAVED_QUERIES.get() and (not request.user.is_superuser or owner_only) \
      and design.owner != request.user:
    raise PopupException(_('Cannot access design %(id)s') % {'id': design_id})
  else:
    return design

def authorized_get_history(request, query_history_id, owner_only=False, must_exist=False):
  if query_history_id is None and not must_exist:
    return None
  try:
    query_history = models.QueryHistory.get(id=query_history_id)
  except models.QueryHistory.DoesNotExist:
    if must_exist:
      raise PopupException(_('QueryHistory %(id)s does not exist.') % {'id': query_history_id})
    else:
      return None

  if not conf.SHARE_SAVED_QUERIES.get() and (not request.user.is_superuser or owner_only) \
      and query_history.owner != request.user:
    raise PopupException(_('Cannot access QueryHistory %(id)s') % {'id': query_history_id})
  else:
    return query_history


def safe_get_design(request, design_type, design_id=None):
  """
  Return a new design, if design_id is None,
  Return the design with the given id and type. If the design is not found,
  display a notification and return a new design.
  """
  design = None

  if design_id is not None:
    try:
      design = models.SavedQuery.get(design_id, request.user, design_type)
    except models.SavedQuery.DoesNotExist:
      messages.error(request, _('Design does not exist'))

  if design is None:
    design = models.SavedQuery(owner=request.user, type=design_type)

  return design

def get_parameterization(request, query_str, form, design, is_explain):
  """
  Figures out whether a design is parameterizable, and, if so,
  returns a form to fill out.  Returns None if there's no parameterization
  to do.
  """
  if form.query.cleaned_data["is_parameterized"]:
    parameters_form = make_parameterization_form(query_str)
    if parameters_form:
      return render("parameterization.mako", request, dict(
        form=parameters_form(prefix="parameterization"),
        design=design,
        explain=is_explain))
  return None

def make_parameterization_form(query_str):
  """
  Creates a django form on the fly with arguments from the
  query.
  """
  variables = find_variables(query_str)
  if len(variables) > 0:
    class Form(forms.Form):
      for name in sorted(variables):
        locals()[name] = forms.CharField(required=True)
    return Form
  else:
    return None


def _run_parameterized_query(request, design_id, explain):
  """
  Given a design and arguments to parameterize that design, runs the query.
  - explain is a boolean to determine whether to run as an explain or as an
  execute.

  This is an extra "step" in the flow from execute_query.
  """
  design = authorized_get_design(request, design_id, must_exist=True)

  # Reconstitute the form
  design_obj = beeswax.design.HQLdesign.loads(design.data)
  query_form = QueryForm()
  params = design_obj.get_query_dict()
  params.update(request.POST)
  query_form.bind(params)
  assert query_form.is_valid()

  query_str = query_form.query.cleaned_data["query"]
  query_server = get_query_server_config(get_app_name(request))

  parameterization_form_cls = make_parameterization_form(query_str)
  if not parameterization_form_cls:
    raise PopupException(_("Query is not parameterizable."))

  parameterization_form = parameterization_form_cls(request.REQUEST, prefix="parameterization")

  if parameterization_form.is_valid():
    real_query = substitute_variables(query_str, parameterization_form.cleaned_data)
    query = HQLdesign(query_form)
    query._data_dict['query']['query'] = real_query
    try:
      if explain:
        return explain_directly(request, query, design, query_server)
      else:
        return execute_directly(request, query, query_server, design)
    except BeeswaxException, ex:
      db = dbms.get(request.user, query_server)
      error_message, log = expand_exception(ex, db)
      return render('execute.mako', request, {
        'action': reverse(get_app_name(request) + ':execute_query'),
        'design': design,
        'error_message': error_message,
        'form': query_form,
        'log': log,
      })
  else:
    return render("parameterization.mako", request, dict(form=parameterization_form, design=design, explain=explain))


def execute_directly(request, query, query_server=None, design=None, tablename=None,
                     on_success_url=None, on_success_params=None, **kwargs):
  """
  execute_directly(request, query_msg, tablename, design) -> HTTP response for execution

  This method wraps around dbms.execute_query() to take care of the HTTP response
  after the execution.

    query
      The HQL model Query object.

    query_server
      To which Query Server to submit the query.
      Dictionary with keys: ['server_name', 'server_host', 'server_port'].

    design
      The design associated with the query.

    tablename
      The associated table name for the context.

    on_success_url
      Where to go after the query is done. The URL handler may expect an option "context" GET
      param. (See ``watch_query``.) For advanced usage, on_success_url can be a function, in
      which case the on complete URL is the return of:
        on_success_url(history_obj) -> URL string
      Defaults to the view results page.

    on_success_params
      Optional params to pass to the on_success_url (in additional to "context").

  Note that this may throw a Beeswax exception.
  """
  if design is not None:
    authorized_get_design(request, design.id)

  db = dbms.get(request.user, query_server)
  database = query.query.get('database', 'default')
  db.use(database)

  history_obj = db.execute_query(query, design)

  watch_url = reverse(get_app_name(request) + ':watch_query', kwargs={'id': history_obj.id})
  if 'download' in kwargs and kwargs['download']:
    watch_url += '?download=true'

  # Prepare the GET params for the watch_url
  get_dict = QueryDict(None, mutable=True)
  # (1) context
  if design:
    get_dict['context'] = make_query_context('design', design.id)
  elif tablename:
    get_dict['context'] = make_query_context('table', '%s:%s' % (tablename, database))

  # (2) on_success_url
  if on_success_url:
    if callable(on_success_url):
      on_success_url = on_success_url(history_obj)
    get_dict['on_success_url'] = on_success_url

  # (3) misc
  if on_success_params:
    get_dict.update(on_success_params)

  return format_preserving_redirect(request, watch_url, get_dict)


def _list_designs(querydict, page_size, prefix=""):
  """
  _list_designs(querydict, page_size, prefix, user) -> (page, filter_param)

  A helper to gather the designs page. It understands all the GET params in
  ``list_designs``, by reading keys from the ``querydict`` with the given ``prefix``.
  If a ``user`` is specified, only the saved queries of this user will be returned.
  This has priority over the ``user`` in the ``querydict`` parameter.
  """
  DEFAULT_SORT = ('-', 'date')                  # Descending date

  SORT_ATTR_TRANSLATION = dict(
    date='mtime',
    name='name',
    desc='desc',
    type='type',
  )

  # Filtering. Only display designs explicitly saved.
  db_queryset = models.SavedQuery.objects.filter(is_auto=False)

  user = querydict.get(prefix + 'user')
  if user is not None:
    db_queryset = db_queryset.filter(owner__username=user)

  # Design type
  d_type = querydict.get(prefix + 'type')
  if d_type:
    d_type = str(d_type)
    if d_type not in SavedQuery.TYPES_MAPPING.keys():
      LOG.warn('Bad parameter to list_designs: type=%s' % (d_type,))
    else:
      db_queryset = db_queryset.filter(type=SavedQuery.TYPES_MAPPING[d_type])

  # Text search
  frag = querydict.get(prefix + 'text')
  if frag:
    db_queryset = db_queryset.filter(Q(name__icontains=frag) | Q(desc__icontains=frag))

  # Ordering
  sort_key = querydict.get(prefix + 'sort')
  if sort_key:
    if sort_key[0] == '-':
      sort_dir, sort_attr = '-', sort_key[1:]
    else:
      sort_dir, sort_attr = '', sort_key

    if not SORT_ATTR_TRANSLATION.has_key(sort_attr):
      LOG.warn('Bad parameter to list_designs: sort=%s' % (sort_key,))
      sort_dir, sort_attr = DEFAULT_SORT
  else:
    sort_dir, sort_attr = DEFAULT_SORT
  db_queryset = db_queryset.order_by(sort_dir + SORT_ATTR_TRANSLATION[sort_attr])

  pagenum = int(querydict.get(prefix + 'page', 1))
  paginator = Paginator(db_queryset, page_size)
  page = paginator.page(pagenum)

  # We need to pass the parameters back to the template to generate links
  keys_to_copy = [ prefix + key for key in ('user', 'type', 'sort') ]
  filter_params = copy_query_dict(querydict, keys_to_copy)

  return page, filter_params


def _get_query_handle_and_state(query_history):
  """
  Front-end wrapper to handle exceptions. Expects the query to be submitted.
  """
  handle = query_history.get_handle()

  if handle is None:
    raise PopupException(_("Failed to retrieve query state from the Query Server."))

  state = dbms.get(query_history.owner, query_history.get_query_server_config()).get_state(handle)

  if state is None:
    raise PopupException(_("Failed to contact Beeswax Server to check query status."))
  return (handle, state)


def _parse_query_context(context):
  """
  _parse_query_context(context) -> ('table', <table_name>) -or- ('design', <design_obj>)
  """
  if not context:
    return None
  pair = context.split(':', 1)
  if len(pair) != 2 or pair[0] not in ('table', 'design'):
    LOG.error("Invalid query context data: %s" % (context,))
    return None

  if pair[0] == 'design':       # Translate design id to design obj
    pair[1] = models.SavedQuery.get(int(pair[1]))
  return pair


HADOOP_JOBS_RE = re.compile("(http[^\s]*/jobdetails.jsp\?jobid=([a-z0-9_]*))")
HADOOP_YARN_JOBS_RE = re.compile("(http[^\s]*/proxy/([a-z0-9_]+?)/)")

def _parse_out_hadoop_jobs(log):
  """
  Ideally, Hive would tell us what jobs it has run directly
  from the Thrift interface.  For now, we parse the logs
  to look for URLs to those jobs.
  """
  ret = []

  for match in HADOOP_JOBS_RE.finditer(log):
    full_job_url, job_id = match.groups()
    # We ignore full_job_url for now, but it may
    # come in handy if we support multiple MR clusters
    # correctly.

    # Ignore duplicates
    if job_id not in ret:
      ret.append(job_id)

  for match in HADOOP_YARN_JOBS_RE.finditer(log):
    full_job_url, job_id = match.groups()
    if job_id not in ret:
      ret.append(job_id)

  return ret


def _copy_prefix(prefix, base_dict):
  """Copy keys starting with ``prefix``"""
  querydict = QueryDict(None, mutable=True)
  for key, val in base_dict.iteritems():
    if key.startswith(prefix):
      querydict[key] = val
  return querydict


def _list_query_history(user, querydict, page_size, prefix=""):
  """
  _list_query_history(user, querydict, page_size, prefix) -> (page, filter_param)

  A helper to gather the history page. It understands all the GET params in
  ``list_query_history``, by reading keys from the ``querydict`` with the
  given ``prefix``.
  """
  DEFAULT_SORT = ('-', 'date')                  # Descending date

  SORT_ATTR_TRANSLATION = dict(
    date='submission_date',
    state='last_state',
    name='design__name',
    type='design__type',
  )

  db_queryset = models.QueryHistory.objects.select_related()

  # Filtering
  #
  # Queries without designs are the ones we submitted on behalf of the user,
  # (e.g. view table data). Exclude those when returning query history.
  if not querydict.get(prefix + 'auto_query', False):
    db_queryset = db_queryset.filter(design__isnull=False)

  username = user.username
  user_filter = querydict.get(prefix + 'user', user.username)
  if user_filter != ':all':
    db_queryset = db_queryset.filter(owner__username=user_filter)

  # Design id
  design_id = querydict.get(prefix + 'design_id')
  if design_id:
    db_queryset = db_queryset.filter(design__id=int(design_id))

  # Design type
  d_type = querydict.get(prefix + 'type')
  if d_type:
    if d_type not in SavedQuery.TYPES_MAPPING.keys():
      LOG.warn('Bad parameter to list_query_history: type=%s' % (d_type,))
    else:
      db_queryset = db_queryset.filter(design__type=SavedQuery.TYPES_MAPPING[d_type])

  # Ordering
  sort_key = querydict.get(prefix + 'sort')
  if sort_key:
    sort_dir, sort_attr = '', sort_key
    if sort_key[0] == '-':
      sort_dir, sort_attr = '-', sort_key[1:]

    if not SORT_ATTR_TRANSLATION.has_key(sort_attr):
      LOG.warn('Bad parameter to list_query_history: sort=%s' % (sort_key,))
      sort_dir, sort_attr = DEFAULT_SORT
  else:
    sort_dir, sort_attr = DEFAULT_SORT
  db_queryset = db_queryset.order_by(sort_dir + SORT_ATTR_TRANSLATION[sort_attr])

  # Get the total return count before slicing
  total_count = db_queryset.count()

  # Slicing (must be the last filter applied)
  pagenum = int(querydict.get(prefix + 'page', 1))
  if pagenum < 1:
    pagenum = 1
  db_queryset = db_queryset[ page_size * (pagenum - 1) : page_size * pagenum ]

  paginator = Paginator(db_queryset, page_size, total=total_count)
  page = paginator.page(pagenum)

  # We do slicing ourselves, rather than letting the Paginator handle it, in order to
  # update the last_state on the running queries
  for history in page.object_list:
    _update_query_state(history.get_full_object())

  # We need to pass the parameters back to the template to generate links
  keys_to_copy = [ prefix + key for key in ('user', 'type', 'sort', 'design_id', 'auto_query') ]
  filter_params = copy_query_dict(querydict, keys_to_copy)

  return page, filter_params

def _update_query_state(query_history):
  """
  Update the last_state for a QueryHistory object. Returns success as True/False.

  This only occurs iff the current last_state is submitted or running, since the other
  states are stable, more-or-less.
  Note that there is a transition from available/failed to expired. That occurs lazily
  when the user attempts to view results that have expired.
  """
  if query_history.last_state <= models.QueryHistory.STATE.running.index:
    try:
      state_enum = dbms.get(query_history.owner, query_history.get_query_server_config()).get_state(query_history.get_handle())
      if state_enum is None:
        # Error was logged at the source
        return False
    except Exception, e:
      LOG.error(e)
      state_enum = models.QueryHistory.STATE.failed
    query_history.save_state(state_enum)
  return True

WHITESPACE = re.compile("\s+", re.MULTILINE)
def collapse_whitespace(s):
  return WHITESPACE.sub(" ", s).strip()

