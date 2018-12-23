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
# limitations under the License.import logging

import re


class FieldType():

  def __init__(self, name, regex, heuristic_regex=None):
    self._name = name
    self._regex = regex
    self._heuristic_regex = heuristic_regex

  @property
  def heuristic_regex(self):
    return self._heuristic_regex if self._heuristic_regex else self.regex

  @property
  def name(self):
    return self._name

  @property
  def regex(self):
    return self._regex

  def heuristic_match(self, field):
    pattern = re.compile(self.heuristic_regex, flags=re.IGNORECASE)

    return pattern.match(field)


class Field(object):

  def __init__(self, name="new_field", field_type_name="string", operations=None, multi_valued=False, unique=False):
    self.name = name
    self.field_type_name = field_type_name
    self.keep = True
    self.operations = operations if operations else []
    self.required = False
    self.unique = unique
    self.multi_valued = multi_valued
    self.show_properties = False

  def to_dict(self):
    return {
      'name': self.name,
      'type': self.field_type_name,
      'unique': self.unique,
      'keep': self.keep,
      'operations': self.operations,
      'required': self.required,
      'multiValued': self.multi_valued,
      'showProperties': self.show_properties,
      'nested': [],
      'level': 0,
      'length': 100,
      'keyType': 'string',
      'isPartition': False,
      'partitionValue': '',
      'comment': '',
      'scale': 0,
      'precision': 10
    }

FIELD_TYPES = [
  FieldType('text_general', "^[\\s\\S]*$", heuristic_regex="^[\\s\\S]{101,}$"),
  FieldType('string', "^[\\s\\S]*$", heuristic_regex="^[\\s\\S]{1,100}$"),
  FieldType('double', "^([+-]?[0-9]+(\.[0-9]+)?(E[+-]?[0-9]+)?)$"),
  FieldType('long', "^(?:[+-]?(?:[0-9]+))$"),
  FieldType('date', "^([0-9]+-[0-9]+-[0-9]+(\s+|T)[0-9]+:[0-9]+:[0-9]+(\.[0-9]*)?Z?)$"),
  FieldType('boolean', "^(true|false|t|f|0|1)$")
]

def get_field_type(type_name):
  return [file_type for file_type in FIELD_TYPES if file_type.name in type_name][0]

def guess_field_type_from_samples(samples):
  guesses = [_guess_field_type(sample) for sample in samples]

  return _pick_best_field(guesses)

def _guess_field_type(field_val):
  if field_val == "":
    return None

  for field_type in FIELD_TYPES[::-1]:
    if field_type.heuristic_match(field_val):
      return field_type.name

def _pick_best_field(types):
  types = set(types)

  for field in FIELD_TYPES:
    if field.name in types:
      return field.name
  return "string"
