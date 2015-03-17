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
import uuid

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render, JsonResponse
from desktop.lib.json_utils import JSONEncoderForHTML
from desktop.models import Document2, Document

from spark.conf import LANGUAGES
from spark.decorators import check_document_access_permission,\
  check_document_modify_permission
from spark.models import Notebook, get_api
from spark.management.commands.spark_setup import Command


LOG = logging.getLogger(__name__)


@check_document_access_permission()
def editor(request):
  notebook_id = request.GET.get('notebook')

  if notebook_id:
    notebook = Notebook(document=Document2.objects.get(id=notebook_id))
  else:
    notebook = Notebook()

  autocomplete_base_url = ''
  try:
    autocomplete_base_url = reverse('beeswax:api_autocomplete_databases', kwargs={})
  except:
    pass

  return render('editor.mako', request, {
      'notebooks_json': json.dumps([notebook.get_data()]),
      'options_json': json.dumps({
          'languages': LANGUAGES.get(),
          'snippet_placeholders' : {
              'scala': _('Example: 1 + 1, or press CTRL + space'),
              'python': _('Example: 1 + 1, or press CTRL + space'),
              'impala': _('Example: SELECT * FROM tablename, or press CTRL + space'),
              'hive': _('Example: SELECT * FROM tablename, or press CTRL + space'),
              'text': _('<h2>This is a text snippet</h2>Type your text here')
          }
      }),
      'autocomplete_base_url': autocomplete_base_url,
  })


def new(request):
  return editor(request)


def notebooks(request):
  notebooks = [d.content_object.to_dict() for d in Document.objects.get_docs(request.user, Document2, extra='notebook')]

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
    copy_doc = doc2.doc.get().copy(owner=request.user)

    doc2.pk = None
    doc2.id = None
    doc2.uuid = str(uuid.uuid4())
    doc2.owner = request.user
    doc2.save()

    doc2.doc.all().delete()
    doc2.doc.add(copy_doc)
    doc2.save()

  return JsonResponse({})


@check_document_access_permission()
def download(request):
  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))
  file_format = request.POST.get('format', 'csv')

  return get_api(request.user, snippet).download(notebook, snippet, file_format)


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
