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

from future import standard_library
standard_library.install_aliases()
from builtins import str, object
import datetime
import json
import logging
import math
import numbers
import sys
import uuid

from datetime import timedelta

from django.contrib.sessions.models import Session
from django.db.models import Count
from django.db.models.functions import Trunc
from django.utils.html import escape

from desktop.conf import has_connectors, TASK_SERVER
from desktop.lib.connectors.models import _get_installed_connectors
from desktop.lib.i18n import smart_unicode
from desktop.lib.paths import SAFE_CHARACTERS_URI
from desktop.models import Directory, Document2
from useradmin.models import User, install_sample_user

from notebook.conf import EXAMPLES, get_ordered_interpreters
from notebook.connectors.base import Notebook, get_api as _get_api, get_interpreter

if sys.version_info[0] > 2:
  from urllib.parse import quote as urllib_quote
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
  from urllib import quote as urllib_quote


LOG = logging.getLogger(__name__)


# Materialize and HTML escape results
def escape_rows(rows, nulls_only=False, encoding=None):
  data = []

  try:
    for row in rows:
      escaped_row = []

      for field in row:
        if isinstance(field, numbers.Number):
          if math.isnan(field) or math.isinf(field):
            escaped_field = json.dumps(field)
          else:
            escaped_field = field
        elif field is None:
          escaped_field = 'NULL'
        else:
          # Prevent error when getting back non utf8 like charset=iso-8859-1
          escaped_field = smart_unicode(field, errors='replace', encoding=encoding)
          if not nulls_only:
            escaped_field = escape(escaped_field).replace(' ', '&nbsp;')
        escaped_row.append(escaped_field)
      data.append(escaped_row)
  except RuntimeError:
    pass  # pep-0479: expected Py3.8 generator raised StopIteration

  return data


def make_notebook(
    name='Browse', description='', editor_type='hive', statement='', status='ready',
    files=None, functions=None, settings=None, is_saved=False, database='default', snippet_properties=None, batch_submit=False,
    on_success_url=None, skip_historify=False, is_task=False, last_executed=-1, is_notebook=False, pub_sub_url=None, result_properties={},
    namespace=None, compute=None, is_presentation_mode=False):
  '''
  skip_historify: do not add the task to the query history. e.g. SQL Dashboard
  is_task / isManaged: true when being a managed by Hue operation (include_managed=True in document),
  e.g. exporting query result, dropping some tables
  '''
  from notebook.connectors.hiveserver2 import HS2Api

  if has_connectors():
    interpreter = get_interpreter(connector_type=editor_type)
    editor_connector = editor_type
    editor_type = interpreter['dialect']
  else:
    editor_connector = editor_type

  editor = Notebook()
  if snippet_properties is None:
    snippet_properties = {}

  if editor_type == 'hive':
    sessions_properties = HS2Api.get_properties(editor_type)
    if files is not None:
      _update_property_value(sessions_properties, 'files', files)

    if functions is not None:
      _update_property_value(sessions_properties, 'functions', functions)

    if settings is not None:
      _update_property_value(sessions_properties, 'settings', settings)
  elif editor_type == 'impala':
    sessions_properties = HS2Api.get_properties(editor_type)
    if settings is not None:
      _update_property_value(sessions_properties, 'files', files)
  elif editor_type == 'java':
    sessions_properties = [] # Java options
  else:
    sessions_properties = []

  data = {
    'name': name,
    'uuid': str(uuid.uuid4()),
    'description': description,
    'sessions': [
      {
         'type': editor_connector,
         'properties': sessions_properties,
         'id': None
      }
    ],
    'selectedSnippet': editor_connector, # TODO: might need update in notebook.ko.js
    'type': 'notebook' if is_notebook else 'query-%s' % editor_type,
    'showHistory': True,
    'isSaved': is_saved,
    'onSuccessUrl': urllib_quote(on_success_url.encode('utf-8'), safe=SAFE_CHARACTERS_URI) if on_success_url else None,
    'pubSubUrl': pub_sub_url,
    'skipHistorify': skip_historify,
    'isPresentationModeDefault': is_presentation_mode,
    'isManaged': is_task,
    'snippets': [
      {
         'status': status,
         'id': str(uuid.uuid4()),
         'statement_raw': statement,
         'statement': statement,
         'type': editor_connector,
         'wasBatchExecuted': batch_submit,
         'lastExecuted': last_executed,
         'properties': {
            'files': [] if files is None else files,
            'functions': [] if functions is None else functions,
            'settings': [] if settings is None else settings
         },
         'name': name,
         'database': database,
         'namespace': namespace if namespace else {},
         'compute': compute if compute else {},
         'result': {'handle': {}},
         'variables': []
      }
    ] if not is_notebook else []
  }

  if has_connectors():  # To improve
    data['dialect'] = interpreter['dialect']
    data['type'] = '%s-%s' % (editor_type, editor_connector)  # e.g. 'flink-' + editor_connector

  if snippet_properties:
    data['snippets'][0]['properties'].update(snippet_properties)
  if result_properties:
    data['snippets'][0]['result'].update(result_properties)

  editor.data = json.dumps(data)

  return editor


