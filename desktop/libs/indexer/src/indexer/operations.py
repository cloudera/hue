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

class Argument():
  def __init__(self, type_, name):
    self._name = name
    self._type = type_

  @property
  def name(self):
    return self._name

  @property
  def type(self):
    return self._type

  def to_dict(self):
    return {"name": self._name, "type": self._type}

class Operator():
  def __init__(self, name, args, output_type):
    self._name = name
    self._args = args
    self._output_type = output_type

  @property
  def name(self):
    return self._name

  @property
  def args(self):
    return self._args

  def to_dict(self):
    return {
      "name": self._name,
      "args": [arg.to_dict() for arg in self._args],
      "outputType": self._output_type
    }

OPERATORS = [
  Operator(
    name="split",
    args=[
      Argument("text", "splitChar")
    ],
    output_type="custom_fields"
  ),
  Operator(
    name="grok",
    args=[
      Argument("text", "regexp")
    ],
    output_type="custom_fields"
  ),
  Operator(
    name="convert_date",
    args=[
      Argument("text", "format")
    ],
    output_type="inplace"
  ),
  Operator(
    name="extract_uri_components",
    args=[
      Argument("checkbox", "authority"),
      Argument("checkbox", "fragment"),
      Argument("checkbox", "host"),
      Argument("checkbox", "path"),
      Argument("checkbox", "port"),
      Argument("checkbox", "query"),
      Argument("checkbox", "scheme"),
      Argument("checkbox", "scheme_specific_path"),
      Argument("checkbox", "user_info")
    ],
    output_type="checkbox_fields"
  ),
  Operator(
    name="geo_ip",
    args=[
      Argument("checkbox", "/country/iso_code"),
      Argument("checkbox", "/country/names/en"),
      Argument("checkbox", "/subdivisions[]/names/en"),
      Argument("checkbox", "/subdivisions[]/iso_code"),
      Argument("checkbox", "/city/names/en"),
      Argument("checkbox", "/postal/code"),
      Argument("checkbox", "/location/latitude"),
      Argument("checkbox", "/location/longitude"),
    ],
    output_type="checkbox_fields"
  ),
  Operator(
    name="translate",
    args=[
      Argument("text", "default"),
      Argument("mapping", "mapping")
    ],
    output_type="inplace"
  ),
  Operator(
    name="find_replace",
    args=[
      Argument("text", "find"),
      Argument("text", "replace")
    ],
    output_type="inplace"
  ),
]

def _get_operator(operation_name):
  return [operation for operation in OPERATORS if operation.name == operation_name][0]

def get_checked_args(operation):
  operation_args = _get_operator(operation["type"]).args

  kept_args = [arg for arg in operation_args if operation['settings'][arg.name]]

  return kept_args
