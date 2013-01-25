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

from nose.tools import assert_equal
from oozie.tests import MockOozieApi

from liboozie.types import WorkflowAction, Coordinator


LOG = logging.getLogger(__name__)


def test_valid_external_id():
  assert_equal('job_201208072118_0044', WorkflowAction(MockOozieApi.JSON_WORKFLOW_LIST[0]).externalId)
  assert_equal(None, WorkflowAction(MockOozieApi.JSON_WORKFLOW_LIST[1]).externalId)
  assert_equal(None, WorkflowAction(MockOozieApi.JSON_WORKFLOW_LIST[2]).externalId)
  assert_equal(None, WorkflowAction(MockOozieApi.JSON_WORKFLOW_LIST[3]).externalId)


def aggregate_coordinator_instances():
  dates = ['1', '2', '3', '6', '7', '8', '10', '12', '15', '16', '20', '23', '30', '40']
  assert_equal(['1-3', '6-8', '10-10', '12-12', '15-16', '20-20', '23-23', '30-30', '40-40'], Coordinator.aggreate(dates))
