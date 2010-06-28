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
Support for parameterizing job designs.

The current incarnation supports $input and $output only.

One possible design for this is rather complicated.
Pretty much every job (including streaming) can be specified
as "hadoop $opts", and then "streaming" could be a template
where $opts = "streaming-jar -map $map -reduce $reduce" and so on.
This requires a template language that can auto-generate
forms (and hence, needs types for each variable).  It might
also need validation rules.  This punts on that right now
and explicitly only supports two variables.

TODO(philip): This also needs methods for simply
indicating which variables need substitution, to
prompt the user only for those.
"""

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

def find_variables(data):
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
      name = match.group('named') or match.group('braced')
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
