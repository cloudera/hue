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
import logging
import re
import sys

from django.http import Http404
from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions import StructuredException
from desktop.lib.i18n import force_unicode
from desktop.models import Document

from oozie.forms import WorkflowForm, NodeForm, design_form_by_type
from oozie.models import Workflow, Node, Start, End, Kill,\
                         Link, Decision, Fork, DecisionEnd, Join,\
                         NODE_TYPES, ACTION_TYPES, _STD_PROPERTIES
from oozie.decorators import check_job_access_permission, check_job_edition_permission
from oozie.utils import model_to_dict, format_dict_field_values, format_field_value


LOG = logging.getLogger(__name__)


try:
  from jobbrowser.views import job_single_logs
  from jobbrowser.models import LinkJobLogs
except:
  LOG.warn('Oozie is not enabled')


def error_handler(view_fn):
  def decorator(request, *args, **kwargs):
    try:
      return view_fn(request, *args, **kwargs)
    except Http404, e:
      raise e
    except StructuredException, e:
      error_code = e.error_code
      message = e.message
      details = e.data or {}
    except Exception, e:
      LOG.exception('error in %s' % view_fn)

      error_code = 500
      details = {}
      (type, value, tb) = sys.exc_info()
      if not hasattr(e, 'message') or not e.message:
        message = str(e)
      else:
        message = force_unicode(e.message, strings_only=True, errors='replace')

    response = {
      'status': 1,
      'message': message,
      'details': details
    }

    return JsonResponse(response, status=error_code)
  return decorator


def get_or_create_node(workflow, node_data, save=True):
  node = None
  id = str(node_data['id'])
  separator_index = id.find(':')

  if separator_index == -1:
    return Node.objects.get(id=id, workflow=workflow).get_full_node()

  node_type = id[0:separator_index]
  node_model = NODE_TYPES.get(node_type, None)
  kwargs = {'workflow': workflow, 'node_type': node_data['node_type']}

  if node_model:
    node = node_model(**kwargs)
  else:
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Could not find node of type'), data=node_data, error_code=500)

  if save:
    node.save()

  return node


def _validate_node_links_json(node_type, node_links, errors):
  """
  Validate a single node's links.
  node_type is the node type of the action information passed.
  node_links is list of dictionaries describing the links.
  errors is a dictionary that will be populated with any found errors.
  """
  assert isinstance(errors, dict), "errors must be a dict."
  if not isinstance(node_links, list):
    errors['links'] = _("links must be a list")
    return False

  # Check link counts are accurate.
  if node_type == Start.node_type:
    if len(node_links) != 2:
      errors['links'] = _("Start should have two children: 'related' to end, 'to' to any node but an end.")
      return False
  elif node_type == End.node_type:
    if len(node_links) != 0:
      errors['links'] = _("End should have no children.")
      return False
  elif node_type == Kill.node_type:
    if len(node_links) != 0:
      errors['links'] = _("Kill should have no children.")
      return False
  elif node_type in (Join.node_type, DecisionEnd.node_type):
    if len(node_links) != 1:
      errors['links'] = _("Join and Decision End should have one child: 'to' to any node.")
      return False
  elif node_type in (Fork.node_type, Decision.node_type):
    if len(node_links) < 2:
      errors['links'] = _("Fork and Decision should have at least two children: 'related' to their respective ends, 'start' to any node.")
      return False
  else:
    if len(node_links) != 2:
      errors['links'] = _("Actions should have two children: 'error' to kill, 'ok' to any node.")
      return False

  # Check if link types are okay.
  link_names_by_node_type = {
    'start': {'related': 1, 'to': 1},
    'end': {},
    'kill': {},
    'fork': {'related': 1, 'start': 2},
    'join': {'to': 1},
    'decision': {'related': 1, 'start': 2},
    'decisionend': {'to': 1},
    None: {'ok': 1, 'error': 1},
  }
  link_types = link_names_by_node_type.get(node_type, link_names_by_node_type[None])
  for link in node_links:
    link_name = link.get('name', None)
    if link_name in link_types:
      link_types[link_name] -= 1

  for link_type in link_types:
    if link_types[link_type] > 0:
      errors['links'] = _('%(node_type)s should have %(count)d more %(link_type)s link' % {
        'node_type': node_type,
        'count': link_types[link_type],
        'link_type': link_type
      })
      return False

  return True


