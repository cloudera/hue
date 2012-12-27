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
"""
Import an external workflow by providing an XML definition.
The workflow definition is imported via the method 'import_workflow'.
The XML is first transformed into a django serialized string that can be deserialized and interpreted.
The interpreted objects are then assigned the worklow, stripped of any useless IDs and saved.
Then the links are interpreted from the original XML definition.
First the basic links are interpreted for basic hierarchy traversal.
Then the related links are infered, including Decision node ends.
See oozie.models.Decision for more information on decision ends.

The XSLTs are partitioned by version.
For every new workflow DTD version a new directory should be created.
IE: uri:oozie:workflow:0.4 => 0.4 directory in xslt dir.
Action extensions are also versioned.
Every action extension will have its own version via /xslt/<workflow version>/extensions/<name of extensions>.<version>.xslt
"""

try:
  import json
except ImportError:
  import simplejson as json
from collections import deque
import logging
import re
from lxml import etree

from django.core import serializers
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException

from conf import DEFINITION_XSLT_DIR
from models import Node, Link, Start, End, Decision, DecisionEnd, Fork, Join

LOG = logging.getLogger(__name__)

LINKS = ('ok', 'error', 'path')
def _save_links(workflow, root):
  """
  Iterates over all links in the passed XML doc and creates links.
  First non-META links are resolved and created, then META links.
  Link name is chosen with the following logic:
    If node is start, then use 'to'.
    Else If node is Join, then use 'to'.
    Else If node is Decision, then
      If tag is 'default', then use 'default'
      Else use 'start'
    Else
      If tag is 'path', use 'start'
      Else use tag as name ('ok' or 'error')

  This strategy has the following resolution:
    - Fork and Decision nodes have Links named 'start'.
    - Decision nodes have a 'default' link.
    - Decision nodes may have a 'related' link that is there end.
    - Fork nodes always have a 'related' node that is there end join node.
    - Start and Join nodes have links named 'to'.
    - All action nodes have 'ok' and 'error' links.

  Note: The nodes that these links point to should exist already.
  Note: Nodes are looked up by workflow and name.
  """
  # Iterate over nodes
  for node in root:
    # Iterate over node members
    # Join nodes have attributes which point to the next node
    # Start node has attribute which points to first node
    parent = Node.objects.get(workflow=workflow, name=node.attrib.get('name', node.tag)).get_full_node()

    if isinstance(parent, Start):
      workflow.start = parent
      to = node.attrib['to']
      child = Node.objects.get(workflow=workflow, name=to)
      obj = Link.objects.create(name='to', parent=parent, child=child)
      obj.save()

    elif isinstance(parent, Join):
      to = node.attrib['to']
      child = Node.objects.get(workflow=workflow, name=to)
      obj = Link.objects.create(name='to', parent=parent, child=child)
      obj.save()

    elif isinstance(parent, Decision):
      for switch in node:
        for case in switch:
          to = case.attrib['to']
          child = Node.objects.get(workflow=workflow, name=to)

          if case.tag == 'default':
            name = 'default'
            obj = Link.objects.create(name=name, parent=parent, child=child)

          else:
            name = 'start'
            comment = case.text.strip()
            obj = Link.objects.create(name=name, parent=parent, child=child, comment=comment)

          obj.save()

    else:
      for el in node:
        # Links
        if el.tag in LINKS:
          name = el.tag
          if el.tag == 'path':
            to = el.attrib['start']
            name = 'start'
          else:
            to = el.attrib['to']

          child = Node.objects.get(workflow=workflow, name=to)
          obj = Link.objects.create(name=name, parent=parent, child=child)
          obj.save()

  workflow.end = End.objects.get(workflow=workflow).get_full_node()
  workflow.save()

  _resolve_fork_relationships(workflow)
  _resolve_decision_relationships(workflow)


def _resolve_fork_relationships(workflow):
  """
  Requires proper workflow structure.
  Fork must come before a join.
  """
  def helper(workflow, node, last_fork):
    if isinstance(node, Fork):
      join = None
      children = node.get_children()
      for child in children:
        join = helper(workflow, child.get_full_node(), node) or join
      link = Link(name='related', parent=node, child=join)
      link.save()

      node = join

    elif isinstance(node, Join):
      return node

    join = None
    children = node.get_children()
    for child in children:
      join = helper(workflow, child.get_full_node(), last_fork) or join
    return join

  helper(workflow, workflow.start.get_full_node(), None)


