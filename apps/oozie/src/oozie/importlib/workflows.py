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

import json
import logging
from lxml import etree
import os
import re

from django.core import serializers
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _

from desktop.models import Document

from oozie.conf import DEFINITION_XSLT_DIR, DEFINITION_XSLT2_DIR
from oozie.models import Workflow, Node, Link, Start, End,\
                         Decision, DecisionEnd, Fork, Join,\
                         Kill

LOG = logging.getLogger(__name__)

OOZIE_NAMESPACES = ['uri:oozie:workflow:0.1', 'uri:oozie:workflow:0.2', 'uri:oozie:workflow:0.3', 'uri:oozie:workflow:0.4', 'uri:oozie:workflow:0.5']

LINKS = ('ok', 'error', 'path')


def _set_properties(workflow, root, namespace):
  # root should be config element.
  properties = []
  seen = {}
  namespaces = {
    'n': namespace
  }

  for prop in root.xpath('n:property', namespaces=namespaces):
    name = prop.xpath('n:name', namespaces=namespaces)[0].text
    value = prop.xpath('n:value', namespaces=namespaces)[0].text
    if name not in seen:
      properties.append({'name': name, 'value': value})
      seen[name] = True

  workflow.job_properties = json.dumps(properties)


def _global_configuration(workflow, root, namespace):
  # root should be global config element.
  namespaces = {
    'n': namespace
  }

  job_xml = root.xpath('n:job-xml', namespaces=namespaces)
  configuration = root.xpath('n:configuration', namespaces=namespaces)
  if job_xml:
    workflow.job_xml = job_xml[0].text
  if configuration:
    _set_properties(workflow, configuration[0], namespace)


