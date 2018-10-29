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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib.i18n import force_unicode
from kafka.kafka_api import get_topics

from notebook.connectors.base import Api, QueryError


LOG = logging.getLogger(__name__)


def query_error_handler(func):
  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Exception, e:
      message = force_unicode(str(e))
      raise QueryError(message)
  return decorator


class KafkaApi(Api):

  @query_error_handler
  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    response = {}

    try:
      if database is None:
        response['databases'] = ['default']
      elif table is None:
        response['tables_meta'] = get_topics()
      else:
        response = {
          u'status': 0,
          u'comment': u'test test test 22',
          u'hdfs_link': u'/filebrowser/view=/user/hive/warehouse/web_logs',
          u'extended_columns': [
            {u'comment': u'', u'type': u'bigint', u'name': u'_version_'},
            {u'comment': u'The app', u'type': u'string', u'name': u'app'},
            {u'comment': u'test test   test 22', u'type': u'smallint', u'name': u'bytes'},
            {u'comment': u'The citi', u'type': u'string', u'name': u'city'},
            {u'comment': u'', u'type': u'string', u'name': u'client_ip'},
            {u'comment': u'', u'type': u'tinyint', u'name': u'code'},
            {u'comment': u'', u'type': u'string', u'name': u'country_code'},
            {u'comment': u'', u'type': u'string', u'name': u'country_code3'},
            {u'comment': u'', u'type': u'string', u'name': u'country_name'},
            {u'comment': u'', u'type': u'string', u'name': u'device_family'},
            {u'comment': u'', u'type': u'string', u'name': u'extension'},
            {u'comment': u'', u'type': u'float', u'name': u'latitude'},
            {u'comment': u'', u'type': u'float', u'name': u'longitude'},
            {u'comment': u'', u'type': u'string', u'name': u'method'},
            {u'comment': u'', u'type': u'string', u'name': u'os_family'},
            {u'comment': u'', u'type': u'string', u'name': u'os_major'},
            {u'comment': u'', u'type': u'string', u'name': u'protocol'},
            {u'comment': u'', u'type': u'string', u'name': u'record'},
            {u'comment': u'', u'type': u'string', u'name': u'referer'},
            {u'comment': u'', u'type': u'bigint', u'name': u'region_code'},
            {u'comment': u'', u'type': u'string', u'name': u'request'},
            {u'comment': u'', u'type': u'string', u'name': u'subapp'},
            {u'comment': u'', u'type': u'string', u'name': u'time'},
            {u'comment': u'', u'type': u'string', u'name': u'url'},
            {u'comment': u'', u'type': u'string', u'name': u'user_agent'},
            {u'comment': u'', u'type': u'string', u'name': u'user_agent_family'},
            {u'comment': u'', u'type': u'string', u'name': u'user_agent_major'},
            {u'comment': u'', u'type': u'string', u'name': u'id'},
            {u'comment': u'', u'type': u'string', u'name': u'date'}
          ],
          u'support_updates': False,
          u'partition_keys': [
            {u'type': u'string', u'name': u'date'}
          ],
          u'columns': [u'_version_', u'app', u'bytes', u'city', u'client_ip', u'code', u'country_code', u'country_code3', u'country_name', u'device_family', u'extension', u'latitude', u'longitude', u'method', u'os_family', u'os_major', u'protocol', u'record', u'referer', u'region_code', u'request', u'subapp', u'time', u'url', u'user_agent', u'user_agent_family', u'user_agent_major', u'id', u'date'],
          u'is_view': False
        }

    except Exception, e:
      LOG.warn('Autocomplete data fetching error: %s' % e)
      response['code'] = 500
      response['error'] = e.message

    return response