def _resolve_decision_relationships(workflow):
  """
  Requires proper workflow structure.
  Decision must come before a any random ends.
  DecisionEnd nodes are added to the end of the decision DAG.
  A 'related' link is created to associate the DecisionEnd to the Decision.
  IE:      D
         D   N
       N   N
           N
        equals
           D
         D   N
       N   N
         E
           E
           N

  Performs a breadth first search to understand branching.
  Call helper for every new decision found.
  Skip forks because decisions currently cannot live in forks.
  """
  def find_decision(node):
    if isinstance(node, Fork):
      node = node.get_child_join().get_full_node()

    decision = None
    children = node.get_children()
    for child in children:
      child = child.get_full_node()
      if isinstance(child, Decision):
        return child
      decision = find_decision(child) or decision
    return decision

  def insert_end(node, decision_end):
    """Insert DecisionEnd between node and node parents"""
    parent_links = node.get_parent_links().exclude(name='default')

    # Nodes that will be seen will always have one node
    # Otherwise, we should fail.
    for parent_link in parent_links:
      parent = parent_link.parent
      if parent.node_type != Decision.node_type:
        links = Link.objects.filter(parent=parent).exclude(name__in=['related', 'kill', 'error'])
        if len(links) != 1:
          raise PopupException(_('Cannot import workflows that have decision DAG leaf nodes with multiple children or no children.'))
        link = links[0]
        link.child = decision_end
        link.save()

    # Create link between DecisionEnd and terminal node.
    link = Link(name='to', parent=decision_end, child=node)
    link.save()

  def helper(decision):
    visit = deque(decision.get_children())
    branch_count = len(visit)

    # Create decision end if it does not exist.
    if not Link.objects.filter(parent=decision, name='related').exists():
      end = DecisionEnd(workflow=workflow, node_type=DecisionEnd.node_type)
      end.save()
      link = Link(name='related', parent=decision, child=end)
      link.save()

    # Find end
    while visit:
      node = visit.popleft().get_full_node()
      parents = node.get_parents()

      # An end is found...
      # IF it covers all branches, then it is an end that perfectly matches this decision.
      # ELSE it is an end for a higher decision as well.
      # The unhandled case is multiple ends for a single decision that converge on a single end.
      # This is not handled in Hue.
      if isinstance(node, Decision):
        end, end_parent_count = helper(node)
        branch_count -= 1

        if end_parent_count < branch_count:
          # In case we hit a workflow that has 2 decision or more nodes where the ends
          # do not cover the entire decision DAG.
          raise PopupException(_('Cannot import workflows that have decisions paths with multiple terminal nodes that converge on a single terminal node.'))

        else:
          insert_end(end, decision.get_child_end())
          if end_parent_count != branch_count:
            return end, end_parent_count - branch_count

        visit.extend(end.get_children())

      elif not isinstance(node, Join) and not isinstance(node, DecisionEnd) and len(parents) > 1:
        if len(parents) < branch_count:
          raise PopupException(_('Cannot import workflows that have decisions paths with multiple terminal nodes that converge on a single terminal node.'))

        else:
          insert_end(node, decision.get_child_end())
          if len(parents) != branch_count:
            return node, len(parents) - branch_count

        visit.extend(node.get_children())

      else:
        visit.extend(node.get_children())

  decision = find_decision(workflow.start.get_full_node())
  if decision is not None:
    helper(decision)


def _save_nodes(workflow, root):
  # Deserialize
  objs = serializers.deserialize('xml', etree.tostring(root))

  # First pass is a list of nodes and their types respectively.
  # Must link up nodes with their respective full nodes.
  node = None
  for obj in objs:
    obj.object.workflow = workflow
    if type(obj.object) is Node:
      node = obj.object
    else:
      node.node_type = obj.object.node_type
      full_node = obj.object
      for k, v in vars(node).items():
        if not k.startswith('_') and k not in ('node_type','workflow','node_ptr_id'):
          setattr(full_node, k, v)
      full_node.workflow = workflow
      full_node.node_type = type(full_node).node_type
      full_node.node_ptr_id = None
      full_node.id = None

      if full_node.node_type is 'start':
        full_node.name = 'start'

      full_node.save()


def import_workflow(workflow, workflow_definition, schema_version=0.4):
  xslt_definition_fh = open("%(xslt_dir)s/%(schema_version)s/workflow.xslt" % {
    'xslt_dir': DEFINITION_XSLT_DIR.get(),
    'schema_version': schema_version
  })

  # Remove namespace from definition
  workflow_definition = re.sub(r'\s*xmlns=".*?"', '', workflow_definition, count=1)

  # Parse Workflow Definition
  xml = etree.fromstring(workflow_definition)

  # Get XSLT
  xslt = etree.parse(xslt_definition_fh)
  xslt_definition_fh.close()
  transform = etree.XSLT(xslt)

  # Transform XML using XSLT
  root = transform(xml)

  # Resolve workflow dependencies and node types and link dependencies
  _save_nodes(workflow, root)
  _save_links(workflow, xml)

  # Update schema_version
  workflow.schema_version = "uri:oozie:workflow:%s" % schema_version
  workflow.save()