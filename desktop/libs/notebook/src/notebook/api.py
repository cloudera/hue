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

import sqlparse
import urllib

from django.urls import reverse
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_GET, require_POST

from desktop.api2 import __paginate
from desktop.conf import IS_K8S_ONLY, TASK_SERVER
from desktop.lib.i18n import smart_str
from desktop.lib.django_util import JsonResponse
from desktop.models import Document2, Document
from indexer.file_format import HiveFormat
from indexer.fields import Field

from notebook.connectors.base import Notebook, QueryExpired, SessionExpired, QueryError, _get_snippet_name
from notebook.connectors.dataeng import DataEngApi
from notebook.connectors.hiveserver2 import HS2Api
from notebook.connectors.oozie_batch import OozieApi
from notebook.decorators import api_error_handler, check_document_access_permission, check_document_modify_permission
from notebook.models import escape_rows, make_notebook
from notebook.views import upgrade_session_properties, get_api


LOG = logging.getLogger(__name__)

DEFAULT_HISTORY_NAME = ''


@require_POST
@api_error_handler
def create_notebook(request):
  response = {'status': -1}

  editor_type = request.POST.get('type', 'notebook')
  directory_uuid = request.POST.get('directory_uuid')

  editor = Notebook()
  data = editor.get_data()

  if editor_type != 'notebook':
    data['name'] = ''
    data['type'] = 'query-%s' % editor_type  # TODO: Add handling for non-SQL types

  data['directoryUuid'] = directory_uuid
  editor.data = json.dumps(data)

  response['notebook'] = editor.get_data()
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def create_session(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  session = json.loads(request.POST.get('session', '{}'))

  if IS_K8S_ONLY.get(): # TODO: create session happening asynchronously on cluster selection when opening Notebook
    return JsonResponse({
      "status": 0,
      "session": {
        "reuse_session": True, "type": session['type'],
        "properties": [
          {"nice_name": "Settings", "multiple": True, "key": "settings", "help_text": "Hive and Hadoop configuration properties.", "defaultValue": [], "type": "settings", "options": ["hive.map.aggr", "hive.exec.compress.output", "hive.exec.parallel", "hive.execution.engine", "mapreduce.job.queuename"], "value": []}
        ]
      }
    })

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


def _execute_notebook(request, notebook, snippet):
  response = {'status': -1}
  result = None
  history = None

  historify = (notebook['type'] != 'notebook' or snippet.get('wasBatchExecuted')) and not notebook.get('skipHistorify')

  try:
    try:
      session = notebook.get('sessions') and notebook['sessions'][0] # Session reference for snippet execution without persisting it
      if historify:
        history = _historify(notebook, request.user)
        notebook = Notebook(document=history).get_data()

      interpreter = get_api(request, snippet)
      if snippet.get('interface') == 'sqlalchemy':
        interpreter.options['session'] = session

      response['handle'] = interpreter.execute(notebook, snippet)

      # Retrieve and remove the result from the handle
      if response['handle'].get('sync'):
        result = response['handle'].pop('result')
    finally:
      if historify:
        _snippet = [s for s in notebook['snippets'] if s['id'] == snippet['id']][0]
        if 'handle' in response: # No failure
          _snippet['result']['handle'] = response['handle']
          _snippet['result']['statements_count'] = response['handle'].get('statements_count', 1)
          _snippet['result']['statement_id'] = response['handle'].get('statement_id', 0)
          _snippet['result']['handle']['statement'] = response['handle'].get('statement', snippet['statement']).strip() # For non HS2, as non multi query yet
        else:
          _snippet['status'] = 'failed'

        if history:  # If _historify failed, history will be None
          history.update_data(notebook)
          history.save()

          response['history_id'] = history.id
          response['history_uuid'] = history.uuid
          if notebook['isSaved']: # Keep track of history of saved queries
            response['history_parent_uuid'] = history.dependencies.filter(type__startswith='query-').latest('last_modified').uuid
  except QueryError, ex: # We inject the history information from _historify() to the failed queries
    if response.get('history_id'):
      ex.extra['history_id'] = response['history_id']
    if response.get('history_uuid'):
      ex.extra['history_uuid'] = response['history_uuid']
    if response.get('history_parent_uuid'):
      ex.extra['history_parent_uuid'] = response['history_parent_uuid']
    raise ex

  # Inject and HTML escape results
  if result is not None:
    response['result'] = result
    response['result']['data'] = escape_rows(result['data'])

  response['status'] = 0

  return response

@require_POST
@check_document_access_permission()
@api_error_handler
def execute(request, engine=None):
  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  response = _execute_notebook(request, notebook, snippet)

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def check_status(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  if not snippet:
    nb_doc = Document2.objects.get_by_uuid(user=request.user, uuid=notebook['id'])
    notebook = Notebook(document=nb_doc).get_data()
    snippet = notebook['snippets'][0]

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

    if notebook['type'].startswith('query') or notebook.get('isManaged'):
      nb_doc = Document2.objects.get(id=notebook['id'])
      if nb_doc.can_write(request.user):
        nb = Notebook(document=nb_doc).get_data()
        if status != nb['snippets'][0]['status']:
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
  rows = json.loads(request.POST.get('rows', '100'))
  start_over = json.loads(request.POST.get('startOver', 'false'))

  response['result'] = get_api(request, snippet).fetch_result(notebook, snippet, rows, start_over)

  # Materialize and HTML escape results
  if response['result'].get('data') and response['result'].get('type') == 'table' and not response['result'].get('isEscaped'):
    response['result']['data'] = escape_rows(response['result']['data'])
    response['result']['isEscaped'] = True

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
def fetch_result_size(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  response['result'] = get_api(request, snippet).fetch_result_size(notebook, snippet)
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

  full_log = smart_str(request.POST.get('full_log', ''))
  logs = smart_str(db.get_log(notebook, snippet, startFrom=startFrom, size=size))
  full_log += logs

  jobs = db.get_jobs(notebook, snippet, full_log)

  response['logs'] = logs.strip()
  response['progress'] = min(db.progress(notebook, snippet, logs=full_log), 99) if snippet['status'] != 'available' and snippet['status'] != 'success' else 100
  response['jobs'] = jobs
  response['isFullLogs'] = db.get_log_is_full_log(notebook, snippet)
  response['status'] = 0

  return JsonResponse(response)

def _save_notebook(notebook, user):
  notebook_type = notebook.get('type', 'notebook')
  save_as = False

  if notebook.get('parentSavedQueryUuid'): # We save into the original saved query, not into the query history
    notebook_doc = Document2.objects.get_by_uuid(user=user, uuid=notebook['parentSavedQueryUuid'])
  elif notebook.get('id'):
    notebook_doc = Document2.objects.get(id=notebook['id'])
  else:
    notebook_doc = Document2.objects.create(name=notebook['name'], uuid=notebook['uuid'], type=notebook_type, owner=user)
    Document.objects.link(notebook_doc, owner=notebook_doc.owner, name=notebook_doc.name, description=notebook_doc.description, extra=notebook_type)
    save_as = True

    if notebook.get('directoryUuid'):
      notebook_doc.parent_directory = Document2.objects.get_by_uuid(user=user, uuid=notebook.get('directoryUuid'), perm_type='write')
    else:
      notebook_doc.parent_directory = Document2.objects.get_home_directory(user)

  notebook['isSaved'] = True
  notebook['isHistory'] = False
  notebook['id'] = notebook_doc.id
  _clear_sessions(notebook)
  notebook_doc1 = notebook_doc._get_doc1(doc2_type=notebook_type)
  notebook_doc.update_data(notebook)
  notebook_doc.search = _get_statement(notebook)
  notebook_doc.name = notebook_doc1.name = notebook['name']
  notebook_doc.description = notebook_doc1.description = notebook['description']
  notebook_doc.save()
  notebook_doc1.save()

  return notebook_doc, save_as


@api_error_handler
@require_POST
@check_document_modify_permission()
def save_notebook(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))

  notebook_doc, save_as = _save_notebook(notebook, request.user)

  response['status'] = 0
  response['save_as'] = save_as
  response.update(notebook_doc.to_dict())
  response['message'] = request.POST.get('editorMode') == 'true' and _('Query saved successfully') or _('Notebook saved successfully')

  return JsonResponse(response)


def _clear_sessions(notebook):
  notebook['sessions'] = [_s for _s in notebook['sessions'] if _s['type'] in ('scala', 'spark', 'pyspark', 'sparkr', 'r')]


def _historify(notebook, user):
  query_type = notebook['type']
  name = notebook['name'] if (notebook['name'] and notebook['name'].strip() != '') else DEFAULT_HISTORY_NAME
  is_managed = notebook.get('isManaged') == True  # Prevents None

  if is_managed and Document2.objects.filter(uuid=notebook['uuid']).exists():
    history_doc = Document2.objects.get(uuid=notebook['uuid'])
  else:
    history_doc = Document2.objects.create(
      name=name,
      type=query_type,
      owner=user,
      is_history=True,
      is_managed=is_managed
    )

  # Link history of saved query
  if notebook['isSaved']:
    parent_doc = Document2.objects.get(uuid=notebook.get('parentSavedQueryUuid') or notebook['uuid']) # From previous history query or initial saved query
    notebook['parentSavedQueryUuid'] = parent_doc.uuid
    history_doc.dependencies.add(parent_doc)

  if not is_managed:
    Document.objects.link(
      history_doc,
      name=history_doc.name,
      owner=history_doc.owner,
      description=history_doc.description,
      extra=query_type
    )

  notebook['uuid'] = history_doc.uuid
  _clear_sessions(notebook)
  history_doc.update_data(notebook)
  history_doc.search = _get_statement(notebook)
  history_doc.save()

  return history_doc


def _get_statement(notebook):
  if notebook['snippets'] and len(notebook['snippets']) > 0:
    return Notebook.statement_with_variables(notebook['snippets'][0])
  return ''

@require_GET
@api_error_handler
@check_document_access_permission()
def get_history(request):
  response = {'status': -1}

  doc_type = request.GET.get('doc_type')
  doc_text = request.GET.get('doc_text')
  page = min(int(request.GET.get('page', 1)), 100)
  limit = min(int(request.GET.get('limit', 50)), 100)
  is_notification_manager = request.GET.get('is_notification_manager', 'false') == 'true'

  if is_notification_manager:
    docs = Document2.objects.get_tasks_history(user=request.user)
  else:
    docs = Document2.objects.get_history(doc_type='query-%s' % doc_type, user=request.user)

  if doc_text:
    docs = docs.filter(Q(name__icontains=doc_text) | Q(description__icontains=doc_text) | Q(search__icontains=doc_text))

  # Paginate
  docs = docs.order_by('-last_modified')
  response['count'] = docs.count()
  docs = __paginate(page, limit, queryset=docs)['documents']

  history = []
  for doc in docs:
    notebook = Notebook(document=doc).get_data()
    if 'snippets' in notebook:
      statement = notebook['description'] if is_notification_manager else _get_statement(notebook)
      history.append({
        'name': doc.name,
        'id': doc.id,
        'uuid': doc.uuid,
        'type': doc.type,
        'data': {
            'statement': statement[:1001] if statement else '',
            'lastExecuted': notebook['snippets'][0].get('lastExecuted', -1),
            'status':  notebook['snippets'][0]['status'],
            'parentSavedQueryUuid': notebook.get('parentSavedQueryUuid', '')
        } if notebook['snippets'] else {},
        'absoluteUrl': doc.get_absolute_url(),
      })
    else:
      LOG.error('Incomplete History Notebook: %s' % notebook)
  response['history'] = sorted(history, key=lambda row: row['data']['lastExecuted'], reverse=True)
  response['message'] = _('History fetched')
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@api_error_handler
@check_document_modify_permission()
def clear_history(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook'), '{}')
  doc_type = request.POST.get('doc_type')
  is_notification_manager = request.POST.get('is_notification_manager', 'false') == 'true'

  if is_notification_manager:
    history = Document2.objects.get_tasks_history(user=request.user)
  else:
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
  notebook = upgrade_session_properties(request, notebook)

  response['status'] = 0
  response['notebook'] = notebook.get_json()
  response['message'] = _('Notebook loaded successfully')


@require_POST
@check_document_access_permission()
def close_notebook(request):
  response = {'status': -1, 'result': []}

  notebook = json.loads(request.POST.get('notebook', '{}'))

  for session in [_s for _s in notebook['sessions'] if _s['type'] in ('scala', 'spark', 'pyspark', 'sparkr', 'r')]:
    try:
      response['result'].append(get_api(request, session).close_session(session))
    except QueryExpired:
      pass
    except Exception, e:
      LOG.exception('Error closing session %s' % str(e))

  for snippet in [_s for _s in notebook['snippets'] if _s['type'] in ('hive', 'impala')]:
    try:
      if snippet['status'] != 'running':
        response['result'].append(get_api(request, snippet).close_statement(notebook, snippet))
      else:
        LOG.info('Not closing SQL snippet as still running.')
    except QueryExpired:
      pass
    except Exception, e:
      LOG.exception('Error closing statement %s' % str(e))

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
    response['result'] = get_api(request, snippet).close_statement(notebook, snippet)
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
  async = json.loads(request.POST.get('async', 'false'))
  operation = json.loads(request.POST.get('operation', '"default"'))

  sample_data = get_api(request, snippet).get_sample_data(snippet, database, table, column, async=async, operation=operation)
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


@require_POST
@api_error_handler
def format(request):
  response = {'status': 0}

  statements = request.POST.get('statements', '')
  response['formatted_statements'] = sqlparse.format(statements, reindent=True, keyword_case='upper') # SQL only currently

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def export_result(request):
  response = {'status': -1, 'message': _('Success')}

  # Passed by check_document_access_permission but unused by APIs
  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))
  data_format = json.loads(request.POST.get('format', '"hdfs-file"'))
  destination = urllib.unquote(json.loads(request.POST.get('destination', '""')))
  overwrite = json.loads(request.POST.get('overwrite', 'false'))
  is_embedded = json.loads(request.POST.get('is_embedded', 'false'))
  start_time = json.loads(request.POST.get('start_time', '-1'))

  api = get_api(request, snippet)

  if data_format == 'hdfs-file': # Blocking operation, like downloading
    if request.fs.isdir(destination):
      if notebook.get('name'):
        destination += '/%(name)s.csv' % notebook
      else:
        destination += '/%(type)s-%(id)s.csv' % notebook
    if overwrite and request.fs.exists(destination):
      request.fs.do_as_user(request.user.username, request.fs.rmtree, destination)
    response['watch_url'] = api.export_data_as_hdfs_file(snippet, destination, overwrite)
    response['status'] = 0
    request.audit = {
      'operation': 'EXPORT',
      'operationText': 'User %s exported to HDFS destination: %s' % (request.user.username, destination),
      'allowed': True
    }
  elif data_format == 'hive-table':
    if is_embedded:
      sql, success_url = api.export_data_as_table(notebook, snippet, destination)

      task = make_notebook(
        name=_('Export %s query to table %s') % (snippet['type'], destination),
        description=_('Query %s to %s') % (_get_snippet_name(notebook), success_url),
        editor_type=snippet['type'],
        statement=sql,
        status='ready',
        database=snippet['database'],
        on_success_url=success_url,
        last_executed=start_time,
        is_task=True
      )
      response = task.execute(request)
    else:
      notebook_id = notebook['id'] or request.GET.get('editor', request.GET.get('notebook'))
      response['watch_url'] = reverse('notebook:execute_and_watch') + '?action=save_as_table&notebook=' + str(notebook_id) + '&snippet=0&destination=' + destination
      response['status'] = 0
    request.audit = {
      'operation': 'EXPORT',
      'operationText': 'User %s exported to Hive table: %s' % (request.user.username, destination),
      'allowed': True
    }
  elif data_format == 'hdfs-directory':
    if is_embedded:
      sql, success_url = api.export_large_data_to_hdfs(notebook, snippet, destination)

      task = make_notebook(
        name=_('Export %s query to directory') % snippet['type'],
        description=_('Query %s to %s') % (_get_snippet_name(notebook), success_url),
        editor_type=snippet['type'],
        statement=sql,
        status='ready-execute',
        database=snippet['database'],
        on_success_url=success_url,
        last_executed=start_time,
        is_task=True
      )
      response = task.execute(request)
    else:
      notebook_id = notebook['id'] or request.GET.get('editor', request.GET.get('notebook'))
      response['watch_url'] = reverse('notebook:execute_and_watch') + '?action=insert_as_query&notebook=' + str(notebook_id) + '&snippet=0&destination=' + destination
      response['status'] = 0
    request.audit = {
      'operation': 'EXPORT',
      'operationText': 'User %s exported to HDFS directory: %s' % (request.user.username, destination),
      'allowed': True
    }
  elif data_format in ('search-index', 'dashboard'):
    # Open the result in the Dashboard via a SQL sub-query or the Import wizard (quick vs scalable)
    if is_embedded:
      notebook_id = notebook['id'] or request.GET.get('editor', request.GET.get('notebook'))

      if data_format == 'dashboard':
        engine = notebook['type'].replace('query-', '')
        response['watch_url'] = reverse('dashboard:browse', kwargs={'name': notebook_id}) + '?source=query&engine=%(engine)s' % {'engine': engine}
        response['status'] = 0
      else:
        sample = get_api(request, snippet).fetch_result(notebook, snippet, rows=4, start_over=True)
        for col in sample['meta']:
          col['type'] = HiveFormat.FIELD_TYPE_TRANSLATE.get(col['type'], 'string')

        response['status'] = 0
        response['id'] = notebook_id
        response['name'] = _get_snippet_name(notebook)
        response['source_type'] = 'query'
        response['target_type'] = 'index'
        response['target_path'] = destination
        response['sample'] = list(sample['data'])
        response['columns'] = [
            Field(col['name'], col['type']).to_dict() for col in sample['meta']
        ]
    else:
      notebook_id = notebook['id'] or request.GET.get('editor', request.GET.get('notebook'))
      response['watch_url'] = reverse('notebook:execute_and_watch') + '?action=index_query&notebook=' + str(notebook_id) + '&snippet=0&destination=' + destination
      response['status'] = 0

    if response.get('status') != 0:
      response['message'] =  _('Exporting result failed.')

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def statement_risk(request):
  response = {'status': -1, 'message': ''}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  api = HS2Api(request.user, snippet)

  response['query_complexity'] = api.statement_risk(notebook, snippet)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def statement_compatibility(request):
  response = {'status': -1, 'message': ''}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))
  source_platform = request.POST.get('sourcePlatform')
  target_platform = request.POST.get('targetPlatform')

  api = get_api(request, snippet)

  response['query_compatibility'] = api.statement_compatibility(notebook, snippet, source_platform=source_platform, target_platform=target_platform)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def statement_similarity(request):
  response = {'status': -1, 'message': ''}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))
  source_platform = request.POST.get('sourcePlatform')

  api = get_api(request, snippet)

  response['statement_similarity'] = api.statement_similarity(notebook, snippet, source_platform=source_platform)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@check_document_access_permission()
@api_error_handler
def get_external_statement(request):
  response = {'status': -1, 'message': ''}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  if snippet.get('statementType') == 'file':
    response['statement'] = _get_statement_from_file(request.user, request.fs, snippet)
  elif snippet.get('statementType') == 'document':
    notebook = Notebook(Document2.objects.get_by_uuid(user=request.user, uuid=snippet['associatedDocumentUuid'], perm_type='read'))
    response['statement'] = notebook.get_str()

  response['status'] = 0

  return JsonResponse(response)


def _get_statement_from_file(user, fs, snippet):
  script_path = snippet['statementPath']
  if script_path:
    script_path = script_path.replace('hdfs://', '')
    if fs.do_as_user(user, fs.isfile, script_path):
      return fs.do_as_user(user, fs.read, script_path, 0, 16 * 1024 ** 2)


@require_POST
@api_error_handler
def describe(request, database, table=None, column=None):
  response = {'status': -1, 'message': ''}
  notebook = json.loads(request.POST.get('notebook', '{}'))
  source_type = request.POST.get('source_type', '')
  snippet = {'type': source_type}

  describe = get_api(request, snippet).describe(notebook, snippet, database, table, column=column)
  response.update(describe)

  return JsonResponse(response)
