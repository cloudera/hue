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


class Argument(object):
  _type = None
  _default_value = None

  def __init__(self, name, description=None):
    self._name = name
    self._description = _(description if description else name)

  @property
  def name(self):
    return self._name

  @property
  def type(self):
    return self._type

  @property
  def default_value(self):
    return self._default_value

  def to_dict(self):
    return {"name": self._name, "type": self._type, "description": self._description}

  def get_default_arg_pair(self):
    return (self.name, self.default_value)


class TextArgument(Argument):
  _type = "text"
  _default_value = ""


class TextDelimiterArgument(Argument):
  _type = "text-delimiter"
  _default_value = ""

  def __init__(self, name, description=None, max_length=2):
    super(TextDelimiterArgument, self).__init__(name, description=description)
    self.max_length = max_length


class CheckboxArgument(Argument):
  _type = "checkbox"
  _default_value = False


class MappingArgument(Argument):
  _type = "mapping"

  @property
  def default_value(self):
    return []
