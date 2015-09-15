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
import re
import sys

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode
from django.utils.translation import ugettext as _

from notebook.connectors.base import Api, QueryError


LOG = logging.getLogger(__name__)

try:
  import jaydebeapi
except ImportError, e:
  LOG.exception('Failed to import jaydebeapi')


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Exception, e:
      message = force_unicode(str(e))
      if 'Class com.mysql.jdbc.Driver not found' in message:
        raise QueryError(_('%s: did you export CLASSPATH=$CLASSPATH:/usr/share/java/mysql.jar?') % message)
      else:
        raise QueryError(message)
  return decorator


class JDBCApi(Api):

  # TODO
  # async with queuing system
  # impersonation / prompting for username/password
  @query_error_handler
  def execute(self, notebook, snippet):
    if 'jaydebeapi' not in sys.modules:
      raise Exception('Required jaydebeapi module is not imported.')

    user = 'root'
    password = 'root'
    
    host = 'localhost'
    port = 3306
    database = 'test'
    
    autocommit = True
    jclassname = "com.mysql.jdbc.Driver"
    url = "jdbc:mysql://{host}:{port}/{database}".format(host=host, port=port, database=database)
    driver_args = [url, user, password]
    jars = None
    libs = None

    db = jaydebeapi.connect(jclassname, driver_args, jars=jars, libs=libs)
    db.jconn.setAutoCommit(autocommit)
    
    curs = db.cursor()
    curs.execute(snippet['statement'])

    data = curs.fetchmany(100)
    description = curs.description
    
    curs.close()
    db.close()
    
    return {
      'sync': True,
      'result': {
        'has_more': False,
        'data': list(data),
        'meta': [{
          'name': column[0],
          'type': 'TODO',
          'comment': ''
        } for column in description],
        'type': 'table'
      }
    }

  @query_error_handler
  def check_status(self, notebook, snippet):
    return {'status': 'available'}

  def _fetch_result(self, cursor):
    return {}

  @query_error_handler
  def fetch_result_metadata(self):
    pass

  @query_error_handler
  def cancel(self, notebook, snippet):
    return {'status': 0}

  def download(self, notebook, snippet, format):
    raise PopupException('Downloading is not supported yet')

  def _get_jobs(self, logs):
    return []

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

  @query_error_handler
  def close_statement(self, snippet):
    return {'status': -1}
