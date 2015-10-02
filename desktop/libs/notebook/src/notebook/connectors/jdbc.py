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

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode
from librdbms.jdbc import Jdbc

from notebook.connectors.base import Api, QueryError


LOG = logging.getLogger(__name__)


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Exception, e:
      message = force_unicode(str(e))
      if 'error occurred while trying to connect to the Java server' in message:
        raise QueryError(_('%s: is the DB Proxy server running?') % message)
      else:
        raise QueryError(message)
  return decorator


class JdbcApi(Api):

  @query_error_handler
  def execute(self, notebook, snippet):

    db = Jdbc(self.options['driver'], self.options['url'], self.options['user'], self.options['password'])

    try:
      db.connect()

      curs = db.cursor()

      try:
        curs.execute(snippet['statement'])

        data = curs.fetchmany(100)
        description = curs.description
      finally:
        curs.close()
    finally:
      db.close()

    return {
      'sync': True,
      'has_result_set': True,
      'result': {
        'has_more': False,
        'data': data,
        'meta': [{
          'name': col[0],
          'type': col[1],
          'comment': ''
        } for col in description],
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

  def progress(self, snippet, logs):
    return 50

  def get_jobs(self, logs):
    return []

  @query_error_handler
  def close_statement(self, snippet):
    return {'status': -1}