def _assign_workflow_properties(workflow, root, namespace):
  namespaces = {
    'n': namespace
  }

  global_config = root.xpath('n:global', namespaces=namespaces)
  if global_config:
    _global_configuration(workflow, global_config[0], namespace)

  LOG.debug("Finished assigning properties to workflow %s" % smart_str(workflow.name))


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
  Note: Unknown elements should throw an error.
  """
  # Iterate over nodes
  for child_el in root:
    # Skip special nodes (like comments).
    if not isinstance(child_el.tag, basestring):
      continue

    # Skip kill nodes.
    if child_el.tag.endswith('kill'):
      continue

    # Skip global configuration.
    if child_el.tag.endswith('global'):
      continue

    # Skip credentials configuration.
    if child_el.tag.endswith('credentials'):
      continue

    tag = etree.QName(child_el).localname
    name = child_el.attrib.get('name', tag)
    LOG.debug("Getting node with data - XML TAG: %(tag)s\tLINK NAME: %(node_name)s\tWORKFLOW NAME: %(workflow_name)s" % {
      'tag': smart_str(tag),
      'node_name': smart_str(name),
      'workflow_name': smart_str(workflow.name)
    })

    # Iterate over node members
    # Join nodes have attributes which point to the next node
    # Start node has attribute which points to first node
    try:
      parent = Node.objects.get(name=name, workflow=workflow).get_full_node()
    except Node.DoesNotExist:
      raise RuntimeError(_('Node with name %s for workflow %s does not exist.') % (name, workflow.name))

    if isinstance(parent, Start):
      _start_relationships(workflow, parent, child_el)

    elif isinstance(parent, Join):
      _join_relationships(workflow, parent, child_el)

    elif isinstance(parent, Decision):
      _decision_relationships(workflow, parent, child_el)

    else:
      _node_relationships(workflow, parent, child_el)

  workflow.end = End.objects.get(workflow=workflow).get_full_node()
  workflow.save()

  _resolve_start_relationships(workflow)
  _resolve_fork_relationships(workflow)
  _resolve_decision_relationships(workflow)

  LOG.debug("Finished resolving links for workflow %s" % smart_str(workflow.name))


def _start_relationships(workflow, parent, child_el):
  """
  Resolve start node links.
  Will always use 'to' link type.
  """
  if 'to' not in child_el.attrib:
    raise RuntimeError(_("Node %s has a link that is missing 'to' attribute.") % parent.name)

  workflow.start = parent
  to = child_el.attrib['to']

  try:
    child = Node.objects.get(workflow=workflow, name=to)
  except Node.DoesNotExist:
    raise RuntimeError(_("Node %s has not been defined.") % to)

  try:
    obj = Link.objects.filter(parent=parent).get(name='to')
    obj.child = child
  except Link.DoesNotExist:
    obj = Link.objects.create(name='to', parent=parent, child=child)
  obj.save()


def _join_relationships(workflow, parent, child_el):
  """
  Resolves join node links.
  Will always use 'to' link type.
  """
  if 'to' not in child_el.attrib:
    raise RuntimeError(_("Node %s has a link that is missing 'to' attribute.") % parent.name)

  to = child_el.attrib['to']

  try:
    child = Node.objects.get(workflow=workflow, name=to)
  except Node.DoesNotExist, e:
    raise RuntimeError(_("Node %s has not been defined.") % to)

  obj = Link.objects.create(name='to', parent=parent, child=child)
  obj.save()


def _decision_relationships(workflow, parent, child_el):
  """
  Resolves the switch statement like nature of decision nodes.
  Will use 'to' link type, except for default case.
  """
  for switch in child_el:
    # Skip special nodes (like comments).
    if not isinstance(switch.tag, basestring):
      continue

    for case in switch:
      # Skip special nodes (like comments).
      if not isinstance(case.tag, basestring):
        continue

      if 'to' not in case.attrib:
        raise RuntimeError(_("Node %s has a link that is missing 'to' attribute.") % parent.name)

      to = case.attrib['to']
      try:
        child = Node.objects.get(workflow=workflow, name=to)
      except Node.DoesNotExist, e:
        raise RuntimeError(_("Node %s has not been defined.") % to)

      if etree.QName(case).localname == 'default':
        name = 'default'
        obj = Link.objects.create(name=name, parent=parent, child=child)

      else:
        name = 'start'
        comment = case.text.strip()
        obj = Link.objects.create(name=name, parent=parent, child=child, comment=comment)

      obj.save()


def _node_relationships(workflow, parent, child_el):
  """
  Resolves node links.
  Will use 'start' link type for fork nodes and 'to' link type for all other nodes.
  Error links will automatically resolve to a single kill node.
  """
  for el in child_el:
    # Skip special nodes (like comments).
    if not isinstance(el.tag, basestring):
      continue

    # Links
    name = etree.QName(el).localname
    if name in LINKS:
      if name == 'path':
        if 'start' not in el.attrib:
          raise RuntimeError(_("Node %s has a link that is missing 'start' attribute.") % parent.name)
        to = el.attrib['start']
        name = 'start'

      else:
        if 'to' not in el.attrib:
          raise RuntimeError(_("Node %s has a link that is missing 'to' attribute.") % parent.name)
        to = el.attrib['to']

      try:
        child = Node.objects.get(workflow=workflow, name=to)
      except Node.DoesNotExist, e:
        if name == 'error':
          child, create = Kill.objects.get_or_create(name='kill', workflow=workflow, node_type=Kill.node_type)
        else:
          raise RuntimeError(_("Node %s has not been defined") % to)

      obj = Link.objects.create(name=name, parent=parent, child=child)
      obj.save()


def _resolve_start_relationships(workflow):
  if not workflow.start:
    raise RuntimeError(_("Workflow start has not been created."))

  if not workflow.end:
    raise RuntimeError(_("Workflow end has not been created."))

  obj = Link.objects.get_or_create(name='related', parent=workflow.start, child=workflow.end)


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
          raise RuntimeError(_('Cannot import workflows that have decision DAG leaf nodes with multiple children or no children.'))
        link = links[0]
        link.child = decision_end
        link.save()

        decision_end_used = True

    # Create link between DecisionEnd and terminal node.
    if decision_end_used and not Link.objects.filter(name='to', parent=decision_end, child=node).exists():
      link = Link(name='to', parent=decision_end, child=node)
      link.save()

  def decision_helper(decision, subgraphs):
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

    children = [_link.child.get_full_node() for _link in decision.get_children_links().exclude(name__in=['error','default'])]

    ends = set()
    for child in children:
      end = helper(child, subgraphs)
      if end:
        ends.add(end)

    # A single end means that we've found a unique end for this decision.
    # Multiple ends mean that we've found a bad decision.
    if len(ends) > 1:
      raise RuntimeError(_('Cannot import workflows that have decisions paths with multiple terminal nodes that converge on a single terminal node.'))
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
          end = decision_helper(end, subgraphs)
          if end:
            return end

        # Can do this because we've replace all its parents with a single DecisionEnd node.
        return helper(end, subgraphs)
      else:
        raise RuntimeError(_('Cannot import workflows that have decisions paths with multiple terminal nodes that converge on a single terminal node.'))
    else:
      raise RuntimeError(_('Cannot import workflows that have decisions paths that never end.'))

    return None

  def helper(node, subgraphs={}):
    """Iterates through nodes, returning ends."""
    if node.name in subgraphs:
      return subgraphs[node.name]

    # Assume receive full node.
    children = [link.child.get_full_node() for link in node.get_children_links().exclude(name__in=['error','default'])]

    # Multiple parents means that we've potentially found an end.
    # Joins will always have more than one parent.
    fan_in_count = len(node.get_parent_links().exclude(name__in=['error','default']))
    if fan_in_count > 1 and not isinstance(node, Join) and not isinstance(node, DecisionEnd):
      return node
    elif isinstance(node, Decision):
      end = decision_helper(node, subgraphs)
      if end:
        # Remember end so we don't have go through checking this path again.
        subgraphs[node.name] = end
        return end
    # In case of fork, should not find different ends.
    elif len(children) > 1:
      end = None
      for child in children:
        temp = helper(child, subgraphs)
        end = end or temp
        if end != temp:
          raise RuntimeError(_('Different ends found in fork.'))
      # Remember end so we don't have go through checking this path again.
      subgraphs[node.name] = end
      return end
    elif children:
      return helper(children.pop(), subgraphs)

    # Likely reached end.
    return None

  if Node.objects.filter(workflow=workflow).filter(node_type=Decision.node_type).exists():
    helper(workflow.start.get_full_node())


def _prepare_nodes(workflow, root):
  """
  Prepare nodes for groking by Django
  - Deserialize
  - Automatically skip undefined nodes.
  """
  objs = serializers.deserialize('xml', etree.tostring(root))

  # First pass is a list of nodes and their types respectively.
  # Must link up nodes with their respective full nodes.
  node = None
  nodes = []
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

      nodes.append(full_node)

  return nodes


def _preprocess_nodes(workflow, transformed_root, workflow_definition_root, nodes, fs=None):
  """
  preprocess nodes
  Sets credentials keys for actions.
  Resolve start name and subworkflow dependencies.
  Looks at path and interrogates all workflows until the proper deployment path is found.
  If the proper deployment path is never found, then
  """

  for action_el in workflow_definition_root:
    if 'cred' in action_el.attrib:
      for full_node in nodes:
        if full_node.name == action_el.attrib['name']:
          full_node.credentials = [{"name": cred, "value": True} for cred in action_el.attrib['cred'].split(',')];

  for full_node in nodes:
    if full_node.node_type is 'start':
      full_node.name = 'start'
    elif full_node.node_type is 'subworkflow':
      app_path = None
      for action_el in workflow_definition_root:
        if 'name' in action_el.attrib and action_el.attrib['name'] == full_node.name:
          for subworkflow_el in action_el:
            if etree.QName(subworkflow_el).localname == 'sub-workflow':
              for property_el in subworkflow_el:
                if etree.QName(property_el).localname == 'app-path':
                  app_path = property_el.text

      if app_path is None:
        LOG.debug("Could not find deployment directory for subworkflow action %s" % full_node.name)
      else:
        LOG.debug("Found deployment directory for subworkflow action %s" % full_node.name)
        subworkflow = _resolve_subworkflow_from_deployment_dir(fs, workflow, app_path)
        if subworkflow:
          LOG.debug("Found workflow %s in deployment directory %s" % (workflow, app_path))
          full_node.sub_workflow = subworkflow
        else:
          LOG.debug("Could not find workflow with deployment directory: %s" % app_path)


def _resolve_subworkflow_from_deployment_dir(fs, workflow, app_path):
  """
  Resolves subworkflow in a subworkflow node
  Looks at path and interrogates all workflows until the proper deployment path is found.
  If the proper deployment path is never found, then
  """
  if not fs:
    raise RuntimeError(_("No hadoop file system to operate on."))

  if app_path.endswith('/'):
    app_path = app_path[:-1]
  if app_path.startswith('hdfs://'):
    app_path = app_path[7:]

  try:
    f = fs.open('%s/workflow.xml' % app_path)
    root = etree.parse(f)
    f.close()
    return Workflow.objects.get(name=root.attrib['name'], owner=workflow.owner, managed=True)
  except IOError:
    pass
  except (KeyError, AttributeError), e:
    raise RuntimeError(_("Could not find workflow name when resolving subworkflow."))
  except Workflow.DoesNotExist, e:
    raise RuntimeError(_("Could not find workflow with name %s extracted from subworkflow path %s") % (root.attrib['name'], app_path))
  except Exception, e:
    raise RuntimeError(_("Could not find workflow at path %s: %s") % (app_path, e))

  for subworkflow in Document.objects.available(Workflow, workflow.owner):
    if subworkflow.deployment_dir == app_path:
      return subworkflow

  return None


def _save_nodes(workflow, nodes):
  """
  Save nodes, but skip kill nodes because we create a single kill node to use.
  """
  for node in nodes:
    if node.node_type is 'kill':
      continue

    try:
      # Do not overwrite start or end node
      Node.objects.get(workflow=workflow, node_type=node.node_type, name=node.name)
    except Node.DoesNotExist:
      node.save()


def _process_metadata(workflow, metadata):
  # Job attributes
  attributes = metadata.setdefault('attributes', {})
  workflow.description = attributes.setdefault('description', workflow.description)
  workflow.deployment_dir = attributes.setdefault('deployment_dir', workflow.deployment_dir)

  # Workflow node attributes
  nodes = metadata.setdefault('nodes', {})
  for node_name in nodes:
    try:
      node = Node.objects.get(name=node_name, workflow=workflow).get_full_node()
      node_attributes = nodes[node_name].setdefault('attributes', {})
      for node_attribute in node_attributes:
        setattr(node, node_attribute, node_attributes[node_attribute])
      node.save()
    except Node.DoesNotExist:
      # @TODO(abe): Log or throw error?
      raise
    except AttributeError:
      # @TODO(abe): Log or throw error?
      # Here there was an attribute reference in the metadata
      # for this node that isn't a member of the node.
      raise


def import_workflow_root(workflow, workflow_definition_root, metadata=None, fs=None):
  try:
    xslt_definition_fh = open("%(xslt_dir)s/workflow.xslt" % {
      'xslt_dir': os.path.join(DEFINITION_XSLT_DIR.get(), 'workflows')
    })

    tag = etree.QName(workflow_definition_root.tag)
    schema_version = tag.namespace

    # Ensure namespace exists
    if schema_version not in OOZIE_NAMESPACES:
      raise RuntimeError(_("Tag with namespace %(namespace)s is not valid. Please use one of the following namespaces: %(namespaces)s") % {
        'namespace': workflow_definition_root.tag,
        'namespaces': ', '.join(OOZIE_NAMESPACES)
      })

    # Get XSLT
    parser = etree.XMLParser(resolve_entities=False)
    xslt = etree.parse(xslt_definition_fh, parser=parser)
    xslt_definition_fh.close()
    transform = etree.XSLT(xslt)

    # Transform XML using XSLT
    transformed_root = transform(workflow_definition_root)

    # Resolve workflow dependencies and node types and link dependencies
    nodes = _prepare_nodes(workflow, transformed_root)
    _preprocess_nodes(workflow, transformed_root, workflow_definition_root, nodes, fs)
    _save_nodes(workflow, nodes)
    _save_links(workflow, workflow_definition_root)
    _assign_workflow_properties(workflow, workflow_definition_root, schema_version)
    if metadata:
      _process_metadata(workflow, metadata)

    # Update workflow attributes
    workflow.schema_version = schema_version
    workflow.name = workflow_definition_root.get('name')
    workflow.save()
  except:
    LOG.exception('failed to import workflow root')
    raise


def import_workflow(workflow, workflow_definition, metadata=None, fs=None):
  # Parse Workflow Definition
  workflow_definition_root = etree.fromstring(workflow_definition)
  if workflow_definition_root is None:
    raise RuntimeError(_("Could not find any nodes in Workflow definition. Maybe it's malformed?"))

  return import_workflow_root(workflow, workflow_definition_root, metadata, fs)


def generate_v2_graph_nodes(workflow_definition):
  # Parse Workflow Definition
  workflow_definition_root = etree.fromstring(workflow_definition)
  if workflow_definition_root is None:
    raise MalformedWfDefException()

  xslt_definition_fh = open("%(xslt_dir)s/workflow.xslt" % {
      'xslt_dir': os.path.join(DEFINITION_XSLT2_DIR.get(), 'workflows')
    })

  tag = etree.QName(workflow_definition_root.tag)
  schema_version = tag.namespace

  # Ensure namespace exists
  if schema_version not in OOZIE_NAMESPACES:
    raise InvalidTagWithNamespaceException(workflow_definition_root.tag)

  # Get XSLT
  parser = etree.XMLParser(resolve_entities=False)
  xslt = etree.parse(xslt_definition_fh, parser=parser)
  xslt_definition_fh.close()
  transform = etree.XSLT(xslt)

  # Transform XML using XSLT
  transformed_root = transform(workflow_definition_root)
  node_list = re.sub('[\s]', '', str(transformed_root))
  node_list = json.loads(node_list)

  return [node for node in node_list if node]



class MalformedWfDefException(Exception):
  pass


class InvalidTagWithNamespaceException(Exception):
  def __init__(self, namespace):
    self.namespace = namespace
    self.namespaces = ', '.join(OOZIE_NAMESPACES)
