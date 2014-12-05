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
import re

from desktop.lib.i18n import smart_str, force_unicode
from desktop.lib.rest.http_client import RestException

from beeswax import models as beeswax_models
from beeswax.design import hql_query
from beeswax.models import QUERY_TYPES, HiveServerQueryHandle, QueryHistory
from beeswax.views import safe_get_design, save_design
from beeswax.server import dbms
from beeswax.server.dbms import get_query_server_config

from spark.job_server_api import get_api as get_spark_api


# To move to Editor API
class SessionExpired(Exception):
  pass


class QueryExpired(Exception):
  pass



class Notebook():
  
  def __init__(self, document=None):
    self.document = None
    
    if document is not None:
      self.data = document.data
      self.document = document
    else:    
      self.data = json.dumps({
          'name': 'My Notebook', 
          'snippets': [{'type': 'scala', 'result': {}}]
      })

  def get_json(self):
    _data = self.get_data()
    
    return json.dumps(_data)
 
  def get_data(self):
    _data = json.loads(self.data)
  
    if self.document is not None:
      _data['id'] = self.document.id 
  
    return _data


def get_api(user, snippet):
  if snippet['type'] in ('hive', 'impala', 'spark-sql'):
    return HS2Api(user)
  elif snippet['type'] == 'text':
    return TextApi(user)  
  else:
    return SparkApi(user)


def _get_snippet_session(notebook, snippet):
  return [session for session in notebook['sessions'] if session['type'] == snippet['type']][0] 


class TextApi():
  
  def __init__(self, user):
    self.user = user
    
  def create_session(self, lang):
    return {
        'type': lang,
        'id': None
    }
  

class HS2Api():
  
  def __init__(self, user):
    self.user = user
    
  def _get_handle(self, snippet):
    snippet['result']['handle']['secret'], snippet['result']['handle']['guid'] = HiveServerQueryHandle.get_decoded(snippet['result']['handle']['secret'], snippet['result']['handle']['guid'])
    return HiveServerQueryHandle(**snippet['result']['handle'])
    
  def _get_db(self, snippet):
    if snippet['type'] == 'hive':
      name = 'beeswax'
    elif snippet['type'] == 'impala':
      name = 'impala'
    else:
      name = 'spark-sql'
      
    return dbms.get(self.user, query_server=get_query_server_config(name=name))
    
  def create_session(self, lang):
    return {
        'type': lang,
        'id': None # Real one at some point
    }
  
  def execute(self, notebook, snippet):
    db = self._get_db(snippet)
    query = hql_query(snippet['statement'], QUERY_TYPES[0])
    handle = db.client.query(query)
    
#    if not handle.is_valid():
#        msg = _("Server returning invalid handle for query id %(id)d [%(query)s]...") % {'id': query_history.id, 'query': query[:40]}
#        raise QueryServerException(msg)
#    except QueryServerException, ex:
#      LOG.exception(ex)
#      # Kind of expected (hql compile/syntax error, etc.)
#      if hasattr(ex, 'handle') and ex.handle:
#        query_history.server_id, query_history.server_guid = ex.handle.id, ex.handle.id
#        query_history.log_context = ex.handle.log_context
#      query_history.save_state(QueryHistory.STATE.failed)
#      raise ex

    # All good
    server_id, server_guid  = handle.get()
    return {
        'secret': server_id,
        'guid': server_guid,
        'operation_type': handle.operation_type,
        'has_result_set': handle.has_result_set,
        'modified_row_count': handle.modified_row_count,
        'log_context': handle.log_context
    }    

  def check_status(self, notebook, snippet):
    db = self._get_db(snippet)
      
    handle = self._get_handle(snippet)

    try:
      status =  db.get_state(handle)
    except Exception, e:
      message = force_unicode(str(e))
      if 'Invalid query handle' in message or 'Invalid OperationHandle' in message:
        raise QueryExpired(e)
      else:
        raise e

    return {
        'status':
          'running' if status.index in (QueryHistory.STATE.running.index, QueryHistory.STATE.submitted.index)
          else (
             'failed' if status.index in (QueryHistory.STATE.failed.index, QueryHistory.STATE.expired.index)
              else 'available'
          )
    }

  def fetch_result(self, notebook, snippet, rows, start_over):
    db = self._get_db(snippet)
      
    handle = self._get_handle(snippet)
    
    try:
      results = db.fetch(handle, start_over=start_over, rows=rows)
    except Exception, e:
      message = force_unicode(str(e))
      if 'Invalid query handle' in message or 'Invalid OperationHandle' in message:
        raise QueryExpired(e)
      else:
        raise e
    
    # No escaping...
    return {
        'has_more': results.has_more,
        'data': list(results.rows()),
        'meta': [{
          'name': column.name,
          'type': column.type,
          'comment': column.comment
        } for column in results.data_table.cols()]
    }

  def fetch_result_metadata(self):
    pass 

  def cancel(self, notebook, snippet):
    db = self._get_db(snippet)
      
    handle = self._get_handle(snippet)
    db.cancel_operation(handle)
    return {'status': 'canceled'}    

  def get_log(self, snippet):
    db = self._get_db(snippet)
      
    handle = self._get_handle(snippet)    
    return db.get_log(handle)
  
  def _progress(self, snippet, logs):
    if snippet['type'] == 'hive':
      match = re.search('Total jobs = (\d+)', logs, re.MULTILINE)
      total = (int(match.group(1)) if match else 1) * 2
      
      started = logs.count('Starting Job')
      ended = logs.count('Ended Job')
      
      return int((started + ended) * 100 / total)
    elif snippet['type'] == 'impala':
      match = re.search('(\d+)% Complete', logs, re.MULTILINE)
      return int(match.group(1)) if match else 0
    else:
      return 50


class SparkApi():  # Pig, DBquery, Phoenix... 
  
  def __init__(self, user):
    self.user = user
  
  def create_session(self, lang='scala'):
    api = get_spark_api(self.user)
    return {
        'type': lang,
        'id': api.create_session(lang=lang)
    } 
  
  def execute(self, notebook, snippet):    
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)
    
    try:
      return {'id': api.submit_statement(session['id'], snippet['statement']).split('cells/')[1]}
    except Exception, e:
      message = force_unicode(str(e))
      if 'session not found' in message:
        raise SessionExpired(e)
      else:
        raise e

  def check_status(self, notebook, snippet):
    try:
      return {'status': 'available'}
    except Exception, e:
      message = force_unicode(str(e))
      if 'session not found' in message:
        raise SessionExpired(e)
      else:
        raise e

  def fetch_result(self, notebook, snippet, rows, start_over):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)
    cell = snippet['result']['handle']['id']  
    

    try:
      data = api.fetch_data(session['id'], cell)
    except Exception, e:
      message = force_unicode(str(e))
      if 'session not found' in message:
        raise SessionExpired(e)
      else:
        raise e
      
    return {
        'data': [data['output']] if start_over else [], # start_over not supported
        'meta': [{'name': 'Header', 'type': 'String', 'comment': ''}]
    }

  def cancel(self, notebook, snippet):
    pass

  def get_log(self, snippet):
    return 'Not available'
  
  def _progress(self, snippet, logs):  
    return 50