def make_notebook2(name='Browse', description='', is_saved=False, snippets=None):

  from notebook.connectors.hiveserver2 import HS2Api

  editor = Notebook()

  _snippets = []

  for snippet in snippets:
    default_properties = {
        'files': [],
        'functions': [],
        'settings': []
    }

    default_properties.update(snippet['properties'])
    snippet['properties'] = default_properties

    _snippets.append(snippet)

  data = {
    'name': name,
    'uuid': str(uuid.uuid4()),
    'type': 'notebook',
    'description': description,
    'sessions': [
      {
        'type': _snippet['type'],
        'properties': HS2Api.get_properties(snippet['type']),
        'id': None
      } for _snippet in _snippets # Non unique types currently
    ],
    'selectedSnippet': _snippets[0]['type'],
    'showHistory': False,
    'isSaved': is_saved,
    'snippets': [
      {
         'status': _snippet.get('status', 'ready'),
         'id': str(uuid.uuid4()),
         'statement_raw': _snippet.get('statement', ''),
         'statement': _snippet.get('statement', ''),
         'type': _snippet.get('type'),
         'properties': _snippet['properties'],
         'name': name,
         'database': _snippet.get('database'),
         'result': {'handle': {}},
         'variables': []
      } for _snippet in _snippets
    ]
  }

  editor.data = json.dumps(data)

  return editor


def _get_notebook_api(user, connector_id, interpreter=None):
  '''
  Helper utils until the API gets simplified.
  '''
  notebook_json = """
    {
      "selectedSnippet": "hive",
      "showHistory": false,
      "description": "Test Query",
      "name": "Test Query",
      "sessions": [
          {
              "type": "hive",
              "properties": [],
              "id": null
          }
      ],
      "type": "hive",
      "id": null,
      "snippets": [{"id":"2b7d1f46-17a0-30af-efeb-33d4c29b1055","type":"%(connector_id)s","status":"running",\
         "statement":"select * from web_logs","properties":{"settings":[],"variables":[],"files":[],"functions":[]},\
          "result":{"id":"b424befa-f4f5-8799-a0b4-79753f2552b1","type":"table",\
          "handle":{"log_context":null,"statements_count":1,\
          "end":{"column":21,"row":0},"statement_id":0,"has_more_statements":false,\
          "start":{"column":0,"row":0},"secret":"rVRWw7YPRGqPT7LZ/TeFaA==an","has_result_set":true,\
          "statement":"select * from web_logs","operation_type":0,"modified_row_count":null,"guid":"7xm6+epkRx6dyvYvGNYePA==an"}},\
          "lastExecuted": 1462554843817,"database":"default"}],
      "uuid": "d9efdee1-ef25-4d43-b8f9-1a170f69a05a"
  }
  """ % {
    'connector_id': connector_id,
  }
  snippet = json.loads(notebook_json)['snippets'][0]
  snippet['interpreter'] = interpreter

  request = MockRequest(user)

  return get_api(request, snippet)


