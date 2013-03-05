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
Views for JobSubmission.

The typical workflow has a user creating a "job design".
Existing job designs can also be edited and listed.
To "run" the job design, it must be parameterized, and submitted
to the cluster.  A parameterized, submitted job design
is a "job submission".  Submissions can be "watched".
"""

try:
  import json
except ImportError:
  import simplejson as json
import logging
import time as py_time

from django.core import urlresolvers
from django.shortcuts import redirect
from django.template.defaultfilters import escapejs
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render, render_json, extract_field_data
from desktop.lib.exceptions import StructuredException
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import RestException
from desktop.log.access import access_warn

from hadoop.fs.exceptions import WebHdfsException
from liboozie.oozie_api import get_oozie

from oozie.models import Workflow
from oozie.forms import design_form_by_type
from oozie.utils import model_to_dict, format_dict_field_values, format_field_value,\
                        sanitize_node_dict, JSON_FIELDS

from jobsub.management.commands import jobsub_setup


LOG = logging.getLogger(__name__)

SKIP_ESCAPE = ('name', 'owner')

def list_designs(request):
  '''
  List all workflow designs. Result sorted by last modification time.
  Query params:
    owner       - Substring filter by owner field
    name        - Substring filter by design name field
  '''
  data = Workflow.objects.filter(managed=False)
  owner = request.GET.get('owner', '')
  name = request.GET.get('name', '')
  if owner:
      data = data.filter(owner__username__icontains=owner)
  if name:
      data = data.filter(name__icontains=name)
  data = data.order_by('-last_modified')

  designs = []
  for design in data:
      ko_design = {
          'id': design.id,
          'owner': design.owner.username,
          # Design name is validated by workflow and node forms.
          'name': design.name,
          'description': escapejs(design.description),
          'node_type': design.start.get_child('to').node_type,
          'last_modified': py_time.mktime(design.last_modified.timetuple()),
          'editable': design.owner.id == request.user.id
      }
      designs.append(ko_design)

  if request.is_ajax():
    return render_json(designs)
  else:
    return render("designs.mako", request, {
      'currentuser': request.user,
      'owner': owner,
      'name': name
    })

def _get_design(design_id):
  """Raise PopupException if design doesn't exist"""
  try:
    return Workflow.objects.get(pk=design_id)
  except Workflow.DoesNotExist:
    raise PopupException(_("Workflow not found"))

def _check_permission(request, owner_name, error_msg, allow_root=False):
  """Raise PopupException if user doesn't have permission to modify the design"""
  if request.user.username != owner_name:
    if allow_root and request.user.is_superuser:
      return
    access_warn(request, error_msg)
    raise PopupException(_("Permission denied. You are not the owner."))

def delete_design(request, design_id):
  if request.method != 'POST':
    raise StructuredException(code="METHOD_NOT_ALLOWED_ERROR", message=_('Must be POST request.'), error_code=405)

  try:
    workflow = _get_design(design_id)
    _check_permission(request, workflow.owner.username,
                      _("Access denied: delete workflow %(id)s.") % {'id': design_id},
                      allow_root=True)
    Workflow.objects.destroy(workflow, request.fs)

  except Workflow.DoesNotExist:
    LOG.error("Trying to delete non-existent workflow (id %s)" % (design_id,))
    raise StructuredException(code="NOT_FOUND", message=_('Could not find design.'), error_code=404)

  return render_json({})


def get_design(request, design_id):
  workflow = _get_design(design_id)
  node = workflow.start.get_child('to')
  node_dict = model_to_dict(node)
  node_dict['id'] = design_id
  for key in node_dict:
    if key not in JSON_FIELDS:
      if key not in SKIP_ESCAPE:
        node_dict[key] = escapejs(node_dict[key])
  node_dict['editable'] = workflow.owner.id == request.user.id
  return render_json(node_dict);


def save_design(request, design_id):
  workflow = _get_design(design_id)
  _check_permission(request, workflow.owner.username, _("Access denied: edit design %(id)s.") % {'id': workflow.id})

  ActionForm = design_form_by_type(request.POST.get('node_type', None), request.user, workflow)
  form = ActionForm(request.POST)

  if not form.is_valid():
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error saving design'), data={'errors': form.errors}, error_code=400)

  data = format_dict_field_values(request.POST.copy())
  sanitize_node_dict(data)
  workflow.name = data['name']
  workflow.description = data['description']
  node = workflow.start.get_child('to').get_full_node()
  node_id = node.id
  for key in data:
    setattr(node, key, data[key])
  node.id = node_id
  node.pk = node_id
  node.save()
  workflow.save()

  data['id'] = workflow.id
  return render_json(data);


def new_design(request, node_type):
  """
  Designs are the interpolation of Workflows and a single action.
  Save ``name`` and ``description`` of workflows.
  Also, use ``id`` of workflows.
  """
  if request.method != 'POST':
    raise StructuredException(code="METHOD_NOT_ALLOWED_ERROR", message=_('Must be POST request.'), error_code=405)

  workflow = Workflow.objects.new_workflow(request.user)
  ActionForm = design_form_by_type(node_type, request.user, workflow)
  form = ActionForm(request.POST)

  if not form.is_valid():
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error saving design'), data={'errors': form.errors}, error_code=400)

  workflow.managed = False
  # Every one should be able to execute and clone a design.
  workflow.is_shared = True
  workflow.save()
  Workflow.objects.initialize(workflow, request.fs)
  action = form.save(commit=False)
  action.workflow = workflow
  action.node_type = node_type
  action.save()
  workflow.start.add_node(action)
  action.add_node(workflow.end)
  workflow.name = request.POST.get('name')
  workflow.description = request.POST.get('description')
  workflow.save()

  data = format_dict_field_values(request.POST.copy())
  data['id'] = workflow.id
  return render_json(data)


def clone_design(request, design_id):
  if request.method != 'POST':
    raise StructuredException(code="METHOD_NOT_ALLOWED_ERROR", message=_('Must be POST request.'), error_code=405)

  workflow = _get_design(design_id)
  clone = workflow.clone(request.fs, request.user)
  cloned_action = clone.start.get_child('to')
  cloned_action.name = clone.name
  cloned_action.save()

  return get_design(request, clone.id)


def jasmine(request):
  return render('jasmine.mako', request, None)
