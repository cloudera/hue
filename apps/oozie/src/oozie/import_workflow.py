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

import logging
from lxml import etree

from django.core import serializers
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException

from conf import DEFINITION_XSLT_DIR
from models import Node, Link, Start, End, Decision, DecisionEnd, Fork, Join
from utils import xml_tag

LOG = logging.getLogger(__name__)

OOZIE_NAMESPACES = ['uri:oozie:workflow:0.1', 'uri:oozie:workflow:0.2', 'uri:oozie:workflow:0.3', 'uri:oozie:workflow:0.4']

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
    parent = Node.objects.get(workflow=workflow, name=node.attrib.get('name', xml_tag(node))).get_full_node()

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

          if xml_tag(case) == 'default':
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
        name = xml_tag(el)
        if name in LINKS:
          if name == 'path':
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
  Decision DAG ends are inferred by counting the parents of nodes that are node joins.
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

  Performs a depth first search to understand branching.
  """
  def insert_end(node, decision):
    """Insert DecisionEnd between node and node parents"""
    parent_links = node.get_parent_links().exclude(name='default')
    decision_end = decision.get_child_end()

    # Find parent decision node for every end's parent.
    # If the decision node is the one passed,
    # change the parent to link to the Decision node's DecisionEnd node.
    # Skip embedded decisions and forks along the way.
    decision_end_used = False
    for parent_link in parent_links:
      parent = parent_link.parent.get_full_node()
      node_temp = parent
      while node_temp and not isinstance(node_temp, Decision):
        if isinstance(node_temp, Join):
          node_temp = node_temp.get_parent_fork().get_parent()
        elif isinstance(node_temp, DecisionEnd):
          node_temp = node_temp.get_parent_decision().get_parent()
        else:
          node_temp = node_temp.get_parent()

      if node_temp.id == decision.id and parent.node_type != Decision.node_type:
        links = Link.objects.filter(parent=parent).exclude(name__in=['related', 'kill', 'error'])
        if len(links) != 1:
          raise PopupException(_('Cannot import workflows that have decision DAG leaf nodes with multiple children or no children.'))
        link = links[0]
        link.child = decision_end
        link.save()

        decision_end_used = True

    # Create link between DecisionEnd and terminal node.
    if decision_end_used and not Link.objects.filter(name='to', parent=decision_end, child=node).exists():
      link = Link(name='to', parent=decision_end, child=node)
      link.save()

  def decision_helper(decision):
    """
    Iterates through children, waits for ends.
    When an end is found, finish the decision.
    If the end has more parents than the decision has branches, bubble the end upwards.
    """
    # Create decision end if it does not exist.
    if not Link.objects.filter(parent=decision, name='related').exists():
      end = DecisionEnd(workflow=workflow, node_type=DecisionEnd.node_type)
      end.save()
      link = Link(name='related', parent=decision, child=end)
      link.save()

    children = [link.child.get_full_node() for link in decision.get_children_links().exclude(name__in=['error','default'])]

    ends = set()
    for child in children:
      end = helper(child)
      if end:
        ends.add(end)

    # A single end means that we've found a unique end for this decision.
    # Multiple ends mean that we've found a bad decision.
    if len(ends) > 1:
      raise PopupException(_('Cannot import workflows that have decisions paths with multiple terminal nodes that converge on a single terminal node.'))
    elif len(ends) == 1:
      end = ends.pop()
      # Branch count will vary with each call if we have multiple decision nodes embedded within decision paths.
      # This is because parents are replaced with DecisionEnd nodes.
      fan_in_count = len(end.get_parent_links().exclude(name__in=['error','default']))
      # IF it covers all branches, then it is an end that perfectly matches this decision.
      # ELSE it is an end for a decision path that the current decision node is a part of as well.
      # The unhandled case is multiple ends for a single decision that converge on a single end.
      # This is not handled in Hue.
      fan_out_count = len(decision.get_children_links().exclude(name__in=['error','default']))
      if fan_in_count > fan_out_count:
        insert_end(end, decision)
        return end
      elif fan_in_count == fan_out_count:
        insert_end(end, decision)
        # End node is a decision node.
        # This means that there are multiple decision nodes in sequence.
        # If both decision nodes are within a single decision path,
        # then the end may need to be returned, if found.
        if isinstance(end, Decision):
          end = decision_helper(end)
          if end:
            return end

        # Can do this because we've replace all its parents with a single DecisionEnd node.
        return helper(end)
      else:
        raise PopupException(_('Cannot import workflows that have decisions paths with multiple terminal nodes that converge on a single terminal node.'))
    else:
      raise PopupException(_('Cannot import workflows that have decisions paths that never end.'))

    return None

  def helper(node):
    """Iterates through nodes, returning ends."""
    # Assume receive full node.
    children = [link.child.get_full_node() for link in node.get_children_links().exclude(name__in=['error','default'])]

    # Will not be a kill node because we skip error links.
    # Error links should not go to a regular node.
    if node.get_parent_links().filter(name='error').exists():
      raise PopupException(_('Error links cannot point to an ordinary node.'))

    # Multiple parents means that we've found an end.
    # Joins will always have more than one parent.
    fan_in_count = len(node.get_parent_links().exclude(name__in=['error','default']))
    if fan_in_count > 1 and not isinstance(node, Join) and not isinstance(node, DecisionEnd):
      return node
    elif isinstance(node, Decision):
      end = decision_helper(node)
      if end:
        return end
    # I case of fork, should not find different ends.
    elif len(children) > 1:
      end = None
      for child in children:
        temp = helper(child)
        end = end or temp
        if end != temp:
          raise PopupException(_('Different ends found in fork.'))
      return end
    elif children:
      return helper(children.pop())

    # Likely reached end.
    return None

  helper(workflow.start.get_full_node())


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


def import_workflow(workflow, workflow_definition):
  xslt_definition_fh = open("%(xslt_dir)s/workflow.xslt" % {
    'xslt_dir': DEFINITION_XSLT_DIR.get()
  })

  # Parse Workflow Definition
  xml = etree.fromstring(workflow_definition)

  if xml is None:
    raise PopupException(_("Could not find any nodes in Workflow definition. Maybe it's malformed?"))

  ns = xml.tag[:-12] # Remove workflow-app from tag in order to get proper namespace prefix
  schema_version = ns and ns[1:-1] or None

  # Ensure namespace exists
  if schema_version not in OOZIE_NAMESPACES:
    raise PopupException(_("Tag with namespace %(namespace)s is not a valid. Please use one of the following namespaces: %(namespaces)s") % {
      'namespace': xml.tag,
      'namespaces': ', '.join(OOZIE_NAMESPACES)
    })

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
  workflow.schema_version = schema_version
  workflow.save()