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

from django.db.models import Q
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render, JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.json_utils import JSONEncoderForHTML
from desktop.models import Document2, Document

from metadata.conf import has_optimizer

from notebook.conf import get_interpreters
from notebook.connectors.base import Notebook, get_api
from notebook.connectors.spark_shell import SparkApi
from notebook.decorators import check_document_access_permission, check_document_modify_permission
from notebook.management.commands.notebook_setup import Command
from notebook.models import make_notebook


LOG = logging.getLogger(__name__)


def notebooks(request):
  editor_type = request.GET.get('type', 'notebook')

  if editor_type != 'notebook':
    notebooks = [d.content_object.to_dict() for d in Document.objects.get_docs(request.user, Document2, qfilter=Q(extra__startswith='query')) if not d.content_object.is_history and d.content_object.type == 'query-' + editor_type]
  else:
    notebooks = [d.content_object.to_dict() for d in Document.objects.get_docs(request.user, Document2, qfilter=Q(extra='notebook')) if not d.content_object.is_history]

  return render('notebooks.mako', request, {
      'notebooks_json': json.dumps(notebooks, cls=JSONEncoderForHTML),
      'editor_type': editor_type
  })


@check_document_access_permission()
def notebook(request):
  notebook_id = request.GET.get('notebook')

  if notebook_id:
    notebook = Notebook(document=Document2.objects.get(id=notebook_id))
  else:
    notebook = Notebook()

  is_yarn_mode = False
  try:
    from spark.conf import LIVY_SERVER_SESSION_KIND
    is_yarn_mode = LIVY_SERVER_SESSION_KIND.get()
  except:
    LOG.exception('Spark is not enabled')

  return render('notebook.mako', request, {
      'notebooks_json': json.dumps([notebook.get_data()]),
      'options_json': json.dumps({
          'languages': get_interpreters(request.user),
          'session_properties': SparkApi.get_properties(),
          'is_optimizer_enabled': has_optimizer(),
      }),
      'is_yarn_mode': is_yarn_mode,
  })


@check_document_access_permission()
def editor(request):
  editor_id = request.GET.get('editor')
  editor_type = request.GET.get('type', 'hive')

  if editor_id:
    editor = Notebook(document=Document2.objects.get(id=editor_id))
    editor_type = editor.get_data()['type'].rsplit('-', 1)[-1]
  else:
    editor = Notebook()
    data = editor.get_data()
    data['name'] = ''
    data['type'] = 'query-%s' % editor_type  # TODO: Add handling for non-SQL types
    editor.data = json.dumps(data)

  return render('editor.mako', request, {
      'notebooks_json': json.dumps([editor.get_data()]),
      'options_json': json.dumps({
          'languages': [{"name": "%s SQL" % editor_type.title(), "type": editor_type}],
          'mode': 'editor',
          'is_optimizer_enabled': has_optimizer(),
      }),
      'editor_type': editor_type,
  })


def new(request):
  return notebook(request)


def browse(request, database, table):
  editor_type = request.GET.get('type', 'hive')

  snippet = {'type': editor_type}
  sql_select = get_api(request, snippet).get_select_star_query(snippet, database, table)

  editor = make_notebook(name='Browse', editor_type=editor_type, statement=sql_select, status='ready-execute')

  return render('editor.mako', request, {
      'notebooks_json': json.dumps([editor.get_data()]),
      'options_json': json.dumps({
          'languages': [{"name": "%s SQL" % editor_type.title(), "type": editor_type}],
          'mode': 'editor',
      }),
      'editor_type': editor_type,
  })


@check_document_access_permission()
def execute_and_watch(request):
  notebook_id = request.GET.get('editor', request.GET.get('notebook'))
  snippet_id = int(request.GET['snippet'])
  action = request.GET['action']
  destination = request.GET['destination']

  notebook = Notebook(document=Document2.objects.get(id=notebook_id))
  snippet = notebook.get_data()['snippets'][snippet_id]
  editor_type = snippet['type']

  api = get_api(request, snippet)

  if action == 'save_as_table':
    sql, success_url = api.export_data_as_table(notebook, snippet, destination)
    editor = make_notebook(name='Execute and watch', editor_type=editor_type, statement=sql, status='ready-execute')
  elif action == 'insert_as_query':
    sql, success_url = api.export_large_data_to_hdfs(notebook, snippet, destination)
    editor = make_notebook(name='Execute and watch', editor_type=editor_type, statement=sql, status='ready-execute')
  else:
    raise PopupException(_('Action %s is unknown') % action)

  return render('editor.mako', request, {
      'notebooks_json': json.dumps([editor.get_data()]),
      'options_json': json.dumps({
          'languages': [{"name": "%s SQL" % editor_type.title(), "type": editor_type}],
          'mode': 'editor',
          'success_url': success_url
      }),
      'editor_type': editor_type,
  })


@check_document_modify_permission()
def delete(request):
  notebooks = json.loads(request.POST.get('notebooks', '[]'))

  for notebook in notebooks:
    doc2 = Document2.objects.get_by_uuid(uuid=notebook['uuid'])
    doc = doc2.doc.get()
    doc.can_write_or_exception(request.user)

    doc.delete()
    doc2.delete()

  return JsonResponse({})


@check_document_access_permission()
def copy(request):
  notebooks = json.loads(request.POST.get('notebooks', '[]'))

  for notebook in notebooks:
    doc2 = Document2.objects.get_by_uuid(uuid=notebook['uuid'])
    doc = doc2.doc.get()

    name = doc2.name + '-copy'
    doc2 = doc2.copy(name=name, owner=request.user)

    doc.copy(content_object=doc2, name=name, owner=request.user)

  return JsonResponse({})


@check_document_access_permission()
def download(request):
  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))
  file_format = request.POST.get('format', 'csv')

  return get_api(request, snippet).download(notebook, snippet, file_format)


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
