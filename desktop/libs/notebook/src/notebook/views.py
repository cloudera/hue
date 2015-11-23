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
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render, JsonResponse
from desktop.lib.json_utils import JSONEncoderForHTML
from desktop.models import Document2, Document

from notebook.decorators import check_document_access_permission, check_document_modify_permission
from notebook.connectors.base import Notebook, get_api
from notebook.management.commands.notebook_setup import Command
from notebook.connectors.spark_shell import SparkApi
from notebook.conf import get_interpreters


LOG = logging.getLogger(__name__)


@check_document_access_permission()
def notebook(request):
  notebook_id = request.GET.get('notebook')

  if notebook_id:
    notebook = Notebook(document=Document2.objects.get(id=notebook_id))
  else:
    notebook = Notebook()

  autocomplete_base_url = ''
  try:
    autocomplete_base_url = reverse('beeswax:api_autocomplete_databases', kwargs={})
  except:
    LOG.exception('failed to get autocomplete base url')

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
          'session_properties': SparkApi.PROPERTIES,
      }),
      'autocomplete_base_url': autocomplete_base_url,
      'is_yarn_mode': is_yarn_mode
  })


@check_document_access_permission()
def editor(request):
  editor_id = request.GET.get('editor')
  editor_type = request.GET.get('type', 'hive')

  if editor_id:
    editor = Notebook(document=Document2.objects.get(id=editor_id))
  else:
    editor = Notebook()
    data = editor.get_data()
    data['name'] = '%s Query' % editor_type.title()
    data['type'] = 'query-%s' % editor_type
    editor.data = json.dumps(data)

  autocomplete_base_url = ''
  try:
    autocomplete_base_url = reverse('beeswax:api_autocomplete_databases', kwargs={})
  except:
    LOG.exception('failed to get autocomplete base url')

  return render('editor.mako', request, {
      'notebooks_json': json.dumps([editor.get_data()]),
      'options_json': json.dumps({
          'languages': [{"name": "%s SQL" % editor_type.title(), "type": editor_type}],
          'mode': 'editor',
      }),
      'editor_type': editor_type,
      'autocomplete_base_url': autocomplete_base_url,
  })


def new(request):
  return notebook(request)


def notebooks(request):
  notebooks = [d.content_object.to_dict() for d in Document.objects.get_docs(request.user, Document2, qfilter=Q(extra='notebook') | Q(extra__startswith='query')) if not d.content_object.is_history]

  return render('notebooks.mako', request, {
      'notebooks_json': json.dumps(notebooks, cls=JSONEncoderForHTML)
  })


@check_document_modify_permission()
def delete(request):
  notebooks = json.loads(request.POST.get('notebooks', '[]'))

  for notebook in notebooks:
    doc2 = Document2.objects.get(uuid=notebook['uuid'])
    doc = doc2.doc.get()
    doc.can_write_or_exception(request.user)

    doc.delete()
    doc2.delete()

  return JsonResponse({})


@check_document_access_permission()
def copy(request):
  notebooks = json.loads(request.POST.get('notebooks', '[]'))

  for notebook in notebooks:
    doc2 = Document2.objects.get(uuid=notebook['uuid'])
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

  return get_api(request.user, snippet, request.fs, request.jt).download(notebook, snippet, file_format)


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

