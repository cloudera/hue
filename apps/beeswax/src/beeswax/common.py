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
from __future__ import print_function

import re
import time
import numbers

from django import forms

from beeswax.models import Compute, Namespace

HIVE_IDENTIFER_REGEX = re.compile(r"(^[a-zA-Z0-9]\w*\.)?[a-zA-Z0-9]\w*$")

DL_FORMATS = ['csv', 'xls']

SELECTION_SOURCE = ['', 'table', 'constant',]

AGGREGATIONS = ['', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX']

JOIN_TYPES = ['', 'LEFT OUTER JOIN', 'RIGHT OUTER JOIN', 'FULL OUTER JOIN', 'JOIN']

SORT_OPTIONS = ['', 'ascending', 'descending']

RELATION_OPS_UNARY = ['IS NULL', 'IS NOT NULL', 'NOT']

RELATION_OPS = ['=', '<>', '<', '<=', '>', '>='] + RELATION_OPS_UNARY

COMPUTE_TYPES = ['hive-compute', 'impala-compute', 'trino-compute']

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
    print('%s elapsed time: %0.3f ms' % (fn.__name__, (time2 - time1) * 1000.0))
    return ret
  return decorator


def to_choices(x):
  """
  Maps [a, b, c] to [(a,a), (b,b), (c,c)].
  Useful for making ChoiceField's.
  """
  return [(y, y) for y in x]


def apply_natural_sort(collection, key=None):
  """
  Applies a natural sort (http://rosettacode.org/wiki/Natural_sorting) to a list or dictionary
  Dictionary types require a sort key to be specified
  """
  def to_digit(i):
    return int(i) if i.isdigit() else i

  def tokenize_and_convert(item, key=None):
    if key:
      item = item[key]
    return [to_digit(c) for c in re.split('([0-9]+)', item)]

  return sorted(collection, key=lambda i: tokenize_and_convert(i, key=key))


def is_compute(cluster):
  if not cluster:
    return False
  connector = cluster.get('connector')
  compute = cluster.get('compute')

  def compute_check(x):
    return x and x.get('type') in COMPUTE_TYPES
  return compute_check(cluster) or compute_check(connector) or compute_check(compute)


'''
find_compute attempts to find a compute based on the provided criteria.
Following is the priority order
1. A full/partial compute object available in cluster
2. Lookup namespace based on namespace_id and return the first compute
   filtered by user-access. Needs valid user and namespace_id
3. Lookup namespace based on dialect from cluster or prpvided dialect
   and return the first compute filtered by user-access. Needs valid user
'''


def find_compute(cluster=None, user=None, dialect=None, namespace_id=None):
  if cluster:
    # If we find a full/partial cluster object, we will attempt to load a compute
    connector = cluster.get('connector')
    compute = cluster.get('compute')

    def compute_check(x):
      return x and x.get('type') in COMPUTE_TYPES

    # Pick the most probable compute object
    selected_compute = (cluster if compute_check(cluster)
                        else compute if compute_check(compute)
                        else connector if compute_check(connector) else None)

    # If found, we will attempt to reload it, first by id then by name
    if selected_compute:
      if selected_compute.get('id') and isinstance(selected_compute['id'], numbers.Integral):
        c = Compute.objects.filter(id=selected_compute['id']).first()
        if c:
          return c.to_dict()

      if selected_compute.get('name'):
        c = Compute.objects.filter(name=selected_compute['name']).first()
        if c:
          return c.to_dict()

      # If we could not load by id or name, then we want to pick a default compute based on dialect
      dialect = selected_compute['dialect'] if selected_compute.get('dialect') else dialect
      if not dialect and cluster.get('type'):
        t = cluster['type']
        dialect = 'hive' if t.startswith('hive') else\
          'impala' if t.startswith('impala') else\
            'trino' if t.startswith('trino') else None

  # We will attempt to find a default compute based on other criteria
  ns = None
  if namespace_id and isinstance(namespace_id, numbers.Integral):
    ns = Namespace.objects.filter(id=namespace_id).first()

  if not ns and dialect:
    ns = Namespace.objects.filter(dialect=dialect).first()

  if ns and user:
    computes = ns.get_computes(user) if ns else None
    if computes:
      return computes[0]


class HiveIdentifierField(forms.RegexField):
  """
  Corresponds to 'Identifier' in Hive.g (Hive's grammar)
  """
  def __init__(self, *args, **kwargs):
    kwargs['regex'] = HIVE_IDENTIFER_REGEX
    super(HiveIdentifierField, self).__init__(*args, **kwargs)
