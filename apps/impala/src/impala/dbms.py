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

from desktop.lib.i18n import smart_str

from beeswax.design import hql_query


LOG = logging.getLogger(__name__)


class ImpalaDbms():

  def get_histogram(self, database, table, column, nested=None):
    """
    Returns the results of an Impala SELECT histogram() FROM query for a given column or nested type.

    Assumes that the column/nested type is scalar.
    """
    results = []

    hql = self.get_histogram_query(database, table, column, nested)
    query = hql_query(hql)
    handle = self.execute_and_wait(query, timeout_sec=5.0)

    if handle:
      result = self.fetch(handle)
      try:
        histogram = list(result.rows())[0][0]  # actual histogram results is in first-and-only result row
        unique_values = set(histogram.split(', '))
        results = list(unique_values)
      except IndexError, e:
        LOG.warn('Failed to get histogram results, result set has unexpected format: %s' % smart_str(e))
      finally:
        self.close(handle)

    return results

  @classmethod
  def get_nested_select(cls, database, table, column, nested=None):
    """
    Given a column or nested type, return the corresponding SELECT and FROM clauses in Impala's nested-type syntax
    """
    select_tokens = [column]
    from_tokens = [database, table]

    if nested:
      nested_tokens = nested.strip('/').split('/')
      while nested_tokens:
        token = nested_tokens.pop(0)
        if token not in ['key', 'value', 'item']:
          select_tokens.append(token)
        else:
          # if we encounter a reserved keyword, move current select_tokens to from_tokens and reset the select_tokens
          from_tokens.extend(select_tokens)
          select_tokens = []
          # if reserved keyword is the last token, make it the only select_token, otherwise we ignore and continue
          if not nested_tokens:
            select_tokens = [token]

    select_clause = '.'.join(select_tokens)
    from_clause = '.'.join('`%s`' % token for token in from_tokens)
    return select_clause, from_clause


  @classmethod
  def get_histogram_query(cls, database, table, column, nested=None):
    select_clause, from_clause = cls.get_nested_select(database, table, column, nested)
    return 'SELECT histogram(%s) FROM %s' % (select_clause, from_clause)
        