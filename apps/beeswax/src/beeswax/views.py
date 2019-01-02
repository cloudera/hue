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
import sys
import time

from django import forms
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, QueryDict
from django.shortcuts import redirect
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.urls import reverse

from desktop.appmanager import get_apps_dict
from desktop.conf import ENABLE_DOWNLOAD, REDIRECT_WHITELIST
from desktop.context_processors import get_app_name

from desktop.lib.django_util import JsonResponse
from desktop.lib.django_util import copy_query_dict, format_preserving_redirect, render
from desktop.lib.django_util import login_notrequired, get_desktop_uri_prefix
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document, _get_apps
from desktop.lib.parameterization import find_variables
from desktop.views import serve_403_error
from notebook.models import escape_rows

import beeswax.forms
import beeswax.design
import beeswax.management.commands.beeswax_install_examples

from beeswax import common, data_export, models
from beeswax.models import QueryHistory, SavedQuery, Session
from beeswax.server import dbms
from beeswax.server.dbms import expand_exception, get_query_server_config, QueryServerException

from desktop.auth.backend import is_admin


LOG = logging.getLogger(__name__)

# For scraping Job IDs from logs
HADOOP_JOBS_RE = re.compile("Starting Job = ([a-z0-9_]+?),")
SPARK_APPLICATION_RE = re.compile("Running with YARN Application = (?P<application_id>application_\d+_\d+)")
TEZ_APPLICATION_RE = re.compile("Executing on YARN cluster with App id ([a-z0-9_]+?)\)")


def index(request):
  return execute_query(request)

"""
Design views
"""

def save_design(request, form, type_, design, explicit_save):
  """
  save_design(request, form, type_, design, explicit_save) -> SavedQuery

  A helper method to save the design:
    * If ``explicit_save``, then we save the data in the current design.
    * If the user clicked the submit button, we do NOT overwrite the current
      design. Instead, we create a new "auto" design (iff the user modified
      the data). This new design is named after the current design, with the
      AUTO_DESIGN_SUFFIX to signify that it's different.

  Need to return a SavedQuery because we may end up with a different one.
  Assumes that form.saveform is the SaveForm, and that it is valid.
  """
  authorized_get_design(request, design.id)
  assert form.saveform.is_valid()
  sub_design_form = form # Beeswax/Impala case

  if type_ == models.HQL:
    design_cls = beeswax.design.HQLdesign
  elif type_ == models.IMPALA:
    design_cls = beeswax.design.HQLdesign
  elif type_ == models.SPARK:
    from spark.design import SparkDesign
    design_cls = SparkDesign
    sub_design_form = form.query
  else:
    raise ValueError(_('Invalid design type %(type)s') % {'type': type_})

  design_obj = design_cls(sub_design_form, query_type=type_)
  name = form.saveform.cleaned_data['name']
  desc = form.saveform.cleaned_data['desc']

  return _save_design(request.user, design, type_, design_obj, explicit_save, name, desc)


def _save_design(user, design, type_, design_obj, explicit_save, name=None, desc=None):
  # Design here means SavedQuery
  old_design = design
  new_data = design_obj.dumps()

  # Auto save if (1) the user didn't click "save", and (2) the data is different.
  # Create an history design if the user is executing a shared design.
  # Don't generate an auto-saved design if the user didn't change anything.
  if explicit_save and (not design.doc.exists() or design.doc.get().can_write_or_exception(user)):
    design.name = name
    design.desc = desc
    design.is_auto = False
  elif design_obj != old_design.get_design():
    # Auto save iff the data is different
    if old_design.id is not None:
      # Clone iff the parent design isn't a new unsaved model
      design = old_design.clone(new_owner=user)
      if not old_design.is_auto:
        design.name = old_design.name + models.SavedQuery.AUTO_DESIGN_SUFFIX
    else:
      design.name = models.SavedQuery.DEFAULT_NEW_DESIGN_NAME
    design.is_auto = True

  design.name = design.name[:64]
  design.type = type_
  design.data = new_data

  design.save()

  LOG.info('Saved %s design "%s" (id %s) for %s' % (explicit_save and '' or 'auto ', design.name, design.id, design.owner))

  if design.doc.exists():
    design.doc.update(name=design.name, description=design.desc)
  else:
    Document.objects.link(design, owner=design.owner, extra=design.type, name=design.name, description=design.desc)

  if design.is_auto:
    design.doc.get().add_to_history()

  return design


