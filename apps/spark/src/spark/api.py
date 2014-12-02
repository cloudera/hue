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

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode
from desktop.models import Document2

from spark.models import get_api, Notebook


LOG = logging.getLogger(__name__)



def create_session(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  try:
    response['session'] = get_api(request.user, snippet).create_session(lang=snippet['type'])
    response['status'] = 0
  except Exception, e:
    response['error'] = force_unicode(str(e))

  return HttpResponse(json.dumps(response), mimetype="application/json")


def execute(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  try:
    response['handle'] = get_api(request.user, snippet).execute(notebook, snippet)
    response['status'] = 0
  except Exception, e:
    message = force_unicode(str(e))
    if 'session not found' in message:
      response['status'] = -2
    else:
      response['error'] = force_unicode(str(e))

  return HttpResponse(json.dumps(response), mimetype="application/json")


def check_status(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  try:
    response['query_status'] = get_api(request.user, snippet).check_status(notebook, snippet)
    response['status'] = 0
  except Exception, e:
    message = force_unicode(str(e))
    if 'session not found' in message:
      response['status'] = -2
    else:
      response['error'] = force_unicode(str(e))

  return HttpResponse(json.dumps(response), mimetype="application/json")


def fetch_result(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  try:
    response['result'] = get_api(request.user, snippet).fetch_result(notebook, snippet)
    response['status'] = 0
  except Exception, e:
    message = force_unicode(str(e))
    if 'session not found' in message:
      response['status'] = -2
    else:
      response['error'] = force_unicode(str(e))


  return HttpResponse(json.dumps(response), mimetype="application/json")


def save_notebook(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}')) # TODO perms

  if notebook.get('id'):
    notebook_doc = Document2.objects.get(id=notebook['id'])
  else:      
    notebook_doc = Document2.objects.create(name=notebook['name'], type='notebook', owner=request.user)

  notebook_doc.update_data(notebook)
  notebook_doc.name = notebook['name']
  notebook_doc.save()
  
  response['status'] = 0
  response['id'] = notebook_doc.id
  response['message'] = _('Notebook saved !')

  return HttpResponse(json.dumps(response), mimetype="application/json")


def open_notebook(request):
  response = {'status': -1}

  notebook_id = request.GET.get('notebook')
  notebook = Notebook(document=Document2.objects.get(id=notebook_id)) # Todo perms
  
  response['status'] = 0
  response['notebook'] = notebook.get_json()
  response['message'] = _('Notebook saved !')

  return HttpResponse(json.dumps(response), mimetype="application/json")
