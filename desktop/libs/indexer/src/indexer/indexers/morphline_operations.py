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

from django.utils.translation import ugettext as _

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

  def _get_default_output_fields(self):
    return []

  def to_dict(self):
    return {
      "name": self._name,
      "args": [arg.to_dict() for arg in self._args],
      "outputType": self._output_type
    }

  def get_default_operation(self):
    return {
      "type": self._name,
      "settings": dict([arg.get_default_arg_pair() for arg in self._args]),
      "fields": self._get_default_output_fields()
    }

OPERATORS = [
  Operator(
    name="split",
    args=[
      TextArgument("splitChar", _("Split Chararacter"))
    ],
    output_type="custom_fields"
  ),
  Operator(
    name="grok",
    args=[
      TextArgument("regexp", _("Regular Expression"))
    ],
    output_type="custom_fields"
  ),
  Operator(
    name="convert_date",
    args=[
      TextArgument("format", _("Date Format (eg: yyyy/MM/dd)"))
    ],
    output_type="inplace"
  ),
  Operator(
    name="extract_uri_components",
    args=[
      CheckboxArgument("authority", _("Authority")),
      CheckboxArgument("fragment", _("Fragment")),
      CheckboxArgument("host", _("Host")),
      CheckboxArgument("path", _("Path")),
      CheckboxArgument("port", _("Port")),
      CheckboxArgument("query", _("Query")),
      CheckboxArgument("scheme", _("Scheme")),
      CheckboxArgument("scheme_specific_path", _("Scheme Specific Path")),
      CheckboxArgument("user_info", _("User Info"))
    ],
    output_type="checkbox_fields"
  ),
  Operator(
    name="geo_ip",
    args=[
      CheckboxArgument("/country/iso_code", _("ISO Code")),
      CheckboxArgument("/country/names/en", _("Country Name")),
      CheckboxArgument("/subdivisions[]/names/en", _("Subdivisions Names")),
      CheckboxArgument("/subdivisions[]/iso_code", _("Subdivisons ISO Code")),
      CheckboxArgument("/city/names/en", _("City Name")),
      CheckboxArgument("/postal/code", _("Postal Code")),
      CheckboxArgument("/location/latitude", _("Latitude")),
      CheckboxArgument("/location/longitude", _("Longitude")),
    ],
    output_type="checkbox_fields"
  ),
  Operator(
    name="translate",
    args=[
      TextArgument("default", "Default Value (if no match found)"),
      MappingArgument("mapping", _("Mapping"))
    ],
    output_type="inplace"
  ),
  Operator(
    name="find_replace",
    args=[
      TextArgument("find", _("Find")),
      TextArgument("replace", _("Replace"))
    ],
    output_type="inplace"
  ),
]

def get_operator(operation_name):
  return [operation for operation in OPERATORS if operation.name == operation_name][0]

def get_checked_args(operation):
  operation_args = get_operator(operation["type"]).args

  kept_args = [arg for arg in operation_args if operation['settings'][arg.name]]

  return kept_args
