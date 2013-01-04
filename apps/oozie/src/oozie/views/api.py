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

from jobsub.models import OozieDesign

from oozie.forms import WorkflowForm, ImportJobsubDesignForm, design_form_by_type
from oozie.import_jobsub import convert_jobsub_design
from oozie.models import Workflow, Node, Mapreduce, Java, Streaming, Link, NODE_TYPES, ACTION_TYPES
from oozie.decorators import check_job_access_permission, check_job_edition_permission
from oozie.utils import model_to_dict


LOG = logging.getLogger(__name__)


JSON_FIELDS = ('parameters', 'job_properties', 'files', 'archives', 'prepares', 'params',
               'deletes', 'mkdirs', 'moves', 'chmods', 'touchzs')
NUMBER_FIELDS = ('sub_workflow',)

def format_field_value(field, value):
  if field in JSON_FIELDS:
    if not isinstance(value, basestring):
      return json.dumps(value)
  if field in NUMBER_FIELDS:
    if not isinstance(value, int):
      return int(value)
  return value


def format_dict_field_values(dictionary):
  for key in dictionary:
    dictionary[key] = format_field_value(key, dictionary[key])
  return dictionary


def workflow_validate_action_json(node_type, node_dict, errors, user, workflow):
  """
  Validates a single action.
  node_type is the node type of the action information passed.
  node_dict is a dictionary describing the node.
  errors is a dictionary that will be populated with any found errors.
  Returns Boolean.
  """
  assert isinstance(errors, dict), "errors must be a dict."
  form_class = design_form_by_type(node_type, user, workflow)
  form = form_class(data=node_dict)

  if form.is_valid():
    for field in form.fields:
      errors[field] = []

    return True

  else:
    for field in form.fields:
      errors[field] = form[field].errors

    return False


def get_or_create_node(workflow, node_data):
  node = None
  id = str(node_data['id'])
  separator_index = id.find(':')

  if separator_index == -1:
    return Node.objects.get(id=id, workflow=workflow).get_full_node()

  node_type = id[0:separator_index]
  node_model = NODE_TYPES.get(node_type, None)
  kwargs = {'workflow': workflow, 'node_type': node_data['node_type']}

  if node_data['node_type'] == 'subworkflow':
    kwargs['sub_workflow'] = Workflow.objects.get(id=int(node_data['sub_workflow']))

  if node_model:
    node = node_model(**kwargs)
  else:
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Could not find node of type'), data=node_data, error_code=500)
  node.save()
  return node


def update_workflow(json_workflow):
  workflow = Workflow.objects.get(id=json_workflow['id'])

  for key in json_workflow:
    if key not in ('nodes', 'start', 'end'):
      setattr(workflow, key, json_workflow[key])

  workflow.save()

  return workflow


def update_workflow_nodes(workflow, json_nodes, id_map, user):
  """Ideally would get objects from form validation instead."""
  for json_node in json_nodes:
    errors = {}
    if json_node['node_type'] in ACTION_TYPES and \
        not workflow_validate_action_json(json_node['node_type'], format_dict_field_values(json_node), errors, user, workflow):
      raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Invalid action'), data={'errors': errors}, error_code=400)

  nodes = []

  for json_node in json_nodes:
    node = get_or_create_node(workflow, json_node)

    if node.node_type == 'fork' and json_node['node_type'] == 'decision':
      node = node.convert_to_decision()

    id_map[str(json_node['id'])] = node.id

    for key in json_node:
      if key not in ('node_ptr', 'child_nodes', 'workflow', 'id', 'sub_workflow'):
        setattr(node, key, format_field_value(key, json_node[key]))

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


@check_job_access_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
@check_job_edition_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
def workflow_validate_action(request, workflow, node_type):
  response = {'status': -1, 'data': {}}

  action_dict = format_dict_field_values(json.loads(str(request.POST.get('node'))))

  if workflow_validate_action_json(node_type, action_dict, response['data'], request.user, workflow):
    response['status'] = 0
  else:
    response['status'] = -1

  return HttpResponse(json.dumps(response), mimetype="application/json")


# Workflow and child links are SPECIAL.
@check_job_access_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
@check_job_edition_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
def workflow_save(request, workflow):
  if request.method != 'POST':
    raise StructuredException(code="METHOD_NOT_ALLOWED_ERROR", message=_('Must be POST request.'), error_code=405)

  json_workflow = format_dict_field_values(json.loads(str(request.POST.get('workflow'))))
  json_workflow.setdefault('schema_version', workflow.schema_version)

  form = WorkflowForm(data=json_workflow)

  if not form.is_valid():
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error saving workflow'), data={'errors': form.errors}, error_code=400)

  json_nodes = json_workflow['nodes']
  id_map = {}

  workflow = update_workflow(json_workflow)
  nodes = update_workflow_nodes(workflow, json_nodes, id_map, request.user)

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
  if request.method != 'GET':
    raise StructuredException(code="METHOD_NOT_ALLOWED_ERROR", message=_('Must be GET request.'), error_code=405)

  return _workflow(request, workflow)


@check_job_access_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
@check_job_edition_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
def workflow_jobsub_actions(request, workflow):
  if request.method not in ['GET', 'POST']:
    raise StructuredException(code="METHOD_NOT_ALLOWED_ERROR", message=_('Must be GET or POST request.'), error_code=405)

  available_actions = OozieDesign.objects.all()
  if request.method == 'POST':
    form = ImportJobsubDesignForm(data=request.POST, choices=[(action.id, action.name) for action in available_actions])
    if form.is_valid():
      try:
        design = OozieDesign.objects.get(id=form.cleaned_data['jobsub_id'])
        action = convert_jobsub_design(design)
        action.workflow = workflow

        response = {
          'status': 0,
          'data': {
            'node': model_to_dict(action)
          }
        }
        response['data']['node']['child_links'] = []
        return HttpResponse(json.dumps(response), mimetype="application/json")
      except OozieDesign.DoesNotExist, e:
        raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Job Designer design does not exist.'), data={'exception': str(e)}, error_code=400)
      except (Mapreduce.DoesNotExist, Streaming.DoesNotExist, Java.DoesNotExist), e:
        raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Could not convert Job Designer design.'), data={'exception': str(e)}, error_code=400)
      except Exception, e:
        raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error importing node from Job Designer'), data={'exception': str(e)}, error_code=400)
    else:
      raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error importing node from Job Designer'), data={'errors': form.errors}, error_code=400)

  else:
    available_actions = OozieDesign.objects.all()
    response = {
      'status': 0,
      'data': {
        'nodes': [model_to_dict(action) for action in available_actions]
      }
    }
    return HttpResponse(json.dumps(response), mimetype="application/json")

