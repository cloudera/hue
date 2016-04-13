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


class ContinuationToken(object):
  def __init__(self, page, page_size, **kwargs):
    """ Page starting at 1 """
    self.page = page
    self.page_size = page_size

  @property
  def start(self):
    return (self.page - 1) * self.page_size

  @property
  def end(self):
    return self.page * self.page_size

  @classmethod
  def from_dict(cls, ct_dict):
    ct['page_size'] = ct_dict.get('page-size', 10)
    return ContinuationToken(**ct_dict)

  def to_dict(self):
    return {
      'page': self.page,
      'page-size': self.page_size
    }

  def next(self, li=None):
    if self.end > len(li):
      return None
    return ContinuationToken(self.page + 1, self.page_size)

  def paginate_list(self, li):
    start = self.start
    if start <= len(li):
      end = self.end
      if end > len(li):
        end = len(li)
      return (li[start:end], end - start)
    return ([], 0)