class MockedDjangoRequest(object):

  def __init__(self, user, get=None, post=None, method='POST'):
    self.user = user
    self.jt = None
    self.GET = get if get is not None else {'format': 'json'}
    self.POST = post if post is not None else {}
    self.REQUEST = {}
    self.method = method


def import_saved_beeswax_query(bquery, interpreter=None):
  design = bquery.get_design()

  return make_notebook(
      name=bquery.name,
      description=bquery.desc,
      editor_type=interpreter['type'] if interpreter else _convert_type(bquery.type, bquery.data),
      statement=design.hql_query,
      status='ready',
      files=design.file_resources,
      functions=design.functions,
      settings=design.settings,
      is_saved=True,
      database=design.database
  )


def import_saved_pig_script(pig_script):
  snippet_properties = {}

  snippet_properties['hadoopProperties'] = []
  if pig_script.dict.get('hadoopProperties'):
    for prop in pig_script.dict.get('hadoopProperties'):
      snippet_properties['hadoopProperties'].append("%s=%s" % (prop.get('name'), prop.get('value')))

  snippet_properties['parameters'] = []
  if pig_script.dict.get('parameters'):
    for param in pig_script.dict.get('parameters'):
      snippet_properties['parameters'].append("%s=%s" % (param.get('name'), param.get('value')))

  snippet_properties['resources'] = []
  if pig_script.dict.get('resources'):
    for resource in pig_script.dict.get('resources'):
      snippet_properties['resources'].append(resource.get('value'))

  notebook = make_notebook(
    name=pig_script.dict.get('name'),
    editor_type='pig',
    statement=pig_script.dict.get('script'),
    status='ready',
    snippet_properties=snippet_properties,
    is_saved=True
  )

  # Remove files, functions, settings from snippet properties
  data = notebook.get_data()
  data['snippets'][0]['properties'].pop('files')
  data['snippets'][0]['properties'].pop('functions')
  data['snippets'][0]['properties'].pop('settings')

  notebook.data = json.dumps(data)
  return notebook


def import_saved_mapreduce_job(wf):
  snippet_properties = {}
  node = wf.start.get_child('to')

  try:
    files = json.loads(node.files)
    for filepath in files:
      snippet_properties['files'].append({'type': 'file', 'path': filepath})
  except ValueError as e:
    LOG.warning('Failed to parse files for mapreduce job design "%s".' % wf.name)

  snippet_properties['archives'] = []
  try:
    archives = json.loads(node.archives)
    for filepath in archives:
      snippet_properties['archives'].append(filepath)
  except ValueError as e:
    LOG.warning('Failed to parse archives for mapreduce job design "%s".' % wf.name)

  snippet_properties['hadoopProperties'] = []
  try:
    properties = json.loads(node.job_properties)
    if properties:
      for prop in properties:
        snippet_properties['hadoopProperties'].append("%s=%s" % (prop.get('name'), prop.get('value')))
  except ValueError as e:
    LOG.warning('Failed to parse job properties for mapreduce job design "%s".' % wf.name)

  snippet_properties['app_jar'] = node.jar_path

  notebook = make_notebook(
    name=wf.name,
    description=wf.description,
    editor_type='mapreduce',
    statement='',
    status='ready',
    snippet_properties=snippet_properties,
    is_saved=True
  )

  # Remove functions, settings from snippet properties
  data = notebook.get_data()
  data['snippets'][0]['properties'].pop('functions')
  data['snippets'][0]['properties'].pop('settings')

  notebook.data = json.dumps(data)
  return notebook


