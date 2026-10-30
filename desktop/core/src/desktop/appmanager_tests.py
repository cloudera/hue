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

from importlib.metadata import EntryPoint
from unittest.mock import patch

from desktop.appmanager import _unique_entry_points


def test_unique_entry_points_skips_a_distribution_found_twice():
  # Older importlib.metadata versions return a distribution once per sys.path entry
  duplicated = [
    EntryPoint(name='dashboard', value='dashboard', group='desktop.sdk.application'),
    EntryPoint(name='search', value='search', group='desktop.sdk.application'),
    EntryPoint(name='dashboard', value='dashboard', group='desktop.sdk.application'),
  ]

  with patch('desktop.appmanager.entry_points', return_value=duplicated) as entry_points:
    names = [entry_point.name for entry_point in _unique_entry_points('desktop.sdk.application')]

  entry_points.assert_called_once_with(group='desktop.sdk.application')
  assert names == ['dashboard', 'search']
