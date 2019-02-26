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
import base64
import json
import os
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../..", 'gen-py'))

from RuntimeProfile.ttypes import *
from thrift.protocol import TCompactProtocol
from thrift.transport import TTransport

from libanalyze import dot
from libanalyze import gjson as jj
from libanalyze import models
from libanalyze import utils
from libanalyze.rules import to_double


class Node(object):
  """Simple Node"""

  def __init__(self, val):
    super(Node, self).__init__()
    self.val = val
    self.children = []
    self.fragment = None
    self.fragment_instance = None
    self.plan_node = None
    self.pos = 0
    self.node_name = None
    self.node_id = None
    self.node_is_fragment = None
    self.node_is_fragment_instance = None
    self.node_is_regular = None
    self.node_is_plan_node = None

  def add_child(self, c):
    self.children.append(c)

  def find_by_name(self, pattern):
    """Returns the first node whose name matches 'name'."""
    if self.val.name.find(pattern) >= 0:
      return self

    for x in self.children:
      tmp = x.find_by_name(pattern)
      if tmp:
        return tmp

  def find_all_by_name(self, pattern):
    result = []
    if self.val.name.find(pattern) >= 0:
      result.append(self)
    for x in self.children:
      result += x.find_all_by_name(pattern)
    return result

  def find_all_non_fragment_nodes(self):
    result = []
    if not self.is_fragment() and not self.is_fragment_instance():
      result.append(self)
    for x in self.children:
      result += x.find_all_non_fragment_nodes()
    return result

  def is_fragment(self):
    if self.node_is_fragment is not None:
      return self.node_is_fragment
    self.node_is_fragment = re.search(r'(.*?Fragment) (F\d+)', self.val.name) is not None
    return self.node_is_fragment

  def is_fragment_instance(self):
    if self.node_is_fragment_instance is not None:
      return self.node_is_fragment_instance
    self.node_is_fragment_instance = re.search(r'Instance\s(.*?)\s\(host=(.*?)\)', self.val.name) is not None
    return self.node_is_fragment_instance

  def is_regular(self):
    if self.node_is_regular is not None:
      return self.node_is_regular
    id = self.id()
    matches = id and re.search(r'^\d*$', id)
    self.node_is_regular = id and matches
    return self.node_is_regular

  def name(self):
    if self.node_name:
      return self.node_name
    matches = re.search(r'(.*?)(\s+\(((dst_)?id)=(\d+)\))?$', self.val.name)
    if matches and matches.group(5):
      self.node_name = matches.group(1)
    elif self.is_fragment():
      self.node_name = re.search(r'(.*?Fragment) (F\d+)', self.val.name).group(1)
    else:
      matches = re.search(r'(.*?)(\s+\(.*?\))?$', self.val.name)
      if matches.group(2):
        self.node_name = matches.group(1)
      else:
        self.node_name = self.val.name
    return self.node_name


  def id(self):
    if self.node_id:
      return self.node_id
    matches = re.search(r'(.*?)(\s+\(((dst_)?id)=(\d+)\))?$', self.val.name)
    if matches and matches.group(5) and not matches.group(4):
      self.node_id = matches.group(5)
    elif self.is_fragment():
      self.node_id = re.search(r'(.*?Fragment) (F\d+)', self.val.name).group(2)
    elif self.is_fragment_instance():
      self.node_id = re.search(r'Instance\s(.*?)\s\(host=(.*?)\)', self.val.name).group(1)
    elif self.fragment:
      self.node_id = self.fragment.id() + ' ' + str(self.pos)
    return self.node_id

  def is_plan_node(self):
    if self.node_is_plan_node is not None:
      self.node_is_plan_node
    matches = re.search('(.*?)(\s+\(((dst_)?id)=(\d+)\))?$', self.val.name)
    self.node_is_plan_node = matches and not matches.group(4) and matches.group(5)
    return self.node_is_plan_node

  def find_by_id(self, pattern):
    if self.nodes and self.nodes.get(pattern):
      return self.nodes[pattern]
    results = []
    if self.id() == pattern:
      results.append(self)

    for x in self.children:
      tmp = x.find_by_id(pattern)
      results += tmp

    return results

  def find_all_fragments(self):
    results = []
    if self.is_fragment_instance():
      results.append(self)

    for x in self.children:
      tmp = x.find_all_fragments()
      results += tmp

    return results

  def foreach_lambda(self, method, plan_node=None, fragment=None, fragment_instance=None, pos=0):
    self.fragment = fragment
    self.fragment_instance = fragment_instance
    self.pos = pos
    self.plan_node = plan_node
    if self.is_fragment():
      fragment = self
    elif self.is_fragment_instance():
      fragment_instance = self
    elif self.is_plan_node():
      plan_node = self

    for idx, x in enumerate(self.children):
      x.foreach_lambda(method, plan_node=plan_node, fragment=fragment, fragment_instance=fragment_instance, pos=idx)

    method(self) # Post execution, because some results need child to have processed

  def find_metric_by_name(self, pattern):
    node = self
    ctr_map = node.counter_map()
    counters = []
    for k in ctr_map:
      if pattern == k:
        counters.append({'name': ctr_map[k].name, 'value': ctr_map[k].value,
                  'unit': ctr_map[k].unit, 'node': node})

    for k in node.child_counters_map():
      v = node.child_counters_map()[k]
      if pattern == k:
        parent = None
        if k in ctr_map:
          parent = {'name': ctr_map[k].name, 'value': ctr_map[k].value,
                  'unit': ctr_map[k].unit}
        for cc in v:
          counters.append({'name': ctr_map[cc].name, 'value': ctr_map[cc].value,
                  'unit': ctr_map[cc].unit, 'parent': parent, 'node': node})
    return counters

  def find_info_by_name(self, pattern):
    node = self
    ctr_map = node.val.info_strings
    counters = []
    if ctr_map.get(pattern):
      counters.append({'name': pattern, 'value': ctr_map.get(pattern), 'node': node})
    return counters

  # Only for fragments
  def is_averaged(self):
    return re.search(r"Averaged", self.val.name) is not None

  # Only for fragments
  def is_coordinator(self):
    return re.match(r'Coordinator', self.val.name) is not None

  # Only for fragments
  def host(self):
    if self.fragment_instance:
      c = self.fragment_instance
    elif self.fragment:
      c = self.fragment.children[0]
    else:
      return None
    m = re.search(r'Instance\s(.*?)\s\(host=(.*?)\)', c.val.name)
    if m:
        #frag.instance_id = m.group(1)
        #frag.host = m.group(2)
        #frag_node = c
        return m.group(2)

  def augmented_host(self):
    if self.is_fragment_instance():
      c = self
    elif self.is_fragment():
      if self.is_averaged():
        return 'averaged'
      else:
        c = self.children[0]
    elif self.fragment_instance:
      c = self.fragment_instance
    elif self.fragment:
      if self.fragment.is_averaged():
        return 'averaged'
      c = self.fragment.children[0]
    else:
      return None
    m = re.search(r'Instance\s(.*?)\s\(host=(.*?)\)', c.val.name)
    if m:
        #frag.instance_id = m.group(1)
        #frag.host = m.group(2)
        #frag_node = c
        return m.group(2)

  def info_strings(self):
    return self.val.info_strings

  def info_string_order(self):
    return self.val.info_strings_display_order

  def child_counters_map(self):
    return self.val.child_counters_map

  def counter_map(self):
    ctr = {}
    if self.val.counters:
        for c in self.val.counters:
            ctr[c.name] = c
    return ctr

  def metric_map(self):
    ctr = {}
    if self.val.counters:
        for c in self.val.counters:
            ctr[c.name] = { 'name': c.name, 'value': to_double(c.value) if c.unit == 6 else c.value, 'unit': c.unit }
    return ctr

  def event_list(self):
    event_list = {}
    if self.val.event_sequences:
      for s in self.val.event_sequences:
        start_time = 0
        sequence_name = s.name
        event_list[sequence_name] = []
        start_time = 0
        for i in range(len(s.labels)):
          event_duration = s.timestamps[i] - start_time
          event_name = s.labels[i]
          event_list[sequence_name].append({'name': event_name, 'value': s.timestamps[i], 'unit': 5, 'start_time': start_time, 'duration': event_duration})
          start_time = s.timestamps[i]
    return event_list

  def repr(self, indent):
    buffer = indent + self.val.name + "\n"
    if self.val.info_strings:
      for k in self.val.info_strings:
        buffer += 2 * indent + " - " + k + "=" + \
          self.val.info_strings[k][:40] + "\n"

    if self.val.event_sequences:
      for s in self.val.event_sequences:
        buffer += 2 * indent + "- " + s.name + \
          " S[" + ", ".join(s.labels) + "]" + "\n"

    ctr = {}
    if self.val.counters:
      for c in self.val.counters:
        buffer += 2 * indent + c.name + ":" + str(c) + "\n"
        ctr[c.name] = c
    return buffer


def decode_thrift(val):
  """Deserialize a binary string into the TRuntimeProfileTree structure"""
  transport = TTransport.TMemoryBuffer(val)
  protocol = TCompactProtocol.TCompactProtocol(transport)
  rp = TRuntimeProfileTree()
  rp.read(protocol)
  return rp


def decompress(val):
  return val.decode("zlib")


def summary(profile):
  summary = profile.find_by_name('Summary')
  execution_profile = profile.find_by_name('Execution Profile')
  counter_map = summary.counter_map()
  counter_map_execution_profile = execution_profile.counter_map()
  host_list = models.host_by_metric(profile, 'PeakMemoryUsage', exprs=[max])
  host_list = sorted(host_list, key=lambda x: x[1], reverse=True)
  peak_memory = models.TCounter(value=host_list[0][1], unit=3) if host_list else models.TCounter(value=0, unit=3) # The value is not always present
  return [{ 'key': 'PlanningTime', 'value': counter_map['PlanningTime'].value, 'unit': counter_map['PlanningTime'].unit }, {'key': 'RemoteFragmentsStarted', 'value': counter_map['RemoteFragmentsStarted'].value, 'unit': counter_map['RemoteFragmentsStarted'].unit}, {'key': 'TotalTime', 'value': counter_map_execution_profile['TotalTime'].value, 'unit': counter_map_execution_profile['TotalTime'].unit}, {'key': 'PeakMemoryUsage', 'value': peak_memory.value, 'unit': peak_memory.unit}]

