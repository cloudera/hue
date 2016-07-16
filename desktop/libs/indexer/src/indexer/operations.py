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
from indexer.argument import TextArgument, CheckboxArgument, MappingArgument

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
      TextArgument("splitChar")
    ],
    output_type="custom_fields"
  ),
  Operator(
    name="grok",
    args=[
      TextArgument("regexp")
    ],
    output_type="custom_fields"
  ),
  Operator(
    name="convert_date",
    args=[
      TextArgument("format")
    ],
    output_type="inplace"
  ),
  Operator(
    name="extract_uri_components",
    args=[
      CheckboxArgument("authority"),
      CheckboxArgument("fragment"),
      CheckboxArgument("host"),
      CheckboxArgument("path"),
      CheckboxArgument("port"),
      CheckboxArgument("query"),
      CheckboxArgument("scheme"),
      CheckboxArgument("scheme_specific_path"),
      CheckboxArgument("user_info")
    ],
    output_type="checkbox_fields"
  ),
  Operator(
    name="geo_ip",
    args=[
      CheckboxArgument("/country/iso_code"),
      CheckboxArgument("/country/names/en"),
      CheckboxArgument("/subdivisions[]/names/en"),
      CheckboxArgument("/subdivisions[]/iso_code"),
      CheckboxArgument("/city/names/en"),
      CheckboxArgument("/postal/code"),
      CheckboxArgument("/location/latitude"),
      CheckboxArgument("/location/longitude"),
    ],
    output_type="checkbox_fields"
  ),
  Operator(
    name="translate",
    args=[
      TextArgument("default"),
      MappingArgument("mapping")
    ],
    output_type="inplace"
  ),
  Operator(
    name="find_replace",
    args=[
      TextArgument("find"),
      TextArgument("replace")
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
