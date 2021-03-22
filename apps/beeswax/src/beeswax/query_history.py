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

from builtins import filter
from builtins import str

import collections
import logging
import json
import sys
import threading
import uuid

from beeswax.design import hql_query
from beeswax.server import dbms
from beeswax.server.dbms import get_query_server_config
from beeswax.management.commands import create_table_query_data

from desktop.lib.exceptions_renderable import raise_popup_exception, PopupException
from desktop.lib import django_mako

from useradmin.models import install_sample_user

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)

QUERY_HISTORY_CACHE_MAX_USER_COUNT = 10
QUERY_HISTORY_CACHE_MAX_LENGTH_PER_USER = 25
HAS_CREATED_TABLE = False


class QueryHistory(object):
  def __init__(self, max_user=10, max_history_per_user=25):
    self.max_user=max_user
    self.max_history_per_user=max_history_per_user
    self.by_user = collections.OrderedDict()
    self.no_user_key = str(uuid.uuid4())
    self.lock = threading.Lock()

  def _remove(self, request_user):
    if request_user in self.by_user:
      del self.by_user[request_user]

  # Data has to be sorted & grouped by
  def _append(self, by_user, data):
    total_history = data + by_user['queries']
    if self.max_history_per_user < len(total_history):
      by_user['queries'] = total_history[:self.max_history_per_user]
    else:
      by_user['queries'] = total_history

    by_user['by_id'] = {}
    by_user['max'] = {'time': 0, 'date': ''}
    for row in by_user['queries']:
      by_user['by_id'][row[0]] = row
      if row[1][-1] > by_user['max']['time']:
        by_user['max']['time'] = row[1][-1]
        by_user['max']['date'] = row[7]

    return total_history

  def _add(self, request_user, filters):
    if len(self.by_user) >= self.max_user:
      # Remove eldest user and all its queries
      self.by_user.popitem(last=False)

    by_id = {'queries': [], 'max': {'time': 0, 'date': ''}, 'by_id': {}, 'filters': filters, 'by_id': {}}
    self.by_user[request_user] = by_id
    return by_id

  def set(self, request_user, data, filters):
    if not request_user:
      request_user = self.no_user_key
    try:
      self.lock.acquire()
      self._remove(request_user)
      by_id = self._add(request_user, filters)
      self._append(by_id, data)
    finally:
      self.lock.release()

  def update(self, by_user, data):

    try:
      self.lock.acquire()
      # Get records not present in current history and append
      # Update records already in query history
      results = _groupby(by_user, data)
      return self._append(by_user, results)
    finally:
      self.lock.release()

  def get_by_id(self, request_user, query_id):
    if not request_user:
      request_user = self.no_user_key

    try:
      self.lock.acquire()
      value = self.by_user.get(request_user)
      if value:
        return value['by_id'].get(query_id)
      else:
        return value
    finally:
      self.lock.release()

  def get_queries(self, request_user, filters):
    if not request_user:
      request_user = self.no_user_key

    try:
      self.lock.acquire()
      by_user = self.by_user.get(request_user)
      if by_user and by_user['filters'] == filters:
        del self.by_user[request_user] # Moving request_user to head of queue
        self.by_user[request_user] = by_user
        return by_user
      return None
    finally:
      self.lock.release()

QUERY_HISTORY = QueryHistory(max_user=QUERY_HISTORY_CACHE_MAX_USER_COUNT, max_history_per_user=QUERY_HISTORY_CACHE_MAX_LENGTH_PER_USER)

# If fresh user get from _get_query_history_latest else get _get_query_history_from. if results set from _get_query_history_from less than limit merge results with cache else call _get_query_history_latest
def get_query_history(request_user=None, start_date=None, start_time=None, query_id=None, status=None, limit=None):
  _init_table()

  filters = {'start_date': start_date, 'start_time': start_time, 'query_id': query_id, 'status': status}
  history = QUERY_HISTORY.get_queries(request_user, filters)
  if history:
    # Get last
    last = history['max']
    data = _get_query_history_from(request_user=request_user,
                                   start_date=last['date'],
                                   start_time=last['time']+1,
                                   query_id=query_id,
                                   status=status,
                                   limit=limit)
    if not limit or len(data['data']) < limit:
      cached = QUERY_HISTORY.update(history, data['data'])
      filter_list = _get_filter_list({'states': status})
      cached = _n_filter(filter_list, cached)[:limit]
      return {'data': cached}

  data = _get_query_history_latest(request_user=request_user, start_date=start_date, start_time=start_time, query_id=query_id, status=status, limit=limit, force_refresh=True)
  QUERY_HISTORY.set(request_user, data['data'], filters)
  return data

