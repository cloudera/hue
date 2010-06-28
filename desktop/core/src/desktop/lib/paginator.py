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

"""
Very similar to the Django Paginator class, but easier to work with
when you don't have the full object list.
"""

from django.db.models import query
import django.core.paginator

class Paginator(django.core.paginator.Paginator):
  """
  Override certain methods of the Django Paginator to allow a partial object list.
  Does not support orphans.
  """
  def __init__(self, object_list, per_page, total=None, allow_empty_first_page=True):
    """
    Accepts a partial ``object_list``, for the purpose of offset and count calculation.

    The ``object_list`` is partial if and only if ``total`` is given. In that case,
    the list is the data for the *next* call to ``page()``.

    If the ``object_list`` is the full list, ``total`` must be None.
    """
    super(Paginator, self).__init__(object_list, per_page, 0, allow_empty_first_page)

    if total is None:
      self.object_list = object_list
    else:
      self.object_list = None
      self._partial_list = object_list
      # We compute the list length again because it could have changed,
      # which is solved by evaluating the QuerySet with len().
      if isinstance(object_list, query.QuerySet):
        total = max(total, len(object_list))
      # Override parent's private member _count
      self._count = total

  def validate_number(self, number):
    if self.object_list is None:
      return number
    return super(Paginator, self).validate_number(number)

  def page(self, number):
    if self.object_list is None:
      # Use a partial list if there is one.
      # Make sure the length of the list agrees with the Page range.
      if self._partial_list is not None:
        res = Page(None, number, self)  # Set the object_list later; None for now
        n_objs = res.end_index() - res.start_index() + 1
        res.object_list = self._partial_list[:n_objs]
        self._partial_list = None       # The _partial_list is single-use
        return res
      # No data. Just a list of None's
      return Page((None,) * self.per_page, number, self)
    # Wrap that parent page in our Page class
    pg = super(Paginator, self).page(number)          # This is a Django Page
    return Page(pg.object_list, pg.number, pg.paginator)


class Page(django.core.paginator.Page):
  """
  Similar to the Django Page, with extra convenient methods.
  """
  def __init__(self, object_list, number, paginator):
    super(Page, self).__init__(object_list, number, paginator)

  def num_pages(self):
    return self.paginator.num_pages

  def total_count(self):
    return self.paginator.count

  def next_page_number(self):
    if self.has_next():
      return self.number + 1
    return self.number

  def previous_page_number(self):
    if self.has_previous():
      return self.number - 1
    return self.number