def _validate_node_json(node_type, node_dict, errors, user, workflow):
  """
  Validates a single node excluding links.
  node_type is the node type of the action information passed.
  node_dict is a dictionary describing the node.
  errors is a dictionary that will be populated with any found errors.
  user is a User object that is associated with the node_type. Only needed for Subworkflow node.
  workflow is the Workflow object associated with the node. Only needed for Subworkflow node.
  Returns Boolean.
  """
  assert isinstance(errors, dict), "errors must be a dict."
  if node_type in ACTION_TYPES:
    form_class = design_form_by_type(node_type, user, workflow)
  else:
    form_class = NodeForm
  form = form_class(data=node_dict)

  if form.is_valid():
    for field in form.fields:
      errors[field] = []

    return True

  else:
    for field in form.fields:
      errors[field] = form[field].errors

    return False


def _validate_nodes_json(json_nodes, errors, user, workflow):
  """
  Validates every node and link in the workflow.
  node_type is the node type of the action information passed.
  node_dict is a dictionary describing the node.
  errors is a dictionary that will be populated with any found errors.
  user is a User object that is associated with the node_type. Only needed for Subworkflow node.
  workflow is the Workflow object associated with the node. Only needed for Subworkflow node.
  Returns Boolean.
  """
  assert isinstance(errors, dict), "errors must be a dict."
  result = True

  for node in json_nodes:
    _errors = {}
    node_dict = format_dict_field_values(node)
    if node['node_type'] in ACTION_TYPES:
      node_result = _validate_node_json(node['node_type'], node_dict, _errors, user, workflow)
    else:
      node_result = True
    link_result = _validate_node_links_json(node['node_type'], node_dict['child_links'], _errors)
    result = result and node_result and link_result
    if not node.has_key('name') and ( not node.has_key('node_type') or not node.has_key('id') ):
      raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error saving workflow'), data={'errors': 'Node is missing a name.'}, error_code=400)
    errors[node.get('name', '%s-%s' % ( node.get('node_type'), node.get('id')))] = _errors

  return result


def _update_workflow_nodes_json(workflow, json_nodes, id_map, user):
  """Ideally would get objects from form validation instead."""
  nodes = []

  for json_node in json_nodes:
    node = get_or_create_node(workflow, json_node, save=False)

    if node.node_type == 'subworkflow':
      try:
        node.sub_workflow = Workflow.objects.get(id=int(json_node['sub_workflow']))
      except TypeError:
        # sub_workflow is None
        node.sub_workflow = None
      except Workflow.DoesNotExist:
        raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error saving workflow'), data={'errors': 'Chosen subworkflow does not exist.'}, error_code=400)
    elif node.node_type == 'fork' and json_node['node_type'] == 'decision':
      node.save() # Need to save in case database throws error when performing delete.
      node = node.convert_to_decision()
    node.save()

    id_map[str(json_node['id'])] = node.id

    for key in json_node:
      if key == 'data':
        if isinstance(json_node[key], basestring):
          node.data = json_node[key]
        else:
          node.data = json.dumps(json_node[key])
      elif key not in ('node_ptr', 'child_nodes', 'workflow', 'id', 'sub_workflow'):
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


def _update_workflow_json(json_workflow):
  workflow = Workflow.objects.get(id=json_workflow['id'])
  for key in json_workflow:
    if key == 'data':
      if isinstance(json_workflow[key], basestring):
        workflow.data = json_workflow[key]
      else:
        workflow.data = json.dumps(json_workflow[key])
    elif key not in ('nodes', 'start', 'end', 'job_ptr', 'owner'):
      setattr(workflow, key, json_workflow[key])

  workflow.save()
  workflow.doc.update(name=workflow.name, description=workflow.description)
  return workflow


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
  return JsonResponse(response)


@error_handler
@check_job_access_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
@check_job_edition_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
def workflow_validate_node(request, workflow, node_type):
  response = {'status': -1, 'data': {}}

  node_dict = format_dict_field_values(json.loads(request.POST.get('node')))

  if _validate_node_json(node_type, node_dict, response['data'], request.user, workflow):
    response['status'] = 0
  else:
    response['status'] = -1

  return JsonResponse(response)