# If id in cache return cache else _get_query_history_from
def get_query_by_id(request_user=None, query_id=None):
  _init_table()

  datum = QUERY_HISTORY.get_by_id(request_user, query_id)
  if datum:
    return {'data': [datum]}
  else:
    data = _get_query_history_from(request_user=request_user, query_id=query_id) # force_refresh?
    cached = _groupby({'by_id': {}}, data['data'])
    return {'data': cached}

def _init_table():
  global HAS_CREATED_TABLE
  if not HAS_CREATED_TABLE:
    if create_table_query_data.create_table():
      HAS_CREATED_TABLE = True
  if not HAS_CREATED_TABLE:
    raise PopupException(_('Could not initialize query history table.'))

def _get_query_history_latest(request_user=None, query_id=None, start_date=None, start_time=None, status=None, limit=25, force_refresh=False):
  proposed_query = django_mako.render_to_string("select_table_query_data_latest.mako", {'table': {'name': 'query_data', 'request_user': request_user, 'query_id': query_id, 'start_date': start_date, 'start_time': start_time, 'status': status, 'limit': limit, 'force_refresh': force_refresh}})
  data = _execute_query(proposed_query, limit)
  for row in data['data']:
    if row[1]:
      row[1] = json.loads(row[1])
    if row[5]:
      row[5] = json.loads(row[5])
    if row[8]:
      row[8] = json.loads(row[8])
  return data

def _get_query_history_from(request_user=None, start_date=None, start_time=None, status=None, query_id=None, limit=25):
  proposed_query = django_mako.render_to_string("select_table_query_data_from.mako",
                                                {'table':
                                                 {'name': 'query_data',
                                                  'request_user': request_user,
                                                  'start_date': start_date,
                                                  'start_time': start_time,
                                                  'query_id': query_id,
                                                  'status': status,
                                                  'limit': limit}})
  data = _execute_query(proposed_query, limit)
  for row in data['data']:
    if row[1]:
      row[1] = [row[1]]
    if row[5]:
      row[5] = json.loads(row[5])
    if row[8]:
      row[8] = [row[8]]
  return data

def _execute_query(proposed_query, limit):
  user = install_sample_user()
  query_server = get_query_server_config('beeswax')
  server = dbms.get(user, query_server)
  query = hql_query(proposed_query)
  try:
    handle = server.execute_and_wait(query)
    if not handle:
      LOG.error(_('Error executing %s: Operation timeout.' % query))
      return []
    results = server.fetch(handle, True, limit)
    rows = [row for row in results.rows()]
    data = {
        'data': rows,
        'columns': [column.name for column in results.data_table.cols()]}

    return data
  except Exception as ex:
    raise_popup_exception(_('Error fetching query history.'))
  finally:
    try:
      if server and handle:
        server.close(handle)
    except Exception as ex:
      raise_popup_exception(_('Error fetching query history.'))

def _get_filter_list(filters):
  filter_list = []
  if filters.get("states"):
    filter_list.append(lambda app: _get_status(app) in filters.get("states"))

  return filter_list

def _get_status(row):
  return 'completed' if len(row[1]) >= 2 else 'running'

def _n_filter(filters, tuples):
  for f in filters:
    tuples = list(filter(f, tuples))
  return tuples

def _groupby(by_user, data):
  results = []
  for row in data:
    if not by_user['by_id'].get(row[0]):
      if not isinstance(row[1], list):
        row[1] = [row[1]]
      if not isinstance(row[8], list):
        row[8] = [row[8]]
      by_user['by_id'][row[0]] = row
      results.append(row)
    else:
      item = by_user['by_id'][row[0]]
      if row[8][0] in item[8]: # we have dup
        continue
      if row[1]:
        item[1] += row[1]
      if row[2]:
        item[2] = row[2]
      if row[4]:
        item[4] = row[4]
      if row[5]:
        item[5] = row[5]
      if row[6]:
        item[6] = row[6]
      if row[8]:
        item[8] += row[8]

  results.sort(key=lambda result: result[1][0], reverse=True)
  return results
