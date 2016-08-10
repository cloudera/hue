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

"""
Common utils for beeswax.
"""

import re
import time

from django import forms


HIVE_IDENTIFER_REGEX = re.compile("(^[a-zA-Z0-9]\w*\.)?[a-zA-Z0-9]\w*$")

DL_FORMATS = [ 'csv', 'xls' ]

SELECTION_SOURCE = [ '', 'table', 'constant', ]

AGGREGATIONS = [ '', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX' ]

JOIN_TYPES = [ '', 'LEFT OUTER JOIN', 'RIGHT OUTER JOIN', 'FULL OUTER JOIN', 'JOIN' ]

SORT_OPTIONS = [ '', 'ascending', 'descending' ]

RELATION_OPS_UNARY = [ 'IS NULL', 'IS NOT NULL', 'NOT' ]

RELATION_OPS = [ '=', '<>', '<', '<=', '>', '>=' ] + RELATION_OPS_UNARY

TERMINATORS = [
  # (hive representation, description, ascii value)
  (r'\001', r"'^A' (\001)", 1),
  (r'\002', r"'^B' (\002)", 2),
  (r'\003', r"'^C' (\003)", 3),
  (r'\t', r"Tab (\t)", 9),
  (',', "Comma (,)", 44),
  (' ', "Space", 32),
]

def timing(fn):
  def decorator(*args, **kwargs):
    time1 = time.time()
    ret = fn(*args, **kwargs)
    time2 = time.time()
    print '%s elapsed time: %0.3f ms' % (fn.func_name, (time2-time1)*1000.0)
    return ret
  return decorator


def to_choices(x):
  """
  Maps [a, b, c] to [(a,a), (b,b), (c,c)].
  Useful for making ChoiceField's.
  """
  return [ (y, y) for y in x ]


def apply_natural_sort(collection, key=None):
  """
  Applies a natural sort (http://rosettacode.org/wiki/Natural_sorting) to a list or dictionary
  Dictionary types require a sort key to be specified
  """
  to_digit = lambda i: int(i) if i.isdigit() else i

  def tokenize_and_convert(item, key=None):
    if key:
      item = item[key]
    return [to_digit(c) for c in re.split('([0-9]+)', item)]

  return sorted(collection, key=lambda i: tokenize_and_convert(i, key=key))


class HiveIdentifierField(forms.RegexField):
  """
  Corresponds to 'Identifier' in Hive.g (Hive's grammar)
  """
  def __init__(self, *args, **kwargs):
    kwargs['regex'] = HIVE_IDENTIFER_REGEX
    super(HiveIdentifierField, self).__init__(*args, **kwargs)