def import_saved_shell_job(wf):
  snippet_properties = {}
  node = wf.start.get_child('to')

  snippet_properties['command_path'] = node.command

  snippet_properties['arguments'] = []
  snippet_properties['env_var'] = []
  try:
    params = json.loads(node.params)
    if params:
      for param in params:
        if param['type'] == 'argument':
          snippet_properties['arguments'].append(param['value'])
        else:
          snippet_properties['env_var'].append(param['value'])
  except ValueError as e:
    LOG.warning('Failed to parse parameters for shell job design "%s".' % wf.name)

  snippet_properties['hadoopProperties'] = []
  try:
    properties = json.loads(node.job_properties)
    if properties:
      for prop in properties:
        snippet_properties['hadoopProperties'].append("%s=%s" % (prop.get('name'), prop.get('value')))
  except ValueError as e:
    LOG.warning('Failed to parse job properties for shell job design "%s".' % wf.name)

  snippet_properties['files'] = []
  try:
    files = json.loads(node.files)
    for filepath in files:
      snippet_properties['files'].append({'type': 'file', 'path': filepath})
  except ValueError as e:
    LOG.warning('Failed to parse files for shell job design "%s".' % wf.name)

  snippet_properties['archives'] = []
  try:
    archives = json.loads(node.archives)
    for archive in archives:
      snippet_properties['archives'].append(archive['name'])
  except ValueError as e:
    LOG.warning('Failed to parse archives for shell job design "%s".' % wf.name)

  snippet_properties['capture_output'] = node.capture_output

  notebook = make_notebook(
      name=wf.name,
      description=wf.description,
      editor_type='shell',
      statement='',
      status='ready',
      snippet_properties=snippet_properties,
      is_saved=True
  )

  # Remove functions, settings from snippet properties
  data = notebook.get_data()
  data['snippets'][0]['properties'].pop('functions')
  data['snippets'][0]['properties'].pop('settings')

  notebook.data = json.dumps(data)
  return notebook


def import_saved_java_job(wf):
  snippet_properties = {}
  node = wf.start.get_child('to')

  snippet_properties['app_jar'] = node.jar_path
  snippet_properties['class'] = node.main_class
  snippet_properties['args'] = node.args if node.args else ''
  snippet_properties['java_opts'] = node.java_opts if node.java_opts else ''

  snippet_properties['hadoopProperties'] = []
  try:
    properties = json.loads(node.job_properties)
    if properties:
      for prop in properties:
        snippet_properties['hadoopProperties'].append("%s=%s" % (prop.get('name'), prop.get('value')))
  except ValueError as e:
    LOG.warning('Failed to parse job properties for Java job design "%s".' % wf.name)

  snippet_properties['files'] = []
  try:
    files = json.loads(node.files)
    for filepath in files:
      snippet_properties['files'].append({'type': 'file', 'path': filepath})
  except ValueError as e:
    LOG.warning('Failed to parse files for Java job design "%s".' % wf.name)

  snippet_properties['archives'] = []
  try:
    archives = json.loads(node.archives)
    for archive in archives:
      snippet_properties['archives'].append(archive['name'])
  except ValueError as e:
    LOG.warning('Failed to parse archives for Java job design "%s".' % wf.name)

  snippet_properties['capture_output'] = node.capture_output

  notebook = make_notebook(
      name=wf.name,
      description=wf.description,
      editor_type='java',
      statement='',
      status='ready',
      snippet_properties=snippet_properties,
      is_saved=True
  )

  # Remove functions, settings from snippet properties
  data = notebook.get_data()
  data['snippets'][0]['properties'].pop('functions')
  data['snippets'][0]['properties'].pop('settings')

  notebook.data = json.dumps(data)
  return notebook


def _convert_type(btype, bdata):
  from beeswax.models import HQL, IMPALA, RDBMS, SPARK

  if btype == HQL:
    return 'hive'
  elif btype == IMPALA:
    return 'impala'
  elif btype == RDBMS:
    data = json.loads(bdata)
    return data['query']['server']
  elif btype == SPARK: # We should not import
    return 'spark'
  else:
    return 'hive'


def _update_property_value(properties, key, value):
  """
  Update property dict in list of properties where prop has "key": key, set "value": value
  """
  for prop in properties:
    if prop['key'] == key:
      prop.update({'value': value})


