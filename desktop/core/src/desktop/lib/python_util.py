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
# 
# Extra python utils


class CaseInsensitiveDict(dict):
  def __setitem__(self, key, value):
    super(CaseInsensitiveDict, self).__setitem__(key.lower(), value)

  def __getitem__(self, key):
    return super(CaseInsensitiveDict, self).__getitem__(key.lower())

  def __contains__(self, key):
    return super(CaseInsensitiveDict, self).__contains__(key.lower())

  @classmethod
  def from_dict(cls, _dict):
    return CaseInsensitiveDict([(isinstance(key, basestring) and key.lower() or key, _dict[key]) for key in _dict])
