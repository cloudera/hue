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


class Form(object):
  """
  Represents a form in sqoop.

  Example sqoop form dictionary received by server: [
    {
      "id": 1,
      "inputs": [
        {
          "id": 1,
          "name": "connection.jdbcDriver",
          "value": "org.apache.derby.jdbc.EmbeddedDriver",
          "type": "STRING",
          "size": 128,
          "sensitive": false
        },
        {
          "id": 2,
          "name": "connection.connectionString",
          "value": "jdbc%3Aderby%3A%2Ftmp%2Ftest",
          "type": "STRING",
          "size": 128,
          "sensitive": false
        },
        {
          "id": 3,
          "name": "connection.username",
          "type": "STRING",
          "size": 40,
          "sensitive": false
        },
        {
          "id": 4,
          "name": "connection.password",
          "type": "STRING",
          "size": 40,
          "sensitive": true
        },
        {
          "id": 5,
          "name": "connection.jdbcProperties",
          "type": "MAP",
          "value": {
            "key": "value"
          },
          "sensitive": false
        }
      ],
      "name": "connection",
      "type": "CONNECTION"
    }
  ],

  These forms are relatively unstructured. They will always have an ID, name, type, and inputs.
  The number of inputs will vary.
  Their definitions are dynamically generated from  annotations on classes in sqoop.
  The ID identifies the form in the sqoop metadata reprository.
  The ID could vary.
  The ID is unique per type.
  """
  def __init__(self, id, name, type, inputs=[]):
    self.id = id
    self.name = name
    self.type = type
    self.inputs = inputs

  @staticmethod
  def from_dict(form_dict):
    form_dict['inputs'] = [Input.from_dict(input_dict) for input_dict in form_dict.setdefault('inputs', [])]
    return Form(**force_dict_to_strings(form_dict))

  def to_dict(self):
    return {
      'id': self.id,
      'type': self.type,
      'name': self.name,
      'inputs': [input.to_dict() for input in self.inputs]
    }


class Input(object):
  """
  Represents an input in a sqoop form.

  Example sqoop input dictionary received by server: {
    "id": 2,
    "name": "connection.connectionString",
    "values": "jdbc%3Aderby%3A%2Ftmp%2Ftest",
    "type": "STRING",
    "size": 128,
    "sensitive": false
  }

  The ID identifies the input in the sqoop metadata repository.
  The ID could vary.
  The ID is unique per type and per form.
  """
  def __init__(self, id, type, name, value=None, values=None, sensitive=False, size=-1):
    self.id = id
    self.type = type
    self.name = name
    self.value = value
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
      'sensitive': self.sensitive
    }
    if self.value:
      d['value'] = self.value
    if self.values:
      d['values'] = ','.join(self.values)
    if self.size != -1:
      d['size'] = self.size
    return d
