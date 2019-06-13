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

from beeswax.data_export import DOWNLOAD_COOKIE_AGE

from django.urls import reverse
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views.decorators.clickjacking import xframe_options_exempt

from desktop.conf import ENABLE_DOWNLOAD, USE_NEW_EDITOR, TASK_SERVER
from desktop.lib import export_csvxls
from desktop.lib.django_util import render, JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.json_utils import JSONEncoderForHTML
from desktop.models import Document2, Document, FilesystemException
from desktop.views import serve_403_error

from metadata.conf import has_optimizer, has_catalog, has_workload_analytics

from notebook.conf import get_ordered_interpreters, SHOW_NOTEBOOKS
from notebook.connectors.base import Notebook, get_api as _get_api, _get_snippet_name
from notebook.connectors.spark_shell import SparkApi
from notebook.decorators import check_editor_access_permission, check_document_access_permission, check_document_modify_permission
from notebook.management.commands.notebook_setup import Command
from notebook.models import make_notebook

LOG = logging.getLogger(__name__)

if TASK_SERVER.ENABLED.get():
  import notebook.tasks as ntasks

class ApiWrapper(object):
  def __init__(self, request, snippet):
    self.request = request
    self.api = _get_api(request, snippet)
  def __getattr__(self, name):
    if TASK_SERVER.ENABLED.get() and hasattr(ntasks, name):
      attr = object.__getattribute__(ntasks, name)
      def _method(*args, **kwargs):
        return attr(*args, **dict(kwargs, postdict=self.request.POST, user_id=self.request.user.id))
      return _method
    else:
      return object.__getattribute__(self.api, name)

def get_api(request, snippet):
  return ApiWrapper(request, snippet)

def notebooks(request):
  editor_type = request.GET.get('type', 'notebook')

  if editor_type != 'notebook':
    if USE_NEW_EDITOR.get():
      notebooks = [doc.to_dict() for doc in Document2.objects.documents(user=request.user).search_documents(types=['query-%s' % editor_type])]
    else:
      notebooks = [d.content_object.to_dict() for d in Document.objects.get_docs(request.user, Document2, qfilter=Q(extra__startswith='query')) if not d.content_object.is_history and d.content_object.type == 'query-' + editor_type]
  else:
    if USE_NEW_EDITOR.get():
      notebooks = [doc.to_dict() for doc in Document2.objects.documents(user=request.user).search_documents(types=['notebook'])]
    else:
      notebooks = [d.content_object.to_dict() for d in Document.objects.get_docs(request.user, Document2, qfilter=Q(extra='notebook')) if not d.content_object.is_history]

  return render('notebooks.mako', request, {
      'notebooks_json': json.dumps(notebooks, cls=JSONEncoderForHTML),
      'editor_type': editor_type
  })


@check_document_access_permission()
def notebook(request, is_embeddable=False):
  if not SHOW_NOTEBOOKS.get() or not request.user.has_hue_permission(action="access", app='notebook'):
    return serve_403_error(request)

  notebook_id = request.GET.get('notebook', request.GET.get('editor'))

  is_yarn_mode = False
  try:
    from spark.conf import LIVY_SERVER_SESSION_KIND
    is_yarn_mode = LIVY_SERVER_SESSION_KIND.get()
  except:
    LOG.exception('Spark is not enabled')

  return render('notebook.mako', request, {
      'editor_id': notebook_id or None,
      'notebooks_json': '{}',
      'is_embeddable': request.GET.get('is_embeddable', False),
      'options_json': json.dumps({
          'languages': get_ordered_interpreters(request.user),
          'session_properties': SparkApi.get_properties(),
          'is_optimizer_enabled': has_optimizer(),
          'is_wa_enabled': has_workload_analytics(),
          'is_navigator_enabled': has_catalog(request.user),
          'editor_type': 'notebook'
      }),
      'is_yarn_mode': is_yarn_mode,
  })


@check_document_access_permission()
def notebook_embeddable(request):
  return notebook(request, True)


