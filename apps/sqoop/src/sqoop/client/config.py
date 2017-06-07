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

from desktop.lib.python_util import force_dict_to_strings


class Config(object):

  def __init__(self, id, name, type, inputs=[], **kwargs):
    self.id = id
    self.name = name
    self.type = type
    self.inputs = inputs

  @staticmethod
  def from_dict(config_dict):
    config_dict['inputs'] = [Input.from_dict(input_dict) for input_dict in config_dict.setdefault('inputs', [])]
    return Config(**force_dict_to_strings(config_dict))

  def to_dict(self):
    return {
      'id': self.id,
      'type': self.type,
      'name': self.name,
      'inputs': [input.to_dict() for input in self.inputs]
    }


class Input(object):

  def __init__(self, id, type, name, value=None, values=None, sensitive=False, size=-1, **kwargs):
    self.id = id
    self.type = type
    self.name = name
    # can be empty for config objects
    self.value = value
    # Not sure why we have values even?
    self.values = values
    self.sensitive = sensitive
    self.size = size

  @staticmethod
  def from_dict(input_dict):
    if 'values' in input_dict and isinstance(input_dict['values'], basestring):
      input_dict['values'] = input_dict['values'].split(',')
    return Input(**force_dict_to_strings(input_dict))

  def to_dict(self):
    d = {
      'id': self.id,
      'type': self.type,
      'name': self.name,
      'sensitive': self.sensitive,
      'size': self.size,
    }
    if self.value:
      d['value'] = self.value
    if self.values:
      d['values'] = ','.join(self.values)
    return d
