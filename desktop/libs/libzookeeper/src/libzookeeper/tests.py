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

from nose.tools import assert_equal, assert_true, assert_false

from libzookeeper.conf import ENSEMBLE


class UnitTests():

  def test_get_ensemble(self):
    clear = ENSEMBLE.set_for_testing('zoo:2181')
    try:
      assert_equal('zoo:2181', ENSEMBLE.get())
    finally:
      clear()

    clear = ENSEMBLE.set_for_testing('zoo:2181,zoo2:2181')
    try:
      assert_equal('zoo:2181,zoo2:2181', ENSEMBLE.get())
    finally:
      clear()

    clear = ENSEMBLE.set_for_testing(['zoo:2181', 'zoo2:2181'])
    try:
      assert_equal('zoo:2181,zoo2:2181', ENSEMBLE.get())
    finally:
      clear()