def delete_design(request):
  if request.method == 'POST':
    ids = request.POST.getlist('designs_selection')
    designs = dict([(design_id, authorized_get_design(request, design_id, owner_only=True)) for design_id in ids])

    if None in designs.values():
      LOG.error('Cannot delete non-existent design(s) %s' % ','.join([key for key, name in designs.items() if name is None]))
      return list_designs(request)

    for design in designs.values():
      if request.POST.get('skipTrash', 'false') == 'false':
        design.doc.get().send_to_trash()
      else:
        design.doc.all().delete()
        design.delete()
    return redirect(reverse(get_app_name(request) + ':list_designs'))
  else:
    return render('confirm.mako', request, {'url': request.path, 'title': _('Delete design(s)?')})


def restore_design(request):
  if request.method == 'POST':
    ids = request.POST.getlist('designs_selection')
    designs = dict([(design_id, authorized_get_design(request, design_id)) for design_id in ids])

    if None in designs.values():
      LOG.error('Cannot restore non-existent design(s) %s' % ','.join([key for key, name in designs.items() if name is None]))
      return list_designs(request)

    for design in designs.values():
      design.doc.get().restore_from_trash()
    return redirect(reverse(get_app_name(request) + ':list_designs'))
  else:
    return render('confirm.mako', request, {'url': request.path, 'title': _('Restore design(s)?')})