# Workflow and child links are SPECIAL.
@error_handler
@check_job_access_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
@check_job_edition_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
def workflow_save(request, workflow):
  if request.method != 'POST':
    raise StructuredException(code="METHOD_NOT_ALLOWED_ERROR", message=_('Must be POST request.'), error_code=405)

  json_workflow = format_dict_field_values(json.loads(request.POST.get('workflow')))
  json_workflow.setdefault('schema_version', workflow.schema_version)

  form = WorkflowForm(data=json_workflow)

  if not form.is_valid():
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error saving workflow'), data={'errors': form.errors}, error_code=400)

  json_nodes = json_workflow['nodes']
  id_map = {}
  errors = {}

  if not _validate_nodes_json(json_nodes, errors, request.user, workflow):
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error saving workflow'), data={'errors': errors}, error_code=400)

  workflow = _update_workflow_json(json_workflow)
  nodes = _update_workflow_nodes_json(workflow, json_nodes, id_map, request.user)

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


@error_handler
@check_job_access_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
def workflow(request, workflow):
  if request.method != 'GET':
    raise StructuredException(code="METHOD_NOT_ALLOWED_ERROR", message=_('Must be GET request.'), error_code=405)

  return _workflow(request, workflow)


@error_handler
@check_job_access_permission(exception_class=(lambda x: StructuredException(code="UNAUTHORIZED_REQUEST_ERROR", message=x, data=None, error_code=401)))
def workflow_actions(request, workflow):
  if request.method != 'GET':
    raise StructuredException(code="METHOD_NOT_ALLOWED_ERROR", message=_('Must be GET request.'), error_code=405)

  action_list = [action.get_full_node() for action in workflow.actions]
  response = {
    'status': 0,
    'data': {
      'actions': [model_to_dict(action) for action in action_list]
    }
  }
  return JsonResponse(response)


@error_handler
def workflows(request):
  if request.method not in ['GET']:
    raise StructuredException(code="METHOD_NOT_ALLOWED_ERROR", message=_('Must be GET request.'), error_code=405)

  if request.GET.get('managed', 'false').lower() == 'false':
    extra='jobsub'
  else:
    extra=''

  workflow_docs = Document.objects.get_docs(request.user, Workflow, extra=extra)

  response = {
    'status': 0,
    'data': {
      'workflows': [model_to_dict(workflow.content_object) for workflow in workflow_docs]
    }
  }

  return JsonResponse(response)


def autocomplete_properties(request):
  return JsonResponse({ 'properties': _STD_PROPERTIES })


@error_handler
def get_log(request, oozie_workflow, make_links=True, log_start_pattern=None, log_end_pattern=None):
  logs = {}
  is_really_done = False

  for action in oozie_workflow.get_working_actions():
    try:
      if action.externalId:
        data = job_single_logs(request, **{'job': action.externalId})

        if data and 'logs' in data:
          action_logs = data['logs'][1]

          if log_start_pattern:
            re_log_start = re.compile(log_start_pattern, re.M | re.DOTALL)
            if re_log_start.search(action_logs):
              action_logs = re.search(re_log_start, action_logs).group(1).strip()
            else:
              LOG.debug('Failed to find given start log pattern in logs: %s' % log_start_pattern)

          if log_end_pattern:
            re_log_end = re.compile(log_end_pattern)
            is_really_done = re_log_end.search(action_logs) is not None or oozie_workflow.status == 'KILLED'
            if is_really_done and not action_logs:
              LOG.warn('Unable to scrape full logs, try increasing the jobbrowser log_offset configuration value.')

          if make_links:
            action_logs = LinkJobLogs._make_links(action_logs)

          logs[action.name] = action_logs

    except Exception:
      LOG.exception('An error occurred while watching the job running')
      is_really_done = True

  workflow_actions = _get_workflow_actions(oozie_workflow, logs, is_really_done)

  return logs, workflow_actions, is_really_done


def _get_workflow_actions(oozie_workflow, logs, is_really_done=False):
  workflow_actions = []

  # Return metadata for workflow actions (required for Pig)
  for action in oozie_workflow.get_working_actions():
    progress = _get_progress(oozie_workflow, logs.get(action.name, ''))
    appendable = {
      'name': action.name,
      'status': action.status,
      'logs': logs.get(action.name, ''),
      'isReallyDone': is_really_done,
      'progress': progress,
      'progressPercent': '%d%%' % progress,
      'absoluteUrl': oozie_workflow.get_absolute_url(),
    }
    workflow_actions.append(appendable)

  return workflow_actions


def _get_progress(job, log):
  if job.status in ('SUCCEEDED', 'KILLED', 'FAILED'):
    return 100
  else:
    try:
      return int(re.findall("MapReduceLauncher  - (1?\d?\d)% complete", log)[-1])
    except:
      return 0
