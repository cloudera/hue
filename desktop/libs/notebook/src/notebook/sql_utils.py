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
import hashlib
import os
import re
import StringIO

from desktop.lib.i18n import smart_str

# Note: Might be replaceable by sqlparse.split
def get_statements(hql_query):
  hql_query = strip_trailing_semicolon(hql_query)
  hql_query_sio = StringIO.StringIO(hql_query)

  statements = []
  for (start_row, start_col), (end_row, end_col), statement in split_statements(hql_query_sio.read()):
    statements.append({
      'start': {
        'row': start_row,
        'column': start_col
      },
      'end': {
        'row': end_row,
        'column': end_col
      },
      'statement': strip_trailing_semicolon(statement.rstrip())
    })
  return statements

def get_current_statement(snippet):
  # Multiquery, if not first statement or arrived to the last query
  should_close = False
  handle = snippet['result'].get('handle', {})
  statement_id = handle.get('statement_id', 0)
  statements_count = handle.get('statements_count', 1)

  statements = get_statements(snippet['statement'])

  statement_id = min(statement_id, len(statements) - 1) # In case of removal of statements
  previous_statement_hash = compute_statement_hash(statements[statement_id]['statement'])
  non_edited_statement = previous_statement_hash == handle.get('previous_statement_hash') or not handle.get('previous_statement_hash')

  if handle.get('has_more_statements'):
    should_close = True
    if non_edited_statement:
      statement_id += 1
  else:
    if non_edited_statement:
      statement_id = 0

  if statements_count != len(statements):
    statement_id = min(statement_id, len(statements) - 1)

  resp = {
    'statement_id': statement_id,
    'has_more_statements': statement_id < len(statements) - 1,
    'statements_count': len(statements),
    'previous_statement_hash': compute_statement_hash(statements[statement_id]['statement'])
  }

  resp.update(statements[statement_id])
  return should_close, resp


def compute_statement_hash(statement):
  return hashlib.sha224(smart_str(statement)).hexdigest()

def split_statements(hql):
  """
  Split statements at semicolons ignoring the ones inside quotes and comments.
  The comment symbols that come inside quotes should be ignored.
  """
  statements = []
  current = ''
  prev = ''
  between_quotes = None
  is_comment = None
  start_row = 0
  start_col = 0
  end_row = 0
  end_col = len(hql) - 1

  if hql.find(';') in (-1, len(hql) - 1):
    return [((start_row, start_col), (end_row, end_col), hql)]

  lines = hql.splitlines()

  for row, line in enumerate(lines):
    end_col = 0
    end_row = row

    if start_row == row and line.strip() == '':  # ignore leading whitespace rows
      start_row += 1
    elif current.strip() == '':  # reset start_row
      start_row = row
      start_col = 0

    for col, c in enumerate(line):
      current += c

      if c in ('"', "'") and prev != '\\' and is_comment is None:
        if between_quotes == c:
          between_quotes = None
        elif between_quotes is None:
          between_quotes = c
      elif c == '-' and prev == '-' and between_quotes is None and is_comment is None:
        is_comment = True
      elif c == ';':
        if between_quotes is None and is_comment is None:
          current = current.strip()
          # Strip off the trailing semicolon
          current = current[:-1]
          if len(current) > 1:
            statements.append(((start_row, start_col), (row, col + 1), current))
            start_col = col + 1
          current = ''
      # This character holds no significance if it was escaped within a string
      if prev == '\\' and between_quotes is not None:
        c = ''
      prev = c
      end_col = col

    is_comment = None
    prev = os.linesep

    if current != '':
      current += os.linesep

  if current and current != ';':
    current = current.strip()
    statements.append(((start_row, start_col), (end_row, end_col+1), current))

  return statements

_SEMICOLON_WHITESPACE = re.compile(";\s*$")

def strip_trailing_semicolon(query):
  """As a convenience, we remove trailing semicolons from queries."""
  s = _SEMICOLON_WHITESPACE.split(query, 2)
  if len(s) > 1:
    assert len(s) == 2
    assert s[1] == ''
  return s[0]