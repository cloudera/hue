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
All Hue metrics should be defined in the APP/metrics.py file so they are discoverable.
"""

import functools
import pyformance


class MetricsRegistry(object):
  def __init__(self, registry=None):
    if registry is None:
      registry = pyformance.global_registry()
    self._registry = registry
    self._schemas = []

  def _register_schema(self, schema):
    self._schemas.append(schema)

  def counter(self, name, **kwargs):
    self._schemas.append(MetricDefinition('counter', name, **kwargs))
    return self._registry.counter(name)

  def histogram(self, name, **kwargs):
    self._schemas.append(MetricDefinition('histogram', name, **kwargs))
    return self._registry.histogram(name)

  def gauge(self, name, gauge=None, default=float('nan'), **kwargs):
    self._schemas.append(MetricDefinition('gauge', name, **kwargs))
    return self._registry.gauge(name, gauge, default)

  def gauge_callback(self, name, callback, default=float('nan'), **kwargs):
    self._schemas.append(MetricDefinition('gauge', name, **kwargs))
    return self._registry.gauge(name, pyformance.meters.CallbackGauge(callback), default)

  def meter(self, name, **kwargs):
    self._schemas.append(MetricDefinition('meter', name, **kwargs))
    return self._registry.meter(name)

  def timer(self, name, **kwargs):
    self._schemas.append(MetricDefinition('timer', name, **kwargs))
    return Timer(self._registry.timer(name))

  def dump_metrics(self):
    return self._registry.dump_metrics()


class MetricDefinition(object):
  def __init__(self, metric_type, name, label,
      description=None,
      numerator=None,
      denominator=None,
      context=None):
    self.metric_type = metric_type
    self.name = name
    self.label = label
    self.description = description
    self.numerator = numerator
    self.denominator = denominator
    self.context = context


class Timer(object):
  """
  Wrapper around the pyformance Timer object to allow it to be used in an
  annotation.
  """

  def __init__(self, timer):
    self._timer = timer

  def __call__(self, fn, *args, **kwargs):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
      with self._timer.time():
        return fn(*args, **kwargs)

    return wrapper

  def __getattr__(self, *args, **kwargs):
    return getattr(self._timer, *args, **kwargs)


_global_registry = MetricsRegistry()


def global_registry():
  return _global_registry
