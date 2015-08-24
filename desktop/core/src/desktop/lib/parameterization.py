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

from string import Template


LOG = logging.getLogger(__name__)


def recursive_walk(function, data):
  """
  Recursively processes dicts, lists and tuples, returning a copy
  with function applied to all leaf values.  We do not recurse
  into dictionary keys.

  NOTE: It's possible to recurse into any objects with __dict__.  We don't
  currently, but for recursing into Thrift, etc., we could.  copy.deepcopy()
  recurses into most pickleable objects, and that would be a reasonable
  pattern to follow.
  """
  # Recurse into lists.
  if isinstance(data, list):
    return list(recursive_walk(function, val) for val in data)

  # Recurse into dicts:
  if isinstance(data, dict):
    return dict( (key, recursive_walk(function, val)) for key, val in data.iteritems() )

  return function(data)

def find_variables(data, include_named=True):
  """
  Finds all substitutable variables.

  This uses Template.pattern, which is arguably
  an implementation detail of string.Template.
  """
  found = set()
  def f(val):
    if not isinstance(val, basestring):
      return
    for match in Template.pattern.finditer(val):
      name = (include_named and match.group('named')) or match.group('braced')
      if name is not None:
        found.add(name)

  recursive_walk(f, data)
  return found

def substitute_variables(input_data, substitutions):
  """
  Replaces variables with values from substitutions.
  """
  def f(value):
    if not isinstance(value, basestring):
      return value

    new_value = Template(value).safe_substitute(substitutions)
    if new_value != value:
      LOG.debug("Substituted %s -> %s" % (repr(value), repr(new_value)))
    return new_value

  return recursive_walk(f, input_data)


def find_parameters(obj, fields=None):
  """Find parameters in the given fields"""
  if fields is None:
    fields = [ k for k in obj.__dict__.keys() if not k.startswith('_') ]

  params = [ ]
  for field in fields:
    data = getattr(obj, field)
    if isinstance(data, basestring):
      for match in Template.pattern.finditer(data):
        name = match.group('named') or match.group('braced')
        if name is not None:
          params.append(name)
  return params


def bind_parameters(obj, substitutions, fields=None):
  """Bind the parameters to the given fields, changing their values."""
  if fields is None:
    fields = [ k for k in obj.__dict__.keys() if not k.startswith('_') ]

  for field in fields:
    data = getattr(obj, field)
    if isinstance(data, basestring):
      new_data = Template(data).safe_substitute(substitutions)
      if new_data != data:
        LOG.debug("Parameterized %s -> %s" % (repr(data), repr(new_data)))
        setattr(obj, field, new_data)
