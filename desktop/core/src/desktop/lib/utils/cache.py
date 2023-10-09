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

from collections import OrderedDict

class LRUCache:
  def __init__(self, capacity: int):
    self.cache = OrderedDict()
    self.capacity = capacity

  def get(self, key: str):
    if key not in self.cache:
      return None
    else:
      self.cache.move_to_end(key)
      return self.cache[key]

  def put(self, key: str, value) -> None:
    self.cache[key] = value
    self.cache.move_to_end(key)
    if len(self.cache) > self.capacity:
      self.cache.popitem(last = False)
