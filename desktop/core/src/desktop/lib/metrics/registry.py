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


MAX_LABEL_SUFFIX = ': Max'
MAX_DESCRIPTION_SUFFIX = ': Max. This is computed over the lifetime of the process.'

MIN_LABEL_SUFFIX = ': Min'
MIN_DESCRIPTION_SUFFIX = ': Min. This is computed over the lifetime of the process.'

AVERAGE_LABEL_SUFFIX = ': Average'
AVERAGE_DESCRIPTION_SUFFIX = ': Average. This is computed over the lifetime of the process.'

SAMPLE_COUNT_LABEL_SUFFIX = ': Sample Count'
SAMPLE_COUNT_DESCRIPTION_SUFFIX = ': Sample Count. This is computed over the lifetime of the process.'

SAMPLE_SUM_LABEL_SUFFIX = ': Sample Sum'
SAMPLE_SUM_DESCRIPTION_SUFFIX = ': Sample Sum. This is computed over the lifetime of the process.'

STD_DEV_LABEL_SUFFIX = ': Standard Deviation'
STD_DEV_DESCRIPTION_SUFFIX = ': Standard Deviation. This is computed over the lifetime of the process.'

RATE_1_LABEL_SUFFIX = ': 1-Minute Rate'
RATE_1_DESCRIPTION_SUFFIX = ': 1-Minute moving average rate.'

RATE_5_LABEL_SUFFIX = ': 5-Minute Rate'
RATE_5_DESCRIPTION_SUFFIX = ': 5-Minute Rate'

RATE_15_LABEL_SUFFIX = ': 15-Minute Rate'
RATE_15_DESCRIPTION_SUFFIX = ': 15-Minute Rate'

PERCENTILE_50_LABEL_SUFFIX = ': 50th Percentile'
PERCENTILE_50_DESCRIPTION_SUFFIX = ': 50th Percentile. This is computed over the past hour.'

PERCENTILE_75_LABEL_SUFFIX = ': 75th Percentile'
PERCENTILE_75_DESCRIPTION_SUFFIX = ': 75th Percentile. This is computed over the past hour.'

PERCENTILE_95_LABEL_SUFFIX = ': 95th Percentile'
PERCENTILE_95_DESCRIPTION_SUFFIX = ': 95th Percentile. This is computed over the past hour.'

PERCENTILE_99_LABEL_SUFFIX = ': 99th Percentile'
PERCENTILE_99_DESCRIPTION_SUFFIX = ': 99th Percentile. This is computed over the past hour.'

PERCENTILE_999_LABEL_SUFFIX = ': 999th Percentile'
PERCENTILE_999_DESCRIPTION_SUFFIX = ': 999th Percentile. This is computed over the past hour.'


class MetricsRegistry(object):
  def __init__(self, registry=None):
    if registry is None:
      registry = pyformance.global_registry()
    self._registry = registry
    self._schemas = []

  def _register_schema(self, schema):
    self._schemas.append(schema)

  @property
  def schemas(self):
    return list(self._schemas)

  def counter(self, name, **kwargs):
    self._schemas.append(CounterDefinition(name, **kwargs))
    return self._registry.counter(name)

  def histogram(self, name, **kwargs):
    self._schemas.append(HistogramDefinition(name, **kwargs))
    return self._registry.histogram(name)

  def gauge(self, name, gauge=None, default=float('nan'), **kwargs):
    self._schemas.append(GaugeDefinition(name, **kwargs))
    return self._registry.gauge(name, gauge, default)

  def gauge_callback(self, name, callback, default=float('nan'), **kwargs):
    self._schemas.append(GaugeDefinition(name, **kwargs))
    return self._registry.gauge(name, pyformance.meters.CallbackGauge(callback), default)

  def meter(self, name, **kwargs):
    self._schemas.append(MeterDefinition(name, **kwargs))
    return self._registry.meter(name)

  def timer(self, name, **kwargs):
    self._schemas.append(TimerDefinition(name, **kwargs))
    return Timer(self._registry.timer(name))

  def dump_metrics(self):
    metrics = self._registry.dump_metrics()

    # Filter out min and max if there have been no samples.
    for metric in metrics.itervalues():
      if metric.get('count') == 0:
        if 'min' in metric:
          metric['min'] = 0.0

        if 'max' in metric:
          metric['max'] = 0.0

    return metrics


class MetricDefinition(object):
  _add_key_to_name = False

  def __init__(self, name, label, description, numerator,
      denominator=None,
      weighting_metric_name=None):
    self.name = name
    self.label = label
    self.description = description
    self.numerator = numerator
    self.denominator = denominator
    self.weighting_metric_name = weighting_metric_name

    assert self.name is not None
    assert self.label is not None
    assert self.description is not None
    assert self.numerator is not None


  def to_json(self):
    raise NotImplementedError


  def _make_json(self, key,
      suffix=None,
      label_suffix=None,
      description_suffix=None,
      **kwargs):
    names = ['hue', self.name.replace('.', '_').replace('-', '_')]

    label = self.label
    description = self.description

    if label_suffix is None:
      label_suffix = suffix

    if description_suffix is None:
      description_suffix = suffix

    if label_suffix:
      label += label_suffix

    if description_suffix:
      description += description_suffix

    if self._add_key_to_name:
      names.append(key)

    if 'counter' in kwargs and not kwargs['counter']:
      kwargs.pop('counter')

    mdl = dict(
      context='%s::%s' % (self.name, key),
      name='_'.join(names),
      label=label,
      description=description,
      numeratorUnit=self.numerator,
    )
    mdl.update(**kwargs)

    return mdl



class CounterDefinition(MetricDefinition):
  def __init__(self, *args, **kwargs):
    self.treat_counter_as_gauge = kwargs.pop('treat_counter_as_gauge', False)

    super(CounterDefinition, self).__init__(*args, **kwargs)

    assert not self.treat_counter_as_gauge or self.denominator is None, \
        "Counters should not have denominators"


  def to_json(self):
    return [
        self._make_json('count', counter=not self.treat_counter_as_gauge),
    ]


class HistogramDefinition(MetricDefinition):
  _add_key_to_name = True

  def __init__(self, *args, **kwargs):
    self.counter_numerator = kwargs.pop('counter_numerator')

    super(HistogramDefinition, self).__init__(*args, **kwargs)


  def to_json(self):
    return [
        self._make_json('max',
          label_suffix=MAX_LABEL_SUFFIX,
          description_suffix=MAX_DESCRIPTION_SUFFIX),
        self._make_json('min',
          label_suffix=MIN_LABEL_SUFFIX,
          description_suffix=MIN_DESCRIPTION_SUFFIX),
        self._make_json('avg',
          label_suffix=': Average',
          description_suffix=AVERAGE_DESCRIPTION_SUFFIX),
        self._make_json('count',
          label_suffix=SAMPLE_COUNT_LABEL_SUFFIX,
          description_suffix=SAMPLE_COUNT_DESCRIPTION_SUFFIX,
          counter=True,
          numeratorUnit=self.counter_numerator),
        self._make_json('sum',
          label_suffix=SAMPLE_SUM_LABEL_SUFFIX,
          description_suffix=SAMPLE_SUM_DESCRIPTION_SUFFIX,
          counter=True,
          numeratorUnit=self.counter_numerator),
        self._make_json('std_dev',
          label_suffix=STD_DEV_LABEL_SUFFIX,
          description_suffix=STD_DEV_DESCRIPTION_SUFFIX),
        self._make_json('median',
          label_suffix=PERCENTILE_50_LABEL_SUFFIX,
          description_suffix=PERCENTILE_50_DESCRIPTION_SUFFIX),
        self._make_json('75_percentile',
          label_suffix=PERCENTILE_75_LABEL_SUFFIX,
          description_suffix=PERCENTILE_75_DESCRIPTION_SUFFIX),
        self._make_json('95_percentile',
          label_suffix=PERCENTILE_95_LABEL_SUFFIX,
          description_suffix=PERCENTILE_95_DESCRIPTION_SUFFIX),
        self._make_json('99_percentile',
          label_suffix=PERCENTILE_99_LABEL_SUFFIX,
          description_suffix=PERCENTILE_99_DESCRIPTION_SUFFIX),
        self._make_json('999_percentile',
          label_suffix=PERCENTILE_999_LABEL_SUFFIX,
          description_suffix=PERCENTILE_999_DESCRIPTION_SUFFIX),
    ]


class GaugeDefinition(MetricDefinition):
  def __init__(self, *args, **kwargs):
    self.treat_gauge_as_counter = kwargs.pop('treat_gauge_as_counter', False)

    super(GaugeDefinition, self).__init__(*args, **kwargs)

    assert not self.treat_gauge_as_counter or self.denominator is None, \
        "Gauge metrics that are marked as counters cannot have a denominator"


  def to_json(self):
    return [
        self._make_json('value', counter=self.treat_gauge_as_counter),
    ]


