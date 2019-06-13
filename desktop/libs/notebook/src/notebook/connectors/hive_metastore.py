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

from django.urls import reverse
from django.utils.translation import ugettext as _


from desktop.lib.exceptions import StructuredException
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode, smart_str
from desktop.lib.rest.http_client import RestException

from notebook.connectors.base import Api, QueryError, QueryExpired, OperationTimeout, OperationNotSupported


LOG = logging.getLogger(__name__)


try:
  from beeswax.api import _autocomplete
  from beeswax.server import dbms
  from beeswax.server.dbms import get_query_server_config, QueryServerException
except ImportError, e:
  LOG.warn('Hive and HiveMetastoreServer interfaces are not enabled: %s' % e)
  hive_settings = None


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except StructuredException, e:
      message = force_unicode(str(e))
      if 'timed out' in message:
        raise OperationTimeout(e)
      else:
        raise QueryError(message)
    except QueryServerException, e:
      message = force_unicode(str(e))
      if 'Invalid query handle' in message or 'Invalid OperationHandle' in message:
        raise QueryExpired(e)
      else:
        raise QueryError(message)
  return decorator


class HiveMetastoreApi(Api):

  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    db = self._get_db(snippet, cluster=self.cluster)

    return _autocomplete(db, database, table, column, nested, query=None, cluster=self.cluster)


  @query_error_handler
  def get_sample_data(self, snippet, database=None, table=None, column=None, async=False, operation=None):
    return []


  def _get_db(self, snippet, async=False, cluster=None):
    return dbms.get(self.user, query_server=get_query_server_config(name='hms', cluster=cluster))
