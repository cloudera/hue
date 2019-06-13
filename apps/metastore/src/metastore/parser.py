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
Helper for parsing a Hive metastore column type
"""
import re


SIMPLE_SCALAR = '[a-z]+'
DECIMAL_SCALAR = 'decimal\(\d+,\d+\)'
DOUBLE_SCALAR = 'double\(\d+,\d+\)'
VARCHAR_SCALAR = 'varchar\(\d+\)'


def parse_column(name, type_string, comment=None):
  """
  Returns a dictionary of a Hive column's type metadata and
   any complex or nested type info
  """
  type_string = type_string.lower()
  column = {
    'name': name,
    'comment': comment or ''
  }
  simple_type, inner = _parse_type(type_string)
  column['type'] = simple_type

  if inner:
    column.update(_parse_complex(simple_type, inner))
  return column


def is_scalar_type(type_string):
  return not (type_string.startswith('array') or type_string.startswith('map') or type_string.startswith('struct'))


def _parse_type(type_string):
  pattern = re.compile('^(%(simple)s|%(decimal)s|%(double)s|%(varchar)s)(<(.+)>)?$' % {
    'simple': SIMPLE_SCALAR,
    'decimal': DECIMAL_SCALAR,
    'double': DOUBLE_SCALAR,
    'varchar': VARCHAR_SCALAR,
    },
    re.IGNORECASE
  )
  match = re.search(pattern, type_string)
  return match.group(1), match.group(3)


def _parse_complex(simple_type, inner):
  complex_type = {}
  if simple_type == "array":
    complex_type['item'] = _parse_array_item(inner)
  elif simple_type == "map":
    complex_type['key'] = _parse_map_key(inner)
    complex_type['value'] = _parse_map_value(inner)
  elif simple_type == "struct":
    complex_type['fields'] = _parse_struct_fields(inner)
  return complex_type


def _parse_array_item(inner):
  item = {}
  simple_type, inner = _parse_type(inner)
  item['type'] = simple_type
  if inner:
    item.update(_parse_complex(simple_type, inner))
  return item


def _parse_map_key(inner):
  key = {}
  key_type = inner.split(',', 1)[0]
  key['type'] = key_type
  return key


def _parse_map_value(inner):
  value = {}
  value_type = inner.split(',', 1)[1]
  simple_type, inner = _parse_type(value_type)
  value['type'] = simple_type
  if inner:
    value.update(_parse_complex(simple_type, inner))
  return value


def _parse_struct_fields(inner):
  fields = []
  field_tuples = _split_struct_fields(inner)
  for (name, value) in field_tuples:
    field = {}
    field['name'] = name
    simple_type, inner = _parse_type(value)
    field['type'] = simple_type
    if inner:
      field.update(_parse_complex(simple_type, inner))
    fields.append(field)
  return fields


def _split_struct_fields(fields_string):
  fields = []
  remaining = fields_string
  while remaining:
    (fieldname, fieldvalue), remaining = _get_next_struct_field(remaining)
    fields.append((fieldname, fieldvalue))
  return fields


def _get_next_struct_field(fields_string):
  fieldname, rest = fields_string.split(':', 1)
  fieldname = fieldname.strip(',')
  balanced = 0
  for pos, char in enumerate(rest):
    balanced += {'<': 1, '>': -1, '(': 1, ')': -1}.get(char, 0)
    if balanced == 0 and char in ['>', ',']:
      return (fieldname, rest[:pos+1].strip(',')), rest[pos+1:]
  return (fieldname, rest), None
