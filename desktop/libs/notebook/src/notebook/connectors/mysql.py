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

import logging

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode

from librdbms.server import dbms

from notebook.connectors.base import Api, QueryError, QueryExpired


LOG = logging.getLogger(__name__)


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Exception, e:
      message = force_unicode(str(e))
      if 'Invalid query handle' in message or 'Invalid OperationHandle' in message:
        raise QueryExpired(e)
      else:
        raise QueryError(message)
  return decorator


class MySqlApi(Api):

  def execute(self, notebook, snippet):
    query_server = dbms.get_query_server_config(server='mysql')
    db = dbms.get(self.user, query_server)
    table = db.execute_statement()
    
    print table
    
    return {
      'result': table
    }

  @query_error_handler
  def check_status(self, notebook, snippet):
    return {'status': 'running'}

  def _fetch_result(self, cursor):
    return {}

  @query_error_handler
  def fetch_result_metadata(self):
    pass

  @query_error_handler
  def cancel(self, notebook, snippet):
    return {'status': 0}

  @query_error_handler
  def get_log(self, notebook, snippet, startFrom=None, size=None):
    return 'No logs'

  def download(self, notebook, snippet, format):
    raise PopupException('Downloading is not supported yet')

  @query_error_handler
  def close_statement(self, snippet):
    return {'status': -1}