@check_editor_access_permission()
@check_document_access_permission()
def editor(request, is_mobile=False, is_embeddable=False):
  editor_id = request.GET.get('editor')
  editor_type = request.GET.get('type', 'hive')

  if editor_type == 'notebook' or request.GET.get('notebook'):
    return notebook(request)

  if editor_id:  # Open existing saved editor document
    document = Document2.objects.get(id=editor_id)
    editor_type = document.type.rsplit('-', 1)[-1]

  template = 'editor.mako'
  if is_mobile:
    template = 'editor_m.mako'

  return render(template, request, {
      'editor_id': editor_id or None,
      'notebooks_json': '{}',
      'is_embeddable': request.GET.get('is_embeddable', False),
      'editor_type': editor_type,
      'options_json': json.dumps({
        'languages': get_ordered_interpreters(request.user),
        'mode': 'editor',
        'is_optimizer_enabled': has_optimizer(),
        'is_wa_enabled': has_workload_analytics(),
        'is_navigator_enabled': has_catalog(request.user),
        'editor_type': editor_type,
        'mobile': is_mobile
      })
  })


@check_document_access_permission()
def editor_embeddable(request):
  return editor(request, False, True)


@check_document_access_permission()
def editor_m(request):
  return editor(request, True)


def new(request):
  return notebook(request)


def browse(request, database, table, partition_spec=None):
  snippet = {'type': request.POST.get('sourceType', 'hive')}

  statement = get_api(request, snippet).get_browse_query(snippet, database, table, partition_spec)
  editor_type = snippet['type']
  namespace = request.POST.get('namespace', 'default')
  compute = json.loads(request.POST.get('cluster', '{}'))

  if request.method == 'POST':
    notebook = make_notebook(name='Execute and watch', editor_type=editor_type, statement=statement, status='ready-execute',
                             is_task=True, namespace=namespace, compute=compute)
    return JsonResponse(notebook.execute(request, batch=False))
  else:
    editor = make_notebook(name='Browse', editor_type=editor_type, statement=statement, status='ready-execute',
                           namespace=namespace, compute=compute)

    return render('editor.mako', request, {
        'notebooks_json': json.dumps([editor.get_data()]),
        'options_json': json.dumps({
            'languages': get_ordered_interpreters(request.user),
            'mode': 'editor',
            'editor_type': editor_type
        }),
        'editor_type': editor_type,
    })

# Deprecated in Hue 4
@check_document_access_permission()
def execute_and_watch(request):
  notebook_id = request.GET.get('editor', request.GET.get('notebook'))
  snippet_id = int(request.GET['snippet'])
  action = request.GET['action']
  destination = request.GET['destination']

  notebook = Notebook(document=Document2.objects.get(id=notebook_id)).get_data()
  snippet = notebook['snippets'][snippet_id]
  editor_type = snippet['type']

  api = get_api(request, snippet)

  if action == 'save_as_table':
    sql, success_url = api.export_data_as_table(notebook, snippet, destination)
    editor = make_notebook(name='Execute and watch', editor_type=editor_type, statement=sql, status='ready-execute', database=snippet['database'])
  elif action == 'insert_as_query':
    # TODO: checks/workarounds in case of non impersonation or Sentry
    # TODO: keep older simpler way in case of known not many rows?
    sql, success_url = api.export_large_data_to_hdfs(notebook, snippet, destination)
    editor = make_notebook(name='Execute and watch', editor_type=editor_type, statement=sql, status='ready-execute', database=snippet['database'], on_success_url=success_url)
  elif action == 'index_query':
    if destination == '__hue__':
      destination = _get_snippet_name(notebook, unique=True, table_format=True)
      live_indexing = True
    else:
      live_indexing = False

    sql, success_url = api.export_data_as_table(notebook, snippet, destination, is_temporary=True, location='')
    editor = make_notebook(name='Execute and watch', editor_type=editor_type, statement=sql, status='ready-execute')

    sample = get_api(request, snippet).fetch_result(notebook, snippet, 0, start_over=True)

    from indexer.api3 import _index # Will ve moved to the lib
    from indexer.file_format import HiveFormat
    from indexer.fields import Field

    file_format = {
        'name': 'col',
        'inputFormat': 'query',
        'format': {'quoteChar': '"', 'recordSeparator': '\n', 'type': 'csv', 'hasHeader': False, 'fieldSeparator': '\u0001'},
        "sample": '',
        "columns": [
            Field(col['name'].rsplit('.')[-1], HiveFormat.FIELD_TYPE_TRANSLATE.get(col['type'], 'string')).to_dict()
            for col in sample['meta']
        ]
    }

    if live_indexing:
      file_format['inputFormat'] = 'hs2_handle'
      file_format['fetch_handle'] = lambda rows, start_over: get_api(request, snippet).fetch_result(notebook, snippet, rows=rows, start_over=start_over)

    job_handle = _index(request, file_format, destination, query=notebook['uuid'])

    if live_indexing:
      return redirect(reverse('search:browse', kwargs={'name': destination}))
    else:
      return redirect(reverse('oozie:list_oozie_workflow', kwargs={'job_id': job_handle['handle']['id']}))
  else:
    raise PopupException(_('Action %s is unknown') % action)

  return render('editor.mako', request, {
      'notebooks_json': json.dumps([editor.get_data()]),
      'options_json': json.dumps({
          'languages': [{"name": "%s SQL" % editor_type.title(), "type": editor_type}],
          'mode': 'editor',
          'editor_type': editor_type,
          'success_url': success_url
      }),
      'editor_type': editor_type,
  })