def clone_design(request, design_id):
  """Clone a design belonging to any user"""
  design = authorized_get_design(request, design_id)

  if design is None:
    LOG.error('Cannot clone non-existent design %s' % (design_id,))
    return list_designs(request)

  copy = design.clone(request.user)
  copy.save()

  name = copy.name + '-copy'
  design.doc.get().copy(content_object=copy, name=name, owner=request.user)

  messages.info(request, _('Copied design: %(name)s') % {'name': design.name})

  return format_preserving_redirect(request, reverse(get_app_name(request) + ':execute_design', kwargs={'design_id': copy.id}))


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
  """
  DEFAULT_PAGE_SIZE = 20
  app_name = get_app_name(request)

  # Extract the saved query list.
  prefix = 'q-'
  querydict_query = _copy_prefix(prefix, request.GET)
  # Manually limit up the user filter.
  querydict_query[ prefix + 'type' ] = app_name
  # Get search filter input if any
  search_filter = request.GET.get('text', None)
  if search_filter is not None:
    querydict_query[ prefix + 'text' ] = search_filter

  paginator, page, filter_params = _list_designs(request.user, querydict_query, DEFAULT_PAGE_SIZE, prefix)
  designs_json = []
  if page:
    designs_json = [query.id for query in page.object_list]

  return render('list_designs.mako', request, {
    'page': page,
    'paginator': paginator,
    'filter_params': filter_params,
    'prefix': prefix,
    'user': request.user,
    'designs_json': json.dumps(designs_json)
  })


def list_trashed_designs(request):
  DEFAULT_PAGE_SIZE = 20
  app_name= get_app_name(request)

  user = request.user

  # Extract the saved query list.
  prefix = 'q-'
  querydict_query = _copy_prefix(prefix, request.GET)
  # Manually limit up the user filter.
  querydict_query[ prefix + 'type' ] = app_name
  # Get search filter input if any
  search_filter = request.GET.get('text', None)
  if search_filter is not None:
    querydict_query[ prefix + 'text' ] = search_filter

  paginator, page, filter_params = _list_designs(user, querydict_query, DEFAULT_PAGE_SIZE, prefix, is_trashed=True)
  designs_json = []
  if page:
    designs_json = [query.id for query in page.object_list]

  return render('list_trashed_designs.mako', request, {
    'page': page,
    'paginator': paginator,
    'filter_params': filter_params,
    'prefix': prefix,
    'user': request.user,
    'designs_json': json.dumps(designs_json)
  })


def my_queries(request):
  """
  View a mix of history and saved queries.
  It understands all the GET params in ``list_query_history`` (with a ``h-`` prefix)
  and those in ``list_designs`` (with a ``q-`` prefix). The only thing it disallows
  is the ``user`` filter, since this view only shows what belongs to the user.
  """
  DEFAULT_PAGE_SIZE = 30
  app_name= get_app_name(request)

  # Extract the history list.
  prefix = 'h-'
  querydict_history = _copy_prefix(prefix, request.GET)
  # Manually limit up the user filter.
  querydict_history[ prefix + 'user' ] = request.user
  querydict_history[ prefix + 'type' ] = app_name

  hist_paginator, hist_page, hist_filter = _list_query_history(request.user,
                                               querydict_history,
                                               DEFAULT_PAGE_SIZE,
                                               prefix)
  # Extract the saved query list.
  prefix = 'q-'
  querydict_query = _copy_prefix(prefix, request.GET)
  # Manually limit up the user filter.
  querydict_query[ prefix + 'user' ] = request.user
  querydict_query[ prefix + 'type' ] = app_name

  query_paginator, query_page, query_filter = _list_designs(request.user, querydict_query, DEFAULT_PAGE_SIZE, prefix)
  designs_json = []
  if query_page:
    designs_json = [query.id for query in query_page.object_list]

  filter_params = hist_filter
  filter_params.update(query_filter)

  return render('my_queries.mako', request, {
    'request': request,
    'h_page': hist_page,
    'h_paginator': hist_paginator,
    'q_page': query_page,
    'q_paginator': query_paginator,
    'filter_params': filter_params,
    'designs_json': json.dumps(designs_json)
  })


def list_query_history(request):
  """
  View the history of query (for the current user).
  We get here from /beeswax/query_history?filterargs, with the options being:
    page=<n>            - Controls pagination. Defaults to 1.
    user=<name>         - Show history items from a user. Default to current user only.
                          Also accepts ':all' to show all history items.
    type=<type>         - <type> is "beeswax|impala", for design type. Default to show all.
    design_id=<id>      - Show history for this particular design id.
    sort=<key>          - Sort by the attribute <key>, which is one of:
                            "date", "state", "name" (design name), and "type" (design type)
                          Accepts the form "-date", which sort in descending order.
                          Default to "-date".
    auto_query=<bool>   - Show auto generated actions (drop table, read data, etc). Default True
  """
  DEFAULT_PAGE_SIZE = 100
  prefix = 'q-'

  share_queries = is_admin(request.user)

  querydict_query = request.GET.copy()
  if not share_queries:
    querydict_query[prefix + 'user'] = request.user.username

  app_name = get_app_name(request)
  querydict_query[prefix + 'type'] = app_name

  paginator, page, filter_params = _list_query_history(request.user, querydict_query, DEFAULT_PAGE_SIZE, prefix)

  filter = request.GET.get(prefix + 'search') and request.GET.get(prefix + 'search') or ''

  if request.GET.get('format') == 'json':
    resp = {
      'queries': [massage_query_history_for_json(app_name, query_history) for query_history in page.object_list]
    }
    return JsonResponse(resp)


  return render('list_history.mako', request, {
    'request': request,
    'page': page,
    'paginator': paginator,
    'filter_params': filter_params,
    'share_queries': share_queries,
    'prefix': prefix,
    'filter': filter,
  })


def massage_query_history_for_json(app_name, query_history):
  return {
    'id': query_history.id,
    'design_id': query_history.design.id,
    'query': escape(query_history.query),
    'timeInMs': time.mktime(query_history.submission_date.timetuple()),
    'timeFormatted': query_history.submission_date.strftime("%x %X"),
    'designUrl': reverse(app_name + ':execute_design', kwargs={'design_id': query_history.design.id}),
    'resultsUrl': not query_history.is_failure() and reverse(app_name + ':watch_query_history', kwargs={'query_history_id': query_history.id}) or ""
  }


def download(request, id, format, user_agent=None):
  if not ENABLE_DOWNLOAD.get():
    return serve_403_error(request)

  try:
    query_history = authorized_get_query_history(request, id, must_exist=True)
    db = dbms.get(request.user, query_history.get_query_server_config())
    LOG.debug('Download results for query %s: [ %s ]' % (query_history.server_id, query_history.query))

    return data_export.download(query_history.get_handle(), format, db, user_agent=user_agent)
  except Exception, e:
    if not hasattr(e, 'message') or not e.message:
      message = e
    else:
      message = e.message
    raise PopupException(message, detail='')

"""
Queries Views
"""

def execute_query(request, design_id=None, query_history_id=None):
  """
  View function for executing an arbitrary query.
  """
  action = 'query'

  if query_history_id:
    query_history = authorized_get_query_history(request, query_history_id, must_exist=True)
    design = query_history.design

    try:
      if query_history.server_id and query_history.server_guid:
        handle, state = _get_query_handle_and_state(query_history)

      if 'on_success_url' in request.GET:
        if request.GET.get('on_success_url') and any([regexp.match(request.GET.get('on_success_url')) for regexp in REDIRECT_WHITELIST.get()]):
          action = 'watch-redirect'
        else:
          action = 'watch-results'
      else:
        action = 'editor-results'
    except QueryServerException, e:
      if 'Invalid query handle' in e.message or 'Invalid OperationHandle' in e.message:
        query_history.save_state(QueryHistory.STATE.expired)
        LOG.warn("Invalid query handle", exc_info=sys.exc_info())
        action = 'editor-expired-results'
      else:
        raise e
  else:
    # Check perms.
    authorized_get_design(request, design_id)

    app_name = get_app_name(request)
    query_type = SavedQuery.TYPES_MAPPING[app_name]
    design = safe_get_design(request, query_type, design_id)
    query_history = None

  current_app, other_apps, apps_list = _get_apps(request.user, '')
  doc = design and design.id and design.doc.get()
  context = {
    'design': design,
    'apps': apps_list,
    'query': query_history, # Backward
    'query_history': query_history,
    'autocomplete_base_url': reverse(get_app_name(request) + ':api_autocomplete_databases', kwargs={}),
    'autocomplete_base_url_hive': reverse('beeswax:api_autocomplete_databases', kwargs={}),
    'can_edit_name': design and design.id and not design.is_auto,
    'doc_id': doc and doc.id or -1,
    'can_edit': doc and doc.can_write(request.user),
    'action': action,
    'on_success_url': request.GET.get('on_success_url'),
    'has_metastore': 'metastore' in get_apps_dict(request.user)
  }

  return render('execute.mako', request, context)


def view_results(request, id, first_row=0):
  """
  Returns the view for the results of the QueryHistory with the given id.

  The query results MUST be ready.
  To display query results, one should always go through the execute_query view.
  If the result set has has_result_set=False, display an empty result.

  If ``first_row`` is 0, restarts (if necessary) the query read.  Otherwise, just
  spits out a warning if first_row doesn't match the servers conception.
  Multiple readers will produce a confusing interaction here, and that's known.

  It understands the ``context`` GET parameter. (See execute_query().)
  """
  first_row = long(first_row)
  start_over = (first_row == 0)
  results = type('Result', (object,), {
                'rows': 0,
                'columns': [],
                'has_more': False,
                'start_row': 0,
            })
  data = []
  fetch_error = False
  error_message = ''
  log = ''
  columns = []
  app_name = get_app_name(request)

  query_history = authorized_get_query_history(request, id, must_exist=True)
  query_server = query_history.get_query_server_config()
  db = dbms.get(request.user, query_server)

  handle, state = _get_query_handle_and_state(query_history)
  context_param = request.GET.get('context', '')
  query_context = parse_query_context(context_param)

  # Update the status as expired should not be accessible
  expired = state == models.QueryHistory.STATE.expired

  # Retrieve query results or use empty result if no result set
  try:
    if query_server['server_name'] == 'impala' and not handle.has_result_set:
      downloadable = False
    else:
      results = db.fetch(handle, start_over, 100)

      # Materialize and HTML escape results
      data = escape_rows(results.rows())

      # We display the "Download" button only when we know that there are results:
      downloadable = first_row > 0 or data
      log = db.get_log(handle)
      columns = results.data_table.cols()

  except Exception, ex:
    LOG.exception('error fetching results')

    fetch_error = True
    error_message, log = expand_exception(ex, db, handle)

  # Handle errors
  error = fetch_error or results is None or expired

  context = {
    'error': error,
    'message': error_message,
    'query': query_history,
    'results': data,
    'columns': columns,
    'expected_first_row': first_row,
    'log': log,
    'hadoop_jobs': app_name != 'impala' and parse_out_jobs(log),
    'query_context': query_context,
    'can_save': False,
    'context_param': context_param,
    'expired': expired,
    'app_name': app_name,
    'next_json_set': None,
    'is_finished': query_history.is_finished()
  }

  if not error:
    download_urls = {}
    if downloadable:
      for format in common.DL_FORMATS:
        download_urls[format] = reverse(app_name + ':download', kwargs=dict(id=str(id), format=format))

    results.start_row = first_row

    context.update({
      'id': id,
      'results': data,
      'has_more': results.has_more,
      'next_row': results.start_row + len(data),
      'start_row': results.start_row,
      'expected_first_row': first_row,
      'columns': columns,
      'download_urls': download_urls,
      'can_save': query_history.owner == request.user,
      'next_json_set':
        reverse(get_app_name(request) + ':view_results', kwargs={
            'id': str(id),
            'first_row': results.start_row + len(data)
          }
        )
        + ('?context=' + context_param or '') + '&format=json'
    })

  context['columns'] = massage_columns_for_json(columns)
  if 'save_form' in context:
    del context['save_form']
  if 'query' in context:
    del context['query']
  return JsonResponse(context)


def configuration(request):
  app_name = get_app_name(request)
  query_server = get_query_server_config(app_name)

  session = Session.objects.get_session(request.user, query_server['server_name'])

  if session:
    properties = json.loads(session.properties)
    # Redact passwords
    for key, value in properties.items():
      if 'password' in key.lower():
        properties[key] = '*' * len(value)
  else:
    properties = {}

  return render("configuration.mako", request, {'configuration': properties})


"""
Other views
"""

def install_examples(request):
  response = {'status': -1, 'message': ''}

  if request.method == 'POST':
    try:
      app_name = get_app_name(request)
      db_name = request.POST.get('db_name', 'default')
      beeswax.management.commands.beeswax_install_examples.Command().handle(app_name=app_name, db_name=db_name, user=request.user)
      response['status'] = 0
    except Exception, err:
      LOG.exception(err)
      response['message'] = str(err)
  else:
    response['message'] = _('A POST request is required.')

  return JsonResponse(response)


@login_notrequired
def query_done_cb(request, server_id):
  """
  A callback for query completion notification. When the query is done,
  BeeswaxServer notifies us by sending a GET request to this view.
  """
  message_template = '<html><head></head>%(message)s<body></body></html>'
  message = {'message': 'error'}

  try:
    query_history = QueryHistory.objects.get(server_id=server_id + '\n')

    # Update the query status
    query_history.set_to_available()

    # Find out details about the query
    if not query_history.notify:
      message['message'] = 'email_notify is false'
      return HttpResponse(message_template % message)

    design = query_history.design
    user = query_history.owner
    subject = _("Beeswax query completed.")

    if design:
      subject += ": %s" % (design.name,)

    link = "%s%s" % \
              (get_desktop_uri_prefix(),
               reverse(get_app_name(request) + ':watch_query_history', kwargs={'query_history_id': query_history.id}))
    body = _("%(subject)s. See the results here: %(link)s\n\nQuery:\n%(query)s") % {
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
def massage_columns_for_json(cols):
  massaged_cols = []
  for column in cols:
    massaged_cols.append({
      'name': column.name,
      'type': column.type,
      'comment': column.comment
    })
  return massaged_cols


def authorized_get_design(request, design_id, owner_only=False, must_exist=False):
  if design_id is None and not must_exist:
    return None

  try:
    design = SavedQuery.objects.get(id=design_id)
  except SavedQuery.DoesNotExist:
    if must_exist:
      raise PopupException(_('Design %(id)s does not exist.') % {'id': design_id})
    else:
      return None

  if owner_only:
    design.doc.get().can_write_or_exception(request.user)
  else:
    design.doc.get().can_read_or_exception(request.user)

  return design


def authorized_get_query_history(request, query_history_id, owner_only=False, must_exist=False):
  if query_history_id is None and not must_exist:
    return None

  try:
    query_history = QueryHistory.get(id=query_history_id)
  except QueryHistory.DoesNotExist:
    if must_exist:
      raise PopupException(_('QueryHistory %(id)s does not exist.') % {'id': query_history_id})
    else:
      return None

  # Some queries don't have a design so are not linked to Document Model permission
  if query_history.design is None or not query_history.design.doc.exists():
    if not is_admin(request.user) and request.user != query_history.owner:
      raise PopupException(_('Permission denied to read QueryHistory %(id)s') % {'id': query_history_id})
  else:
    query_history.design.doc.get().can_read_or_exception(request.user)

  return query_history


def safe_get_design(request, design_type, design_id=None):
  """
  Return a new design, if design_id is None,
  Return the design with the given id and type. If the design is not found,
  display a notification and return a new design.
  """
  design = None

  if design_id is not None:
    design = authorized_get_design(request, design_id)

  if design is None:
    design = SavedQuery(owner=request.user, type=design_type)

  return design


def make_parameterization_form(query_str):
  """
  Creates a django form on the fly with arguments from the
  query.
  """
  variables = find_variables(query_str)
  if len(variables) > 0:
    class Form(forms.Form):
      for name in sorted(variables):
        locals()[name] = forms.CharField(widget=forms.TextInput(attrs={'required': True}))
    return Form
  else:
    return None


def execute_directly(request, query, query_server=None,
                     design=None, on_success_url=None, on_success_params=None,
                     **kwargs):
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

  query_history = db.execute_query(query, design)

  watch_url = reverse(get_app_name(request) + ':watch_query_history', kwargs={'query_history_id': query_history.id})

  # Prepare the GET params for the watch_url
  get_dict = QueryDict(None, mutable=True)

  # (1) on_success_url
  if on_success_url:
    if callable(on_success_url):
      on_success_url = on_success_url(query_history)
    get_dict['on_success_url'] = on_success_url

  # (2) misc
  if on_success_params:
    get_dict.update(on_success_params)

  return format_preserving_redirect(request, watch_url, get_dict)


def _list_designs(user, querydict, page_size, prefix="", is_trashed=False):
  """
  _list_designs(user, querydict, page_size, prefix, is_trashed) -> (page, filter_param)

  A helper to gather the designs page. It understands all the GET params in
  ``list_designs``, by reading keys from the ``querydict`` with the given ``prefix``.
  """
  DEFAULT_SORT = ('-', 'date')                  # Descending date

  SORT_ATTR_TRANSLATION = dict(
    date='last_modified',
    name='name',
    desc='description',
    type='extra',
  )

  # Trash and security
  if is_trashed:
    db_queryset = Document.objects.trashed_docs(SavedQuery, user)
  else:
    db_queryset = Document.objects.available_docs(SavedQuery, user)

  # Filter by user
  filter_username = querydict.get(prefix + 'user')
  if filter_username:
    try:
      db_queryset = db_queryset.filter(owner=User.objects.get(username=filter_username))
    except User.DoesNotExist:
      # Don't care if a bad filter term is provided
      pass

  # Design type
  d_type = querydict.get(prefix + 'type')
  if d_type and d_type in SavedQuery.TYPES_MAPPING.keys():
    db_queryset = db_queryset.filter(extra=str(SavedQuery.TYPES_MAPPING[d_type]))

  # Text search
  frag = querydict.get(prefix + 'text')
  if frag:
    db_queryset = db_queryset.filter(Q(name__icontains=frag) | Q(description__icontains=frag))

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

  designs = [job.content_object for job in db_queryset.all() if job.content_object and job.content_object.is_auto == False]

  pagenum = int(querydict.get(prefix + 'page', 1))
  paginator = Paginator(designs, page_size, allow_empty_first_page=True)
  try:
    page = paginator.page(pagenum)
  except EmptyPage:
    page = None

  # We need to pass the parameters back to the template to generate links
  keys_to_copy = [ prefix + key for key in ('user', 'type', 'sort', 'text') ]
  filter_params = copy_query_dict(querydict, keys_to_copy)

  return paginator, page, filter_params


def _get_query_handle_and_state(query_history):
  """
  Front-end wrapper to handle exceptions. Expects the query to be submitted.
  """
  handle = query_history.get_handle()

  if handle is None:
    raise PopupException(_("Failed to retrieve query state from the Query Server."))

  state = dbms.get(query_history.owner, query_history.get_query_server_config()).get_state(handle)

  if state is None:
    raise PopupException(_("Failed to contact Server to check query status."))
  return (handle, state)


def parse_query_context(context):
  """
  parse_query_context(context) -> ('table', <table_name>) -or- ('design', <design_obj>)
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