def _get_editor_type(editor_id):
  document = Document2.objects.get(id=editor_id)
  return document.type.rsplit('-', 1)[-1]


def _get_example_directory(user):
  home_dir = Directory.objects.get_home_directory(user)
  examples_dir, created = Directory.objects.get_or_create(
    parent_directory=home_dir,
    owner=user,
    name=Document2.EXAMPLES_DIR
  )
  return examples_dir

def _get_dialect_example(dialect):
  sample_user = install_sample_user()
  examples_dir = _get_example_directory(sample_user)

  return Document2.objects.filter(
      owner=sample_user,
      type='query-%s' % dialect,
      is_history=False,
      parent_directory=examples_dir
  ).first()


class ApiWrapper():
  def __init__(self, request, snippet):
    self.request = request
    self.api = _get_api(request, snippet)

  def __getattr__(self, name):
    if TASK_SERVER.ENABLED.get():
      from notebook import tasks as ntasks
      if hasattr(ntasks, name):
        attr = getattr(ntasks, name)
        def _method(*args, **kwargs):
          return attr(*args, **dict(kwargs, postdict=self.request.POST, user_id=self.request.user.id))
        return _method
      else:
        LOG.debug('Skipping Task Server call %s' % name)
    return getattr(self.api, name)


def get_api(request, snippet):
  return ApiWrapper(request, snippet)


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


class Analytics(object):

  @classmethod
  def admin_stats(cls):
    stats = []
    one_day = datetime.date.today() - timedelta(days=1)
    one_week = datetime.date.today() - timedelta(weeks=1)
    one_month = datetime.date.today() - timedelta(days=30)
    three_months = datetime.date.today() - timedelta(days=90)

    stats.append(('Last modified', '1 day'))
    stats.append(('Users', User.objects.filter(last_login__gte=one_day).count()))
    stats.append(('Sessions', Session.objects.filter(expire_date__gte=one_day).count()))
    stats.append(('Executed queries', Document2.objects.filter(
        last_modified__gte=one_day, is_history=True, type__startswith='query-').count()
      )
    )

    stats.append(('\nLast modified', '1 week'))
    stats.append(('Users', User.objects.filter(last_login__gte=one_week).count()))
    stats.append(('Sessions', Session.objects.filter(expire_date__gte=one_week).count()))
    stats.append(('Executed queries', Document2.objects.filter(
        last_modified__gte=one_week, is_history=True, type__startswith='query-').count()
      )
    )
    stats.append(('Saved queries', Document2.objects.filter(
        last_modified__gte=one_week, is_history=False, type__startswith='query-').count()
      )
    )

    stats.append(('\nAll', ''))
    stats.append(('Active users 30 days', User.objects.filter(last_login__gte=one_month).count()))
    stats.append(('Sessions 30 days', Session.objects.filter(expire_date__gte=one_month).count()))
    stats.append(('Executed queries 30 days', Document2.objects.filter(
        last_modified__gte=one_month, is_history=True, type__startswith='query-').count()
      )
    )
    stats.append(('Active users 90 days', User.objects.filter(last_login__gte=three_months).count()))

    stats.append(('\nDialect executions', ''))
    queries = Document2.objects.filter(type__startswith='query-', is_trashed=False, is_managed=False)
    last_month_qdialects = queries.filter(
      last_modified__gte=one_month
    ).values('type').annotate(c=Count('type')).values('type', 'c').order_by('-c')
    stats.append(('30 days', ', '.join(['%(type)s: %(c)s' % d for d in last_month_qdialects])))

    return stats

  @classmethod
  def user_stats(cls, user_id=None, user=None):
    stats = []
    one_month = datetime.date.today() - timedelta(days=30)

    user = User.objects.get(id=user_id) if user is None else user
    queries = Document2.objects.filter(owner__id=user_id, type__startswith='query-', is_trashed=False, is_managed=False)

    stats.append({
      'name': 'user',
      'value': '%s - %s' % (user_id, user.username), 'description': _('User info')
    })
    query_executions = queries.filter(is_history=True, type__startswith='query-')
    stats.append({
      'name': 'query_executions',
      'values': query_executions.count(),
      'description': _('Query executions count')
    })
    stats.append({
      'name': 'saved_queries_count',
      'value': queries.filter(is_history=False, type__startswith='query-').count(),
      'description': _('Saved queries count')
    })
    stats.append({
      'name': 'query_executions_30_days_count',
      'value': query_executions.filter(last_modified__gte=one_month).count(),
      'description': _('Query executions 30 days total')
    })
    last_month_daily = queries.filter(
        last_modified__gte=one_month).annotate(
          day=Trunc('last_modified', 'day')
        ).values('day').annotate(c=Count('day')).values('day', 'c').order_by('day')
    stats.append({
      'name': 'query_executions_30_days_histogram',
      'value': last_month_daily,
      'description': _('Daily executions 30 days')
    })

    return stats

  @classmethod
  def query_stats(cls, query_id=None, query=None):
    stats = []
    one_month = datetime.date.today() - timedelta(days=30)

    query = Document2.objects.get(id=query_id) if query is None else query
    stats.append({
      'name': 'query',
      'value': '%s - %s' % (query_id, query.name),
      'description': _('Query info')
    })
    executions = query.dependents.filter(is_history=True, type__startswith='query-')
    stats.append({
      'name': 'execution_count',
      'value': executions.count(),
      'description': _('How many times executed')
    })
    stats.append({
      'name': 'execution_count_shared',
      'value': executions.exclude(owner=query.owner).count(),
      'description': _('Executions by others')
    })
    last_month_daily = executions.filter(
        last_modified__gte=one_month).annotate(
          day=Trunc('last_modified', 'day')
        ).values('day').annotate(c=Count('day')).values('day', 'c').order_by('day')
    stats.append({
      'name': 'executions_30_days_histogram',
      'value': last_month_daily,
      'description': _('Daily executions 30 days')
    })
    # Could count number of "forks" (but would need to start tracking parent of Saved As query cf. saveAsNotebook)

    return stats


