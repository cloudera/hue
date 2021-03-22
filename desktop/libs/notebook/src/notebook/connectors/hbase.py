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

from __future__ import absolute_import

import logging
import sys

from django.urls import reverse

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode

from notebook.connectors.base import Api, QueryError

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


try:
  from hbase.api import HbaseApi
except ImportError as e:
  LOG.warning("HBase app is not enabled: %s" % e)


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Exception as e:
      message = force_unicode(str(e))
      raise QueryError(message)
  return decorator


class HBaseApi(Api):

  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None, operation=None):
    db = HbaseApi(self.user)
    cluster_name = database

    response = {}

    try:
      if database is None:
        response['databases'] = [cluster['name'] for cluster in db.getClusters()]
      elif table is None:
        tables_meta = db.getTableList(cluster_name)
        response['tables_meta'] = [_table['name'] for _table in tables_meta if _table['enabled']]
      elif column is None:
        tables_meta = db.get(cluster_name, table)
        response['columns'] = []
      else:
        raise PopupException('Could not find column `%s`.`%s`.`%s`' % (database, table, column))
    except Exception as e:
      LOG.warning('Autocomplete data fetching error: %s' % e)
      response['code'] = 500
      response['error'] = e.message

    return response