def metrics(profile):
  execution_profile = profile.find_by_name('Execution Profile')
  summary = profile.find_by_name("Summary")
  plan_json = utils.parse_plan_details(summary.val.info_strings.get('Plan')) if summary.val.info_strings.get('Plan') else {}
  if not execution_profile:
    return {}
  counter_map = {'nodes': {}, 'max': 0, 'summary': {'timeline': summary.event_list(), 'properties': summary.metric_map()}}
  def flatten(node, counter_map=counter_map):
    is_plan_node = node.is_plan_node()
    is_parent_node = is_plan_node
    bIncludeInMinMax = True
    if not is_plan_node:
      if node.plan_node:
        nid = node.plan_node.id()
      elif node.is_fragment_instance():
        is_parent_node = True
        nid = node.fragment.id()
        bIncludeInMinMax = False
      elif node.is_fragment() and node.is_averaged():
        is_parent_node = True
        nid = node.id()
        bIncludeInMinMax = False
      elif node.fragment:
        nid = node.fragment.id()
      else:
        return
    else:
      nid = node.id()

    host = node.augmented_host()
    metric_map = node.metric_map()
    if counter_map['nodes'].get(nid) is None:
      counter_map['nodes'][nid] = {'properties': { 'hosts': {} }, 'children': { }, 'timeline': {'hosts': {}}, 'other': {}}

    event_list = node.event_list();

    if is_parent_node:
      counter_map['nodes'][nid]['properties']['hosts'][host] = metric_map
      if event_list:
        counter_map['nodes'][nid]['timeline']['hosts'][host] = event_list
      if plan_json.get(nid):
        counter_map['nodes'][nid]['other'] = plan_json[nid]
      if is_plan_node:
        counter_map['nodes'][nid]['fragment'] = node.fragment.id()
      counter_map['nodes'][nid]['timeline']['minmax'] = bIncludeInMinMax
    else:
      name = node.name()
      if counter_map['nodes'][nid]['children'].get(name) is None:
        counter_map['nodes'][nid]['children'][name] = {'hosts': {}}
      counter_map['nodes'][nid]['children'][name]['hosts'][host] = metric_map

  execution_profile.foreach_lambda(flatten)

  for nodeid, node in counter_map['nodes'].iteritems():
    host_min = {'value': sys.maxint, 'host' : None}
    host_max = {'value': -(sys.maxint - 1), 'host' : None}
    if not node['timeline']['minmax']:
      continue
    for host_name, host_value in node['timeline']['hosts'].iteritems():
      for event_name, event in host_value.iteritems():
        if len(event):
          value = event[len(event) - 1]['value']
          if value < host_min['value']:
            host_min['value'] = value
            host_min['host'] = host_name
          if value > host_max['value']:
            host_max['value'] = value
            host_max['host'] = host_name
    node['timeline']['min'] = host_min.get('host', '')
    node['timeline']['max'] = host_max.get('host', '')
    if node['timeline']['min']:
      counter_map['max'] = max(host_min['value'], counter_map['max'])

  counter_map['ImpalaServer'] = profile.find_by_name('ImpalaServer').metric_map()
  return counter_map

def heatmap_by_host(profile, counter_name):
  rows = models.host_by_metric(profile,
                               counter_name,
                               exprs=[max, sum])
  # Modify the data to contain the relative data as well
  sum_sum = 0
  max_max = 0
  if (rows):
    sum_sum = float(sum([v[2] for v in rows]))
    max_max = float(max([v[1] for v in rows]))

  result = []
  for r in rows:
    result.append([r[0], float(r[1]), float(r[2]),
        float(r[1]) / float(max_max) if float(max_max) != 0 else 0,
        float(r[2]) / float(sum_sum) if float(sum_sum) != 0 else 0,
        rows.unit])
  return { 'data': result, 'max': max_max, 'unit': rows.unit }

