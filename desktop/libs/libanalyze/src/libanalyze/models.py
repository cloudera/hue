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
import json
from itertools import groupby

class Contributor(object):
  def __init__(self, **kwargs):
    self.id = None
    self.query_id = None
    self.type = None
    self.wall_clock_time = None
    self.plan_node_id = None
    self.plan_node_name = None
    self.reason = None
    self.__dict__.update(kwargs)

  def to_json(self):
    return json.dumps(self.__dict__)

class Reason(object):
  def __init__(self, **kwargs):
    self.name = None
    self.message = None
    self.impact = None
    self.unit = None
    self.fix = None
    self.__dict__.update(kwargs)

  def to_json(self):
    return json.dumps(self.__dict__)

class TCounter(object):
  def __init__(self, **kwargs):
    self.value = None
    self.name = None
    self.unit = None
    self.__dict__.update(kwargs)

def query_node_by_id(profile, node_id, metric_name, averaged=False):
  """Given the query_id, searches for the corresponding query profile and
  selects the node instances given by node_id, selects the metric given by
  metric_name and groups by fragment and fragment instance."""
  result = profile.find_by_id(node_id)
  if not result:
    return result

  nodes = _filter_averaged(result, averaged)
  metric = reduce(lambda x, y: x + y.find_metric_by_name(metric_name), nodes, [])

  return map(lambda x: L(x['value'], x['unit'], 0, x['node'].fragment.id(), x['node'].host(), 0, x['node'].id(), x['node'].name(), value=x['value'], unit=x['unit'], fragment_id=0, fid=x['node'].fragment.id(), host=x['node'].host(), node_id=x['node'].id(), name=x['node'].name(), node=x['node']), metric)

def query_node_by_id_value(profile, node_id, metric_name, averaged=False, default=0):
  results = query_node_by_id(profile, node_id, metric_name, averaged)
  return results and results[0][0] or default

def _filter_averaged(result, averaged=False):
  #nodes = filter(lambda x: x.fragment.is_averaged() == averaged, result)
  # Averaged results are not always present. If we're looking for averaged results, sort by averaged and get first result (hopefully getting averaged!).
  # If we're not looking for averaged results, remove them.
  if averaged:
    def by_averaged(x, y):
      if x.fragment.is_averaged():
        return -1
      elif y.fragment.is_averaged():
        return 1
      else:
        return 0
    return sorted(result, cmp=by_averaged)
  else:
    return filter(lambda x: x.fragment.is_averaged() == averaged, result)

def query_node_by_metric(profile, node_name, metric_name):
  """Given the query_id, searches for the corresponding query profile and
  selects the node instances given by node_name, selects the metric given by
  metric_name and groups by fragment and fragment instance."""

  result = profile.find_all_by_name(node_name)
  nodes = filter(lambda x: x.fragment.is_averaged() == False, result)
  metric = reduce(lambda x, y: x + y.find_metric_by_name(metric_name), nodes, [])
  return map(lambda x: L(x['value'], 0, x['node'].fragment.id(), x['node'].host(), 0, x['node'].id(), x['node'].name(), value=x['value'], unit=x['unit'], fragment_id=0, fid=x['node'].fragment.id(), host=x['node'].host(), node_id=x['node'].id(), name=x['node'].name(), node=x['node']), metric)

def query_element_by_metric(profile, node_name, metric_name):
  """Given the query_id, searches for the corresponding query profile and
  selects the node instances given by node_name, selects the metric given by
  metric_name and groups by fragment and fragment instance."""

  result = profile.find_all_by_name(node_name)
  nodes = filter(lambda x: not x.fragment or x.fragment.is_averaged() == False, result)
  metric = reduce(lambda x, y: x + y.find_metric_by_name(metric_name), nodes, [])
  return map(lambda x: L(x['value'], 0, x['node'].fragment.id() if x['node'].fragment else '', x['node'].host(), 0, x['node'].id(), x['node'].name(), value=x['value'], unit=x['unit'], fragment_id=0, fid=x['node'].fragment.id() if x['node'].fragment else '', host=x['node'].host(), node_id=x['node'].id(), name=x['node'].name(), node=x['node']), metric)

def query_element_by_info(profile, node_name, metric_name):
  """Given the query_id, searches for the corresponding query profile and
  selects the node instances given by node_name, selects the metric given by
  metric_name and groups by fragment and fragment instance."""

  result = profile.find_all_by_name(node_name)
  nodes = filter(lambda x: not x.fragment or x.fragment.is_averaged() == False, result)
  metric = reduce(lambda x, y: x + y.find_info_by_name(metric_name), nodes, [])
  return map(lambda x: L(x['value'], 0, x['node'].fragment.id() if x['node'].fragment else '', x['node'].host(), 0, x['node'].id(), x['node'].name(), value=x['value'], fragment_id=0, fid=x['node'].fragment.id() if x['node'].fragment else '', host=x['node'].host(), node_id=x['node'].id(), name=x['node'].name(), node=x['node']), metric)

def query_avg_fragment_metric_by_node_nid(profile, node_nid, metric_name, default):
  """
  Given the surragate node id (i.e. unique id of the plan node in the database),
  return the value of the fragment level metric.
  :param node_id:
  :param metric_name:
  :return: the value of the metric; none if there is no result
  """
  result = profile.find_by_id(node_nid)
  if not result:
    return result
  node = _filter_averaged(result, True)[0]
  metric = node.fragment.find_metric_by_name(metric_name)
  return metric and metric[0]['value'] or default

def query_fragment_metric_by_node_id(node, metric_name):
  """
  Given the surragate node id (i.e. unique id of the plan node in the database),
  return the value of the fragment level metric.
  :param node_id:
  :param metric_name:
  :return: the value of the metric; none if there is no result
  """
  metrics = node.find_metric_by_name(metric_name)
  return metrics[0]['value'] if metrics else None

def query_unique_node_by_id(profile, fragment_id, fragment_instance_id, node_id):
  result = profile.find_by_id(node_id)
  nodes = filter(lambda x: ((x.fragment is None and x.is_fragment()) or x.fragment.id() == fragment_id) and x.fragment_instance.id() == fragment_instance_id, result)
  return nodes[0]

def host_by_metric(profile, metric_name, exprs=[max]):
  """Queries all fragment instances for a particular associated metric value.
  Calculates the aggregated value based on exprs."""
  fragments = profile.find_all_fragments()
  fragments = filter(lambda x: x.is_averaged() == False, fragments)
  metrics = reduce(lambda x,y: x + y.find_metric_by_name(metric_name), fragments, [])
  results = L(unit=-1)
  for k, g in groupby(metrics, lambda x: x['node'].host()):
      grouped = list(g)
      values = map(lambda x: x['value'], grouped)
      result = [k]
      for expr in exprs:
        value = expr(values)
        result.append(value)
      results.append(result)
      if grouped:
        results.unit = grouped[0]['unit']

  return results

class L(list):
  def __new__(self, *args, **kwargs):
      return super(L, self).__new__(self, args, kwargs)

  def __init__(self, *args, **kwargs):
      if len(args) == 1 and hasattr(args[0], '__iter__'):
          list.__init__(self, args[0])
      else:
          list.__init__(self, args)
      self.__dict__.update(kwargs)

  def __call__(self, **kwargs):
      self.__dict__.update(kwargs)
      return self