class MockRequest():
  def __init__(self, user, fs=None, jt=None):
    self.user = user
    self.fs = fs
    self.jt = jt
    self.POST = {}
    self.GET = {}

def install_custom_examples():
  if EXAMPLES.AUTO_LOAD.get():
    from desktop.auth.backend import rewrite_user
    from beeswax.management.commands import beeswax_install_examples
    from useradmin.models import install_sample_user

    user = rewrite_user(
      install_sample_user()
    )

    if has_connectors():
      interpreters = [
        {
          'type': connector['id'],
          'dialect': connector['dialect']
        }
        for connector in _get_installed_connectors(category='editor')
      ]
    else:
      interpreters = [
        {
          'type': interpreter['dialect'],
          'dialect': interpreter['dialect']
        }
        for interpreter in get_ordered_interpreters(user)
        # Only for hive/impala currently, would also need to port to Notebook install examples.
        if interpreter['dialect'] in ('hive', 'impala')
      ]

    queries = EXAMPLES.QUERIES.get()
    tables = EXAMPLES.TABLES.get()  # No-op. Only for the saved query samples, not the tables currently.

    LOG.info('Installing custom examples queries: %(queries)s, tables: %(tables)s for dialects %(dialects)s '
      'belonging to user %(user)s' % {
        'queries': queries,
        'tables': tables,
        'dialects': [interpreter['dialect'] for interpreter in interpreters],
        'user': user
      }
    )

    result = []

    for interpreter in interpreters:
      successes, errors = beeswax_install_examples.Command().handle(
          dialect=interpreter['dialect'],
          user=user,
          interpreter=interpreter,
          queries=queries,
          tables=tables,
          request=None
      )
      LOG.info('Dialect %(dialect)s installed samples: %(successes)s, %(errors)s,' % {
        'dialect': interpreter['dialect'],
        'successes': successes,
        'errors': errors,
      })
      result.append((successes, errors))

    return result
