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

try:
  import json
except ImportError:
  import simplejson as json
import logging

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from desktop.lib.exceptions import StructuredException

from oozie.models import Workflow, Node, Link, NODE_TYPES, ACTION_TYPES
from oozie.decorators import check_job_access_permission, check_job_edition_permission
from oozie.utils import model_to_dict


LOG = logging.getLogger(__name__)


def validate_json_node(json):
  assert 'id' in json, "Member 'id' not in node."
  assert 'node_type' in json, "Member 'node_type' not in node."
  if json['node_type'] in ACTION_TYPES.keys():
    assert 'name' in json, "Member 'name' not in node."
    # assert 'description' in json, "Member 'description' not in node."
  if 'child_links' not in json:
    raise AssertionError("Member 'child_links' is missing.")

  validate_json_links(json['child_links'])


def validate_json_nodes(json):
  if not isinstance(json, list):
    raise AssertionError("Member 'nodes' is not a list.")

  for node in json:
    validate_json_node(node)


def validate_json_link(json):
  assert 'name' in json, "Member 'name' not in link."
  assert 'comment' in json, "Member 'comment' not in link."
  assert 'parent' in json, "Member 'parent' not in link."
  assert 'child' in json, "Member 'child' not in link."


def validate_json_links(json):
  if not isinstance(json, list):
    raise AssertionError("Member 'child_links' is not a list.")

  for node in json:
    validate_json_link(node)


def validate_json_workflow(json):
  assert 'name' in json, "Member 'name' not in link."
  assert 'description' in json, "Member 'description' not in link."
  assert 'job_properties' in json, "Member 'job_properties' not in link."
  assert 'parameters' in json, "Member 'parameters' not in link."
  assert 'is_shared' in json, "Member 'is_shared' not in link."
  assert 'job_xml' in json, "Member 'job_xml' not in link."
  assert 'deployment_dir' in json, "Member 'deployment_dir' not in link."

  if 'nodes' not in json:
    raise AssertionError(_("Member 'nodes' is missing."))

  validate_json_nodes(json['nodes'])


def get_or_create_node(workflow, node_data):
  node = None
  id = str(node_data['id'])
  separator_index = id.find(':')

  if separator_index == -1:
    return Node.objects.get(id=id, workflow=workflow).get_full_node()

  node_type = id[0:separator_index]
  node_model = NODE_TYPES.get(node_type, None)
  if node_model:
    node = node_model(workflow=workflow, node_type=node_data['node_type'])
  else:
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Could not find node of type'), data=node_data, error_code=500)
  node.save()
  return node


def update_workflow(json_workflow):
  workflow = Workflow.objects.get(id=json_workflow['id'])

  for key in json_workflow:
    if key not in ('nodes', 'start', 'end'):
      if key in ('parameters', 'job_properties', 'files', 'archives', 'prepares', 'params'):
        setattr(workflow, key, json.dumps(json_workflow[key]))
      else:
        setattr(workflow, key, json_workflow[key])

  workflow.save()

  return workflow


def update_workflow_nodes(workflow, json_nodes, id_map):
  validate_json_nodes(json_nodes)

  nodes = []

  for json_node in json_nodes:
    node = get_or_create_node(workflow, json_node)
    if node.node_type == 'fork' and json_node['node_type'] == 'decision':
      node = node.convert_to_decision()

    id_map[str(json_node['id'])] = node.id

    for key in json_node:
      if key not in ('node_ptr', 'child_nodes', 'workflow', 'id'):
        if key in ('parameters', 'job_properties', 'files', 'archives', 'prepares', 'params'):
          if isinstance(json_node[key], basestring):
            setattr(node, key, json_node[key])
          else:
            setattr(node, key, json.dumps(json_node[key]))
        else:
          setattr(node, key, json_node[key])

    node.workflow = workflow
    node.save()

    # Keep track of nodes in order of received list
    # so that we may iterate over them again in the same order
    # when we handle links
    nodes.append(node)

  # Delete unused nodes from workflow
  old_nodes = Node.objects.filter(workflow=workflow).exclude(id__in=map(lambda x: x.id, nodes))
  for node in old_nodes:
    node.get_full_node().delete()

  return nodes


# Workflow and child links are SPECIAL.
@check_job_access_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
@check_job_edition_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
def workflow_save(request, workflow):
  json_workflow = json.loads(str(request.POST.get('workflow')))

  try:
    validate_json_workflow(json_workflow)
  except AssertionError, e:
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error saving workflow'), data={'more': str(e)}, error_code=400)

  json_nodes = json_workflow['nodes']
  id_map = {}

  workflow = update_workflow(json_workflow)
  nodes = update_workflow_nodes(workflow, json_nodes, id_map)

  # Update links
  index = 0
  for json_node in json_nodes:
    child_links = json_node['child_links']
    Link.objects.filter(parent=nodes[index]).delete()

    for child_link in child_links:
      link = Link()
      link.id = getattr(child_link, 'id', None)
      link.name = child_link['name']

      id = str(child_link['parent'])
      link.parent = Node.objects.get(id=id_map[id])

      id = str(child_link['child'])
      link.child = Node.objects.get(id=id_map[id])

      link.comment = child_link.get('comment', '')

      link.save()

    index += 1

  # Make sure workflow HDFS permissions are correct
  Workflow.objects.check_workspace(workflow, request.fs)

  return _workflow(request, workflow=workflow)


def _workflow(request, workflow):
  response = {'status': -1, 'data': 'None'}

  workflow_dict = model_to_dict(workflow)
  node_list = [node.get_full_node() for node in workflow.node_list]
  nodes = [model_to_dict(node) for node in node_list]

  for index in range(0, len(node_list)):
    nodes[index]['child_links'] = [model_to_dict(link) for link in node_list[index].get_all_children_links()]

  workflow_dict['nodes'] = nodes

  response['status'] = 0
  response['data'] = workflow_dict
  return HttpResponse(json.dumps(response), mimetype="application/json")


@check_job_access_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
def workflow(request, workflow):
  return _workflow(request, workflow)