def parse_out_jobs(log, engine='mr', with_state=False):
  """
  Ideally, Hive would tell us what jobs it has run directly from the Thrift interface.

  with_state: If True, will return a list of dict items with 'job_id', 'started', 'finished'
  """
  ret = []

  if engine.lower() == 'mr':
    start_pattern = HADOOP_JOBS_RE
  elif engine.lower() == 'spark':
    start_pattern = SPARK_APPLICATION_RE
  elif engine.lower() == 'tez':
    start_pattern = TEZ_APPLICATION_RE
  else:
    raise ValueError(_('Cannot parse job IDs for execution engine %(engine)s') % {'engine': engine})

  for match in start_pattern.finditer(log):
    job_id = match.group(1)

    if with_state:
      if job_id not in list(job['job_id'] for job in ret):
        ret.append({'job_id': job_id, 'started': True, 'finished': False})
      end_pattern = 'Ended Job = %s' % job_id

      if end_pattern in log:
        job = next((job for job in ret if job['job_id'] == job_id), None)
        if job is not None:
          job['finished'] = True
        else:
          ret.append({'job_id': job_id, 'started': True, 'finished': True})
    else:
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
  if querydict.get(prefix + 'auto_query', 'on') != 'on':
    db_queryset = db_queryset.exclude(design__isnull=False, design__is_auto=True)

  user_filter = querydict.get(prefix + 'user', user.username)
  if user_filter != ':all':
    db_queryset = db_queryset.filter(owner__username=user_filter)

  # Design id
  design_id = querydict.get(prefix + 'design_id')
  if design_id:
    if design_id.isdigit():
      db_queryset = db_queryset.filter(design__id=int(design_id))
    else:
      raise PopupException(_('list_query_history requires design_id parameter to be an integer: %s') % design_id)

  # Search
  search_filter = querydict.get(prefix + 'search')
  if search_filter:
    db_queryset = db_queryset.filter(Q(design__name__icontains=search_filter) | Q(query__icontains=search_filter) | Q(owner__username__icontains=search_filter))

  # Design type
  d_type = querydict.get(prefix + 'type')
  if d_type:
    if d_type not in SavedQuery.TYPES_MAPPING.keys():
      LOG.warn('Bad parameter to list_query_history: type=%s' % (d_type,))
    else:
      db_queryset = db_queryset.filter(design__type=SavedQuery.TYPES_MAPPING[d_type])

  # If recent query
  recent = querydict.get('recent')
  if recent:
    db_queryset = db_queryset.filter(is_cleared=False)

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
  db_queryset = db_queryset.order_by(sort_dir + SORT_ATTR_TRANSLATION[sort_attr], '-id')

  # Get the total return count before slicing
  total_count = db_queryset.count()

  # Slicing (must be the last filter applied)
  pagenum = int(querydict.get(prefix + 'page', 1))
  if pagenum < 1:
    pagenum = 1
  db_queryset = db_queryset[ page_size * (pagenum - 1) : page_size * pagenum ]
  paginator = Paginator(db_queryset, page_size, allow_empty_first_page=True)

  try:
    page = paginator.page(pagenum)
  except EmptyPage:
    page = None

  # We do slicing ourselves, rather than letting the Paginator handle it, in order to
  # update the last_state on the running queries
  if page:
    for history in page.object_list:
      _update_query_state(history.get_full_object())

  # We need to pass the parameters back to the template to generate links
  keys_to_copy = [ prefix + key for key in ('user', 'type', 'sort', 'design_id', 'auto_query', 'search') ]
  filter_params = copy_query_dict(querydict, keys_to_copy)

  return paginator, page, filter_params


def _update_query_state(query_history):
  """
  Update the last_state for a QueryHistory object. Returns success as True/False.

  This only occurs iff the current last_state is submitted or running, since the other
  states are stable, more-or-less.
  Note that there is a transition from available/failed to expired. That occurs lazily
  when the user attempts to view results that have expired.
  """
  if query_history.last_state <= models.QueryHistory.STATE.running.value:
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


def get_db_choices(request):
  app_name = get_app_name(request)
  query_server = get_query_server_config(app_name)
  db = dbms.get(request.user, query_server)
  dbs = db.get_databases()
  return [(db, db) for db in dbs]


WHITESPACE = re.compile("\s+", re.MULTILINE)
def collapse_whitespace(s):
  return WHITESPACE.sub(" ", s).strip()