def parse(file_name):
  """Given a file_name, open the file and decode the first line of the file
  into the TRuntimeProfileTree structure."""
  with open(file_name) as fid:
    for line in fid:
      val = base64.decodestring(line.strip())
      try:
          val = decompress(val.strip())
      except:
          pass
      return decode_thrift(val)

def parse_data(data):
  val = base64.decodestring(data)
  try:
      val = decompress(val.strip())
  except:
      pass
  return decode_thrift(val)

def pre_order_traversal(nodes, index, level=0):
  # print index, nodes[index].num_children, nodes[index].name, level
  node = Node(nodes[index])
  pos = index
  for x in range(node.val.num_children):
      child_node, pos = pre_order_traversal(nodes, pos + 1, level + 1)
      node.add_child(child_node)
  return node, pos

def analyze(profile):
  """The runtime profile tree is pre-order flattened"""
  node, _ = pre_order_traversal(profile.nodes, 0)
  return node

def get_plan(profile):
  return profile.find_by_name("Sumary").val.info_strings["Plan"]


def to_dot(profile):
  fragments = [
      x for x in profile.find_by_name("Execution Profile").children if re.search(
          "Averaged|Coordinator",
          x.val.name)]
  return dot.graph_to_dot(fragments)


def to_json(profile):
  fragments = [
      x for x in profile.find_by_name("Execution Profile").children if re.search(
          "Averaged|Coordinator",
          x.val.name)]
  return json.dumps(jj.graph_to_json(fragments))


def print_tree(node, level, indent):
  if level == 0:
      return
  print node.repr(indent)
  for c in node.children:
      print_tree(c, level - 1, indent + "  ")


if __name__ == '__main__':
  pass
  # from datetime import datetime
  # from dateutil.parser import parse as dtparse

  # db_engine = create_engine('sqlite:///profiles.db', echo=False)
  thrift = parse(sys.argv[1])
  root = analyze(thrift)
  # for n in root.find_by_name("Summary").info_strings():
  #     print n
  #

  summary = root.find_by_name("Execution Profile")
  print_tree(summary, 4, " ")

  # db.Base.metadata.create_all(db_engine)
  # Session2 = sessionmaker(bind=db_engine)

  # query_id = "ea48c505d8604dc4:d4c46af6d57afa4"

  # from sqlalchemy.schema import *
  # impala_engine = create_engine('impala://mgrund-desktop.ca.cloudera.com/default', echo=False)
  # dstat = Table('dstat', MetaData(bind=impala_engine), autoload=True)

  # Session = sessionmaker(bind=impala_engine)
  # session = Session()
  # data = session.query(dstat).all()

  # sss = Session2()
  # # tt = db.Dstat.__table__
  # # cols = [c.key for c in db.Dstat.__table__.columns]

  # # for i, d in enumerate(data):
  # #     sss.add(db.Dstat(**dict(zip(cols[1:], d))))

  # sss.commit()

  # from sqlalchemy.sql import func

  # #sss.query(db.RuntimeProfile).filter(db.RuntimeProfile.query_id==query_id)
  # instances = db.query_node_by_metric(sss, query_id, "HASH_JOIN_NODE", "TotalTime", 5)

  # for i in instances:
  #     node = sss.query(db.Node).filter(db.Node.id==i[3]).one()
  #     infos = {x.name: x.val for x in node.info_strings}

  #     left = (dtparse(infos["StartTime"]) - datetime(1970,1,1)).total_seconds() + 7*3600
  #     right = (dtparse(infos["StopTime"]) - datetime(1970,1,1)).total_seconds() + 7*3600

  # print "HASH_JOIN_NODE", i.fid, i.host, sss.query(func.avg(db.Dstat.usr),
  # func.max(db.Dstat.usr)).filter(db.Dstat.ts<=left,
  # db.Dstat.ts<=right).all()

  # #to_db(db_engine, root)

  #summary = root.find_by_name("Execution Profile")

  # #print summary.info_strings()["ExecSummary"]

  #print_tree(summary, 3, "  ")
  # #list = root.find_all_by_name("CodeGen")

  # #print next(x for x in list[0].val.counters if x.name == "TotalTime").value / float(10**9)
  # #n = root.find_by_name("Averaged Fragment F01")
  # #print_tree(n, 2, "  ")

  # #summary = root.find_by_name("ImpalaServer")
  # #print summary.val.info_strings.keys()
  # #print summary.val.info_strings["Plan"]

# #print summary.val.info_strings["ExecSummary"]
