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

from django.core.urlresolvers import reverse
from django.forms import ValidationError
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_GET, require_POST

from desktop.lib.django_util import JsonResponse
from desktop.models import Document2, Document

from notebook.connectors.base import get_api, Notebook, QueryExpired, SessionExpired
from notebook.decorators import api_error_handler, check_document_access_permission, check_document_modify_permission
from notebook.github import GithubClient
from notebook.models import escape_rows


LOG = logging.getLogger(__name__)


DEFAULT_HISTORY_NAME = _('Query history')


@require_POST
@check_document_access_permission()
@api_error_handler
def create_session(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  session = json.loads(request.POST.get('session', '{}'))

  properties = session.get('properties', [])

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

  try:
    response['handle'] = get_api(request, snippet).execute(notebook, snippet)
  finally:
    if notebook['type'].startswith('query-'):
      _snippet = [s for s in notebook['snippets'] if s['id'] == snippet['id']][0]
      if 'handle' in response: # No failure
        _snippet['result']['handle'] = response['handle']
      else:
        _snippet['status'] = 'failed'
      history = _historify(notebook, request.user)
      response['history_id'] = history.id
      response['history_uuid'] = history.uuid

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

  try:
    response['query_status'] = get_api(request, snippet).check_status(notebook, snippet)
    response['status'] = 0
  except SessionExpired:
    response['status'] = 'expired'
    raise
  except QueryExpired:
    response['status'] = 'expired'
    raise
  finally:
    if response['status'] == 0 and snippet['status'] != response['query_status']:
      status = response['query_status']['status']
    elif response['status'] == 'expired':
      status = 'expired'
    else:
      status = 'failed'
    if notebook['type'].startswith('query'):
      nb_doc = Document2.objects.get(id=notebook['id'])
      nb_doc.can_write_or_exception(request.user)
      nb = Notebook(document=nb_doc).get_data()
      nb['snippets'][0]['status'] = status
      nb_doc.update_data(nb)
      nb_doc.save()

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
  parent_uuid = notebook.get('parent_uuid', None)
  parent = Document2.objects.get_home_directory(request.user)
  if parent_uuid:
    parent = Document2.objects.get_by_uuid(parent_uuid)

  if notebook.get('id'):
    notebook_doc = Document2.objects.get(id=notebook['id'])
  else:
    notebook_doc = Document2.objects.create(name=notebook['name'], uuid=notebook['uuid'], type=notebook_type, owner=request.user)
    Document.objects.link(notebook_doc, owner=notebook_doc.owner, name=notebook_doc.name, description=notebook_doc.description, extra=notebook_type)

  notebook_doc1 = notebook_doc.doc.get()
  notebook_doc.update_data(notebook)
  notebook_doc.name = notebook_doc1.name = notebook['name']
  notebook_doc.description = notebook_doc1.description = notebook['description']
  notebook_doc.parent_directory = parent
  notebook_doc.save()
  notebook_doc1.save()

  response['status'] = 0
  response['id'] = notebook_doc.id
  response['message'] = request.POST.get('editorMode') == 'true' and _('Query saved successfully') or _('Notebook saved successfully')

  return JsonResponse(response)



def _historify(notebook, user):
  query_type = notebook['type']
  name = notebook['name'] if notebook['name'] and notebook['name'].strip() != '' else DEFAULT_HISTORY_NAME

  history_doc = Document2.objects.create(
    name=name,
    type=query_type,
    owner=user,
    is_history=True
  )
  Document.objects.link(
    history_doc,
    name=history_doc.name,
    owner=history_doc.owner,
    description=history_doc.description,
    extra=query_type
  )

  notebook['uuid'] = history_doc.uuid
  history_doc.update_data(notebook)
  history_doc.save()

  return history_doc


@require_GET
@api_error_handler
@check_document_access_permission()
def get_history(request):
  response = {'status': -1}

  doc_type = request.GET.get('doc_type')
  limit = max(request.GET.get('len', 50), 100)

  response['status'] = 0
  response['history'] = [{
      'name': doc.name,
      'id': doc.id,
      'uuid': doc.uuid,
      'data': Notebook(document=doc).get_data(),
      'absoluteUrl': doc.get_absolute_url(),
      } for doc in Document2.objects.get_history(doc_type='query-%s' % doc_type, user=request.user).order_by('-last_modified')[:limit]]
  response['message'] = _('History fetched')

  return JsonResponse(response)


@require_POST
@api_error_handler
@check_document_modify_permission()
def clear_history(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook'), '{}')
  doc_type = request.POST.get('doc_type')

  history = Document2.objects.get_history(doc_type='query-%s' % doc_type, user=request.user)

  response['updated'] = history.delete()
  response['message'] = _('History cleared !')
  response['status'] = 0

  return JsonResponse(response)


@require_GET
@check_document_access_permission()
def open_notebook(request):
  response = {'status': -1}

  notebook_id = request.GET.get('notebook')
  notebook = Notebook(document=Document2.objects.get(id=notebook_id))

  # Check session properties format and upgrade if necessary
  data = notebook.get_data()
  for session in data['sessions']:
    api = get_api(request, session)
    if 'type' in session and hasattr(api, 'upgrade_properties'):
      properties = session.get('properties', None)
      session['properties'] = api.upgrade_properties(session['type'], properties)
  notebook.data = json.dumps(data)

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


@require_POST
@check_document_access_permission()
@api_error_handler
def get_sample_data(request, server=None, database=None, table=None, column=None):
  response = {'status': -1}

  # Passed by check_document_access_permission but unused by APIs
  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  sample_data = get_api(request, snippet).get_sample_data(snippet, database, table, column)
  response.update(sample_data)

  response['status'] = 0

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def explain(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  response = get_api(request, snippet).explain(notebook, snippet)

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


@require_POST
@check_document_access_permission()
@api_error_handler
def export_result(request):
  response = {'status': -1, 'message': _('Exporting result failed.')}

  # Passed by check_document_access_permission but unused by APIs
  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))
  data_format = json.loads(request.POST.get('format', 'hdfs-file'))
  destination = json.loads(request.POST.get('destination', ''))
  overwrite = json.loads(request.POST.get('overwrite', False))

  api = get_api(request, snippet)

  if data_format == 'hdfs-file':
    if overwrite and request.fs.exists(destination):
      if request.fs.isfile(destination):
        request.fs.do_as_user(request.user.username, request.fs.rmtree, destination)
      else:
        raise ValidationError(_("The target path is a directory"))
    response['watch_url'] = api.export_data_as_hdfs_file(snippet, destination, overwrite)
    response['status'] = 0
  elif data_format == 'hive-table':
    notebook_id = notebook['id'] or request.GET.get('editor', request.GET.get('notebook'))
    response['watch_url'] = reverse('notebook:execute_and_watch') + '?action=save_as_table&notebook=' + str(notebook_id) + '&snippet=0&destination=' + destination
    response['status'] = 0
  elif data_format == 'hdfs-directory':
    notebook_id = notebook['id'] or request.GET.get('editor', request.GET.get('notebook'))
    response['watch_url'] = reverse('notebook:execute_and_watch') + '?action=insert_as_query&notebook=' + str(notebook_id) + '&snippet=0&destination=' + destination
    response['status'] = 0

  return JsonResponse(response)
