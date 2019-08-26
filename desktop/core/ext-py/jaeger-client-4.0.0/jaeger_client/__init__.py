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

import sys

# This is because thrift for python doesn't have 'package_prefix'.
# The thrift compiled libraries refer to each other relative to their subdir.
import jaeger_client.thrift_gen as modpath
sys.path.append(modpath.__path__[0])

__version__ = '4.0.0'

from .tracer import Tracer  # noqa
from .config import Config  # noqa
from .span import Span  # noqa
from .span_context import SpanContext  # noqa
from .sampler import ConstSampler  # noqa
from .sampler import ProbabilisticSampler  # noqa
from .sampler import RateLimitingSampler  # noqa
from .sampler import RemoteControlledSampler  # noqa
