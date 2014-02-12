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

import logging

from nose.tools import assert_equal, assert_true

from liboozie.submittion import Submission
from oozie.tests import OozieMockBase


LOG = logging.getLogger(__name__)


class MockFs(object):
  def __init__(self, logical_name=None):

    self.fs_defaultfs = 'hdfs://curacao:8020'
    if logical_name:
      self.logical_name = logical_name
    else:
      self.logical_name = ''


class MockJt(object):
  def __init__(self, logical_name=None):

    if logical_name:
      self.logical_name = logical_name
    else:
      self.logical_name = ''


class TestSubmission(OozieMockBase):

  def test_get_properties(self):
    submission = Submission(self.user, fs=MockFs())

    assert_equal({}, submission.properties)

    submission._update_properties('curacao:8032', '/deployment_dir')

    assert_equal({
        'jobTracker': 'curacao:8032',
        'nameNode': 'hdfs://curacao:8020'
      }, submission.properties)

  def test_get_logical_properties(self):
    submission = Submission(self.user, fs=MockFs(logical_name='fsname'), jt=MockJt(logical_name='jtname'))

    assert_equal({}, submission.properties)

    submission._update_properties('curacao:8032', '/deployment_dir')

    assert_equal({
        'jobTracker': 'jtname',
        'nameNode': 'fsname'
      }, submission.properties)
