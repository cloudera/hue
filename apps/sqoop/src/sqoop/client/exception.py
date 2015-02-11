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

from config import Config


class SqoopException(Exception):
  def __init__(self, errors):
    self.errors = errors

  @classmethod
  def from_dicts(cls, error_dicts):
    return SqoopException([force_dict_to_strings(d) for d in error_dicts])

  def to_dict(self):
    return {
      'errors': self.errors
    }

  def __str__(self):
    return 'Errors: %s\n' % (self.errors)
