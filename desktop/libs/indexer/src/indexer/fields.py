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
  def __init__(self, name, regex):
    self._name = name
    self._regex = regex

  @property
  def name(self):
    return self._name

  @property
  def regex(self):
    return self._regex

  def matches(self, field):
    pattern = re.compile(self._regex)

    return pattern.match(field)

class Field(object):
  def __init__(self, name, field_type):
    self.name = name
    self.field_type = field_type
    self.keep = True
    self.operations = []
    self.required = True

  def to_dict(self):
    return {'name': self.name,
    'type': self.field_type,
    'keep': self.keep,
    'operations': self.operations,
    'required': self.required}

FIELD_TYPES = [
  FieldType('text_en', "^[\\s\\S]{100,}$"),
  FieldType('string', "^[\\s\\S]*$"),
  FieldType('double', "^([+-]?[0-9]+\\.?[0-9]+)?$"),
  FieldType('long', "^(?:[+-]?(?:[0-9]+))?$"),
  FieldType('date', "^([0-9]+-[0-9]+-[0-9]+T[0-9]+:[0-9]+:[0-9]+(\\.[0-9]*)?Z)?$")
]

def guess_field_type_from_samples(samples):
  guesses = [_guess_field_type(sample) for sample in samples]

  return _pick_best_field(guesses)

def _guess_field_type(field_val):
  if field_val == "":
    return None

  for field_type in FIELD_TYPES[::-1]:
    if field_type.matches(field_val):
      return field_type.name

def _pick_best_field(types):
  types = set(types)

  for field in FIELD_TYPES:
    if field.name in types:
      return field.name
  return "string"
