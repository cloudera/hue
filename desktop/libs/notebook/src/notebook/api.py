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

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_GET, require_POST

from desktop.decorators import check_document_access_permission
from desktop.lib.django_util import JsonResponse
from desktop.models import Document2, Document

from notebook.connectors.base import get_api, Notebook, QueryExpired
from notebook.decorators import api_error_handler, check_document_modify_permission
from notebook.github import GithubClient
from notebook.models import escape_rows


LOG = logging.getLogger(__name__)


@require_POST
@check_document_access_permission()
@api_error_handler
def create_session(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  session = json.loads(request.POST.get('session', '{}'))

  properties = session.get('properties', [])

  # If not properties look for previously used notebook session
  if not properties:
    old_session = [_session for _session in notebook['sessions'] if _session['type'] == session['type']]
    if any(old_session) and 'properties' in old_session[0]:
      properties = old_session[0]['properties']

  response['session'] = get_api(request, session).create_session(lang=session['type'], properties=properties)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def close_session(request):
  response = {'status': -1}

  session = json.loads(request.POST.get('session', '{}'))

  response['session'] = get_api(request, {'type': session['type']}).close_session(session=session)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def execute(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  response['handle'] = get_api(request, snippet).execute(notebook, snippet)

  # Materialize and HTML escape results
  if response['handle'].get('sync') and response['handle']['result'].get('data'):
    response['handle']['result']['data'] = escape_rows(response['handle']['result']['data'])

  response['status'] = 0

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def check_status(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  response['query_status'] = get_api(request, snippet).check_status(notebook, snippet)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def fetch_result_data(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))
  rows = json.loads(request.POST.get('rows', 100))
  start_over = json.loads(request.POST.get('startOver', False))

  response['result'] = get_api(request, snippet).fetch_result(notebook, snippet, rows, start_over)

  # Materialize and HTML escape results
  if response['result'].get('data') and response['result'].get('type') == 'table':
    response['result']['data'] = escape_rows(response['result']['data'])

  response['status'] = 0

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def fetch_result_metadata(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  response['result'] = get_api(request, snippet).fetch_result_metadata(notebook, snippet)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def cancel_statement(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  response['result'] = get_api(request, snippet).cancel(notebook, snippet)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def get_logs(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  startFrom = request.POST.get('from')
  startFrom = int(startFrom) if startFrom else None

  size = request.POST.get('size')
  size = int(size) if size else None

  db = get_api(request, snippet)

  logs = db.get_log(notebook, snippet, startFrom=startFrom, size=size)

  jobs = json.loads(request.POST.get('jobs', '[]'))

  # Get any new jobs from current logs snippet
  new_jobs = db.get_jobs(notebook, snippet, logs)

  # Append new jobs to known jobs and get the unique set
  if new_jobs:
    all_jobs = jobs + new_jobs
    jobs = dict((job['name'], job) for job in all_jobs).values()

  # Retrieve full log for job progress parsing
  full_log = request.POST.get('full_log', logs)

  response['logs'] = logs
  response['progress'] = db.progress(snippet, full_log) if snippet['status'] != 'available' and snippet['status'] != 'success' else 100
  response['jobs'] = jobs
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@check_document_modify_permission()
def save_notebook(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  notebook_type = notebook.get('type', 'notebook')

  if notebook.get('id'):
    notebook_doc = Document2.objects.get(id=notebook['id'])
  else:
    notebook_doc = Document2.objects.create(name=notebook['name'], type=notebook_type, owner=request.user)
    Document.objects.link(notebook_doc, owner=notebook_doc.owner, name=notebook_doc.name, description=notebook_doc.description, extra=notebook_type)

  notebook_doc1 = notebook_doc.doc.get()
  notebook_doc.update_data(notebook)
  notebook_doc.name = notebook_doc1.name = notebook['name']
  notebook_doc.description = notebook_doc1.description = notebook['description']
  notebook_doc.save()
  notebook_doc1.save()

  response['status'] = 0
  response['id'] = notebook_doc.id
  response['message'] = request.POST.get('editorMode') == 'true' and _('Query saved successfully') or _('Notebook saved successfully')

  return JsonResponse(response)


@require_POST
@check_document_modify_permission()
def historify(request):
  response = {'status': -1}

  history = json.loads(request.POST.get('notebook', '{}'))
  query_type = history['type']

  history_doc = Document2.objects.create(name=history['name'], type=query_type, owner=request.user, is_history=True)
  Document.objects.link(history_doc, owner=history_doc.owner, name=history_doc.name, description=history_doc.description, extra=query_type)

  history_doc1 = history_doc.doc.get()
  history_doc.update_data(history)
  history_doc.name = history_doc1.name = history['name']
  history_doc.description = history_doc1.description = history.get('description', '')
  history_doc.is_history = True
  history_doc.save()
  history_doc1.save()

  if history.get('id'): # If we come from a saved query
    Document2.objects.get(id=history['id']).dependencies.add(history_doc)

  response['status'] = 0
  response['id'] = history_doc.id
  response['message'] = _('Query notebook history saved !')

  return JsonResponse(response)


@require_GET
def get_history(request):
  response = {'status': -1}

  doc_type = request.GET.get('doc_type')

  response['status'] = 0
  response['history'] = [{
      'name': doc.name,
      'id': doc.id,
      'data': Notebook(document=doc).get_data(),
      'absoluteUrl': doc.get_absolute_url()
      } for doc in Document2.objects.get_history(doc_type='query-%s' % doc_type, user=request.user)[:25]]
  response['message'] = _('History fetched')

  return JsonResponse(response)


@require_POST
@check_document_modify_permission()
def clear_history(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook'), '{}')
  doc_type = request.POST.get('doc_type')

  response['status'] = 0
  history = Document2.objects.get_history(doc_type='query-%s' % doc_type, user=request.user)
  if notebook.get('id'):
    history = history.exclude(id=notebook.get('id'))
  response['updated'] = history.delete()
  response['message'] = _('History cleared !')

  return JsonResponse(response)


@require_GET
@check_document_access_permission()
def open_notebook(request):
  response = {'status': -1}

  notebook_id = request.GET.get('notebook')
  notebook = Notebook(document=Document2.objects.get(id=notebook_id))

  response['status'] = 0
  response['notebook'] = notebook.get_json()
  response['message'] = _('Notebook loaded successfully')


@require_POST
@check_document_access_permission()
def close_notebook(request):
  response = {'status': -1, 'result': []}

  notebook = json.loads(request.POST.get('notebook', '{}'))

  for session in notebook['sessions']:
    try:
      response['result'].append(get_api(request, session).close_session(session))
    except QueryExpired:
      pass
    except Exception, e:
      LOG.exception('Error closing session %s' % str(e))

  response['status'] = 0
  response['message'] = _('Notebook closed successfully')

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
def close_statement(request):
  response = {'status': -1}

  # Passed by check_document_access_permission but unused by APIs
  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  try:
    response['result'] = get_api(request, snippet).close_statement(snippet)
  except QueryExpired:
    pass

  response['status'] = 0
  response['message'] = _('Statement closed !')

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def autocomplete(request, server=None, database=None, table=None, column=None, nested=None):
  response = {'status': -1}

  # Passed by check_document_access_permission but unused by APIs
  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  try:
    autocomplete_data = get_api(request, snippet).autocomplete(snippet, database, table, column, nested)
    response.update(autocomplete_data)
  except QueryExpired:
    pass

  response['status'] = 0

  return JsonResponse(response)


@require_GET
@api_error_handler
def github_fetch(request):
  response = {'status': -1}

  api = GithubClient(access_token=request.session.get('github_access_token'))

  response['url'] = url = request.GET.get('url')

  if url:
    owner, repo, branch, filepath = api.parse_github_url(url)
    content = api.get_file_contents(owner, repo, filepath, branch)
    try:
      response['content'] = json.loads(content)
    except ValueError:
      # Content is not JSON-encoded so return plain-text
      response['content'] = content
    response['status'] = 0
  else:
    return HttpResponseBadRequest(_('url param is required'))

  return JsonResponse(response)


@api_error_handler
def github_authorize(request):
  access_token = request.session.get('github_access_token')
  if access_token and GithubClient.is_authenticated(access_token):
    response = {
      'status': 0,
      'message': _('User is already authenticated to GitHub.')
    }
    return JsonResponse(response)
  else:
    auth_url = GithubClient.get_authorization_url()
    request.session['github_callback_redirect'] = request.GET.get('currentURL')
    request.session['github_callback_fetch'] = request.GET.get('fetchURL')
    response = {
      'status': -1,
      'auth_url':auth_url
    }
    if (request.is_ajax()):
      return JsonResponse(response)

    return HttpResponseRedirect(auth_url)


@api_error_handler
def github_callback(request):
  redirect_base = request.session['github_callback_redirect'] + "&github_status="
  if 'code' in request.GET:
    session_code = request.GET.get('code')
    request.session['github_access_token'] = GithubClient.get_access_token(session_code)
    return HttpResponseRedirect(redirect_base + "0&github_fetch=" + request.session['github_callback_fetch'])
  else:
    return HttpResponseRedirect(redirect_base + "-1&github_fetch=" + request.session['github_callback_fetch'])
