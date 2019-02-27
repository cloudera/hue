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

import logging
import time as py_time

from django.utils.translation import ugettext as _

from desktop import appmanager
from desktop.lib.django_util import render, render_json
from desktop.lib.exceptions import StructuredException
from desktop.lib.exceptions_renderable import PopupException
from desktop.log.access import access_warn
from desktop.models import Document

from oozie.models import Workflow
from oozie.forms import design_form_by_type
from oozie.utils import model_to_dict, format_dict_field_values,\
                        sanitize_node_dict

from desktop.auth.backend import is_admin

LOG = logging.getLogger(__name__)
MAX_DESIGNS = 250


def _list_designs(request, owner, name, order_by='-last_modified'):
  """
  Fetch all workflow designs.
  parameters:
    owner       - Substring filter by owner field
    name        - Substring filter by design name field
    order_by    - Order by string in django ORM format
    is_trashed  - Boolean filter for trash or available
  """
  data = Document.objects.get_docs(request.user, Workflow, extra='jobsub')

  if owner:
      data = data.filter(owner__username__icontains=owner)
  if name:
      data = data.filter(name__icontains=name)
  data = data.order_by(order_by)

  designs = []
  for doc in data[:MAX_DESIGNS]:
    design = doc.content_object

    if design is not None:
      ko_design = {
       'id': design.id,
       'owner': design.owner.username,
       # Design name is validated by workflow and node forms.
       'name': design.name,
       'description': design.description,
       'node_type': design.start.get_child('to').node_type,
       'last_modified': py_time.mktime(design.last_modified.timetuple()),
       'editable': design.owner.id == request.user.id,
       'is_shared': design.is_shared,
       'is_trashed': doc.is_trashed()
      }
      designs.append(ko_design)

  return designs


def list_designs(request):
  '''
  List all workflow designs. Result sorted by last modification time.
  Query params:
    owner       - Substring filter by owner field
    name        - Substring filter by design name field
  '''
  owner = request.GET.get('owner', '')
  name = request.GET.get('name', '')

  if request.is_ajax():
    return render_json({
      'designs': _list_designs(request, owner, name)
    }, js_safe=True)
  else:
    return render("designs.mako", request, {
      'currentuser': request.user,
      'owner': owner,
      'name': name,
      'apps': appmanager.get_apps_dict()
    })

def not_available(request):
  return render("not_available.mako", request, {})

def _get_design(user, design_id):
  """Raise PopupException if design doesn't exist"""
  try:
    return Document.objects.can_read_or_exception(user, Workflow, doc_id=design_id).content_object
  except Workflow.DoesNotExist:
    raise PopupException(_("Workflow not found"))


def _check_permission(request, owner_name, error_msg, allow_root=False):
  """Raise PopupException if user doesn't have permission to modify the design"""
  if request.user.username != owner_name:
    if allow_root and is_admin(request.user):
      return
    access_warn(request, error_msg)
    raise PopupException(_("Permission denied. You are not the owner."))


def delete_design(request, design_id):
  if request.method != 'POST':
    raise StructuredException(code="METHOD_NOT_ALLOWED_ERROR", message=_('Must be POST request.'), error_code=405)

  skip_trash = 'skip_trash' in request.GET

  try:
    workflow = _get_design(request.user, design_id)
    _check_permission(request, workflow.owner.username,
                      _("Access denied: delete design %(id)s.") % {'id': design_id},
                      allow_root=True)
    if skip_trash:
      Workflow.objects.destroy(workflow, request.fs)
    else:
      workflow.delete(skip_trash=False)

  except Workflow.DoesNotExist:
    raise StructuredException(code="NOT_FOUND", message=_('Could not find design %s.') % design_id, error_code=404)

  return render_json({
    'status': 0
  })


def restore_design(request, design_id):
  if request.method != 'POST':
    raise StructuredException(code="METHOD_NOT_ALLOWED_ERROR", message=_('Must be POST request.'), error_code=405)

  try:
    workflow = _get_design(request.user, design_id)
    _check_permission(request, workflow.owner.username,
                      _("Access denied: delete design %(id)s.") % {'id': design_id},
                      allow_root=True)
    workflow.restore()

  except Workflow.DoesNotExist:
    LOG.error("Trying to restore non-existent workflow (id %s)" % (design_id,))
    raise StructuredException(code="NOT_FOUND", message=_('Could not find design %s.') % design_id, error_code=404)

  return render_json({
    'status': 0
  })


def get_design(request, design_id):
  workflow = _get_design(request.user, design_id)

  node = workflow.start.get_child('to')
  node_dict = model_to_dict(node)
  node_dict['id'] = design_id
  node_dict['is_shared'] = workflow.is_shared
  node_dict['editable'] = workflow.owner.id == request.user.id
  node_dict['parameters'] = workflow.parameters
  node_dict['description'] = workflow.description

  return render_json(node_dict, js_safe=True)


def save_design(request, design_id):
  workflow = _get_design(request.user, design_id)
  _check_permission(request, workflow.owner.username, _("Access denied: edit design %(id)s.") % {'id': workflow.id})

  ActionForm = design_form_by_type(request.POST.get('node_type', None), request.user, workflow)
  form = ActionForm(request.POST)

  if not form.is_valid():
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error saving design'), data={'errors': form.errors}, error_code=400)

  data = format_dict_field_values(request.POST.copy())
  _save_design(request.user, design_id, data)

  return get_design(request, design_id);


def _save_design(user, design_id, data):
  sanitize_node_dict(data)
  workflow = _get_design(user, design_id)

  workflow.name = data['name']
  workflow.description = data.setdefault('description', '')
  workflow.is_shared = str(data.setdefault('is_shared', 'true')).lower() == "true"
  workflow.parameters = data.setdefault('parameters', '[]')
  node = workflow.start.get_child('to').get_full_node()
  node_id = node.id

  for key in data:
    if key in ('is_shared', 'capture_output', 'propagate_configuration'):
      setattr(node, key, str(data[key]).lower() == 'true')
    else:
      setattr(node, key, data[key])

  node.id = node_id
  node.pk = node_id
  node.save()

  workflow.save()

  if workflow.doc.exists():
    workflow.doc.update(name=workflow.name, description=workflow.description)


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

  # Action form validates name and description.
  workflow.name = request.POST.get('name')
  workflow.description = request.POST.get('description')
  workflow.save()

  doc = workflow.doc.get()
  doc.extra = 'jobsub'
  doc.save()

  # Save design again to update all fields.
  data = format_dict_field_values(request.POST.copy())
  _save_design(request.user, workflow.id, data)

  return get_design(request, workflow.id)


def clone_design(request, design_id):
  if request.method != 'POST':
    raise StructuredException(code="METHOD_NOT_ALLOWED_ERROR", message=_('Must be a POST request.'), error_code=405)

  workflow = _get_design(request.user, design_id)
  clone = workflow.clone(request.fs, request.user)
  doc = clone.doc.get()
  doc.extra = 'jobsub'
  doc.save()
  cloned_action = clone.start.get_child('to')
  cloned_action.name = clone.name
  cloned_action.save()

  return get_design(request, clone.id)