@check_document_modify_permission()
def delete(request):
  response = {'status': -1}

  notebooks = json.loads(request.POST.get('notebooks', '[]'))

  if not notebooks:
    response['message'] = _('No notebooks have been selected for deletion.')
  else:
    ctr = 0
    failures = []
    for notebook in notebooks:
      try:
        doc2 = Document2.objects.get_by_uuid(user=request.user, uuid=notebook['uuid'], perm_type='write')
        doc = doc2._get_doc1()
        doc.can_write_or_exception(request.user)
        doc2.trash()
        ctr += 1
      except FilesystemException, e:
        failures.append(notebook['uuid'])
        LOG.exception("Failed to delete document with UUID %s that is writable by user %s, skipping." % (notebook['uuid'], request.user.username))

    response['status'] = 0
    if failures:
      response['errors'] = failures
      response['message'] = _('Trashed %d notebook(s) and failed to delete %d notebook(s).') % (ctr, len(failures))
    else:
      response['message'] = _('Trashed %d notebook(s)') % ctr

  return JsonResponse(response)


@check_document_access_permission()
def copy(request):
  response = {'status': -1}

  notebooks = json.loads(request.POST.get('notebooks', '[]'))

  if len(notebooks) == 0:
    response['message'] = _('No notebooks have been selected for copying.')
  else:
    ctr = 0
    failures = []
    for notebook in notebooks:
      try:
        doc2 = Document2.objects.get_by_uuid(user=request.user, uuid=notebook['uuid'])
        doc = doc2._get_doc1()
        name = doc2.name + '-copy'
        doc2 = doc2.copy(name=name, owner=request.user)

        doc.copy(content_object=doc2, name=name, owner=request.user)
      except FilesystemException, e:
        failures.append(notebook['uuid'])
        LOG.exception("Failed to copy document with UUID %s accessible by user %s, skipping." % (notebook['uuid'], request.user.username))

    response['status'] = 0
    if failures:
      response['errors'] = failures
      response['message'] = _('Copied %d notebook(s) and failed to copy %d notebook(s).') % (ctr, len(failures))
    else:
      response['message'] = _('Copied %d notebook(s)') % ctr

  return JsonResponse(response)

@check_document_access_permission()
def download(request):
  if not ENABLE_DOWNLOAD.get():
    return serve_403_error(request)

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))
  file_format = request.POST.get('format', 'csv')
  user_agent = request.META.get('HTTP_USER_AGENT')
  file_name = _get_snippet_name(notebook)

  content_generator = get_api(request, snippet).download(notebook, snippet, file_format=file_format)
  response = export_csvxls.make_response(content_generator, file_format, file_name, user_agent=user_agent)

  if snippet['id']:
    response.set_cookie(
      'download-%s' % snippet['id'],
      json.dumps({
        'truncated': 'false',
        'row_counter': '0'
      }),
      max_age=DOWNLOAD_COOKIE_AGE
    )
  if response:
    request.audit = {
      'operation': 'DOWNLOAD',
      'operationText': 'User %s downloaded results from %s as %s' % (request.user.username, _get_snippet_name(notebook), file_format),
      'allowed': True
    }

  return response


def install_examples(request):
  response = {'status': -1, 'message': ''}

  if request.method == 'POST':
    try:
      Command().handle(user=request.user)
      response['status'] = 0
    except Exception, err:
      LOG.exception(err)
      response['message'] = str(err)
  else:
    response['message'] = _('A POST request is required.')

  return JsonResponse(response)


def upgrade_session_properties(request, notebook):
  # Upgrade session data if using old format
  data = notebook.get_data()

  for session in data.get('sessions', []):
    api = get_api(request, session)
    if 'type' in session and hasattr(api, 'upgrade_properties'):
      properties = session.get('properties', None)
      session['properties'] = api.upgrade_properties(session['type'], properties)

  notebook.data = json.dumps(data)
  return notebook
