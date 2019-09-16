# Copyright (c) 2016 Uber Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

import unittest

from jaeger_client import ConstSampler, Tracer
from jaeger_client.reporter import NullReporter
from opentracing.harness.api_check import APICompatibilityCheckMixin


class APITest(unittest.TestCase, APICompatibilityCheckMixin):

    reporter = NullReporter()
    sampler = ConstSampler(True)
    _tracer = Tracer(
        service_name='test_service_1', reporter=reporter, sampler=sampler)

    def tracer(self):
        return APITest._tracer

    def test_binary_propagation(self):
        # TODO binary codecs are not implemented at the moment
        pass

    def is_parent(self, parent, span):
        return span.parent_id == getattr(parent, 'span_id', None)