class MeterDefinition(MetricDefinition):
  _add_key_to_name = True

  def __init__(self, *args, **kwargs):
    self.counter_numerator = kwargs.pop('counter_numerator')
    self.rate_denominator = kwargs.pop('rate_denominator')

    assert self.counter_numerator is not None
    assert self.rate_denominator is not None

    super(MeterDefinition, self).__init__(*args, **kwargs)

  def to_json(self):
    return [
        self._make_json('count',
          label_suffix=SAMPLE_SUM_LABEL_SUFFIX,
          description_suffix=SAMPLE_SUM_DESCRIPTION_SUFFIX,
          counter=True,
          numeratorUnit=self.counter_numerator),
        self._make_json('1m_rate',
          label_suffix=RATE_1_LABEL_SUFFIX,
          description_suffix=RATE_1_DESCRIPTION_SUFFIX,
          numeratorUnit=self.counter_numerator,
          denominatorUnit=self.rate_denominator),
        self._make_json('5m_rate',
          label_suffix=RATE_5_LABEL_SUFFIX,
          description_suffix=RATE_5_DESCRIPTION_SUFFIX,
          numeratorUnit=self.counter_numerator,
          denominatorUnit=self.rate_denominator),
        self._make_json('15m_rate',
          label_suffix=RATE_15_LABEL_SUFFIX,
          description_suffix=RATE_15_DESCRIPTION_SUFFIX,
          numeratorUnit=self.counter_numerator,
          denominatorUnit=self.rate_denominator),
    ]


class TimerDefinition(MetricDefinition):
  _add_key_to_name = True

  def __init__(self, *args, **kwargs):
    self.counter_numerator = kwargs.pop('counter_numerator')
    self.rate_denominator = kwargs.pop('rate_denominator')

    assert self.counter_numerator is not None
    assert self.rate_denominator is not None

    super(TimerDefinition, self).__init__(*args, **kwargs)


  def to_json(self):
    return [
        self._make_json('max',
          label_suffix=MAX_LABEL_SUFFIX,
          description_suffix=MAX_DESCRIPTION_SUFFIX),
        self._make_json('min',
          label_suffix=MIN_LABEL_SUFFIX,
          description_suffix=MIN_DESCRIPTION_SUFFIX),
        self._make_json('avg',
          label_suffix=': Average',
          description_suffix=AVERAGE_DESCRIPTION_SUFFIX),
        self._make_json('count',
          label_suffix=SAMPLE_COUNT_LABEL_SUFFIX,
          description_suffix=SAMPLE_COUNT_DESCRIPTION_SUFFIX,
          counter=True,
          numeratorUnit=self.counter_numerator),
        self._make_json('sum',
          label_suffix=SAMPLE_SUM_LABEL_SUFFIX,
          description_suffix=SAMPLE_SUM_DESCRIPTION_SUFFIX,
          counter=True,
          numeratorUnit=self.counter_numerator),
        self._make_json('std_dev',
          label_suffix=STD_DEV_LABEL_SUFFIX,
          description_suffix=STD_DEV_DESCRIPTION_SUFFIX),
        self._make_json('1m_rate',
          label_suffix=RATE_1_LABEL_SUFFIX,
          description_suffix=RATE_1_DESCRIPTION_SUFFIX,
          numeratorUnit=self.counter_numerator,
          denominatorUnit=self.rate_denominator),
        self._make_json('5m_rate',
          label_suffix=RATE_5_LABEL_SUFFIX,
          description_suffix=RATE_5_DESCRIPTION_SUFFIX,
          numeratorUnit=self.counter_numerator,
          denominatorUnit=self.rate_denominator),
        self._make_json('15m_rate',
          label_suffix=RATE_15_LABEL_SUFFIX,
          description_suffix=RATE_15_DESCRIPTION_SUFFIX,
          numeratorUnit=self.counter_numerator,
          denominatorUnit=self.rate_denominator),
        self._make_json('median',
          label_suffix=PERCENTILE_50_LABEL_SUFFIX,
          description_suffix=PERCENTILE_50_DESCRIPTION_SUFFIX),
        self._make_json('75_percentile',
          label_suffix=PERCENTILE_75_LABEL_SUFFIX,
          description_suffix=PERCENTILE_75_DESCRIPTION_SUFFIX),
        self._make_json('95_percentile',
          label_suffix=PERCENTILE_95_LABEL_SUFFIX,
          description_suffix=PERCENTILE_95_DESCRIPTION_SUFFIX),
        self._make_json('99_percentile',
          label_suffix=PERCENTILE_99_LABEL_SUFFIX,
          description_suffix=PERCENTILE_99_DESCRIPTION_SUFFIX),
        self._make_json('999_percentile',
          label_suffix=PERCENTILE_999_LABEL_SUFFIX,
          description_suffix=PERCENTILE_999_DESCRIPTION_SUFFIX),
    ]


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
