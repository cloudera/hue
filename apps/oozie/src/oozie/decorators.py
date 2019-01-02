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

from django.utils.functional import wraps
from django.utils.translation import ugettext as _

from desktop.conf import USE_NEW_EDITOR
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document, Document2

from oozie.models import Job, Node, Dataset

from desktop.auth.backend import is_admin


LOG = logging.getLogger(__name__)


def check_document_access_permission():
  def inner(view_func):
    def decorate(request, *args, **kwargs):
      doc_id = uuid = doc2 = None

      try:
        if request.GET.get('workflow'):
          workflow_id = request.GET.get('workflow')
          if workflow_id.isdigit():
            doc_id = workflow_id
          else:
            uuid = workflow_id
        elif request.GET.get('uuid'):
          uuid = request.GET.get('uuid')
        elif request.GET.get('coordinator'):
          doc_id = request.GET.get('coordinator')
        elif request.GET.get('bundle'):
          doc_id = request.GET.get('bundle')
        elif 'doc_id' in kwargs:
          doc_id = kwargs['doc_id']

        if doc_id and not doc_id.isdigit():
          uuid = doc_id
          doc_id = None

        if doc_id is not None:
          doc2 = Document2.objects.get(id=doc_id)
        elif uuid is not None:
          # TODO: The commented line should be used once we fully transition to doc2
          # doc2 = Document2.objects.get_by_uuid(user=request.user, uuid=uuid, perm_type=None)
          doc2 = Document2.objects.filter(uuid=uuid).order_by('-last_modified').first()

        if doc2:
          if USE_NEW_EDITOR.get():
            doc2.can_read_or_exception(request.user)
          else:
            doc2.doc.get().can_read_or_exception(request.user)
      except Document2.DoesNotExist:
        raise PopupException(_('Job with %(key)s=%(value)s does not exist') %
                             {'key': 'id' if doc_id else 'uuid', 'value': doc_id or uuid})

      return view_func(request, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner


def check_document_modify_permission():
  def inner(view_func):
    def decorate(request, *args, **kwargs):
      doc_id = None

      job = json.loads(request.POST.get('workflow', '{}'))
      if not job:
        job = json.loads(request.POST.get('coordinator', '{}'))
      elif not job:
        job = json.loads(request.POST.get('bundle', '{}'))

      if job and job.get('id'):
        doc_id = job.get('id')

        try:
          doc2 = Document2.objects.get(id=job['id'])
          if USE_NEW_EDITOR.get():
              doc2.can_write_or_exception(request.user)
          else:
              doc2.doc.get().can_write_or_exception(request.user)
        except Document.DoesNotExist:
          raise PopupException(_('Job %(id)s does not exist') % {'id': doc_id})

      return view_func(request, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner


def check_editor_access_permission(view_func):

  def decorate(request, *args, **kwargs):
    if not is_admin(request.user) and request.user.has_hue_permission(action="disable_editor_access", app="oozie"):
      raise PopupException(_('Missing permission to access the Oozie Editor'), error_code=401)
    return view_func(request, *args, **kwargs)
  return wraps(view_func)(decorate)


## Oozie v1 below


def check_job_access_permission(exception_class=PopupException):
  """
  Decorator ensuring that the user has access to the workflow or coordinator.

  Arg: 'workflow' or 'coordinator' id.
  Return: the workflow of coordinator or raise an exception

  Notice: its gets an id in input and returns the full object in output (not an id).
  """
  def inner(view_func):
    def decorate(request, *args, **kwargs):
      if 'workflow' in kwargs:
        job_type = 'workflow'
      elif 'coordinator' in kwargs:
        job_type = 'coordinator'
      else:
        job_type = 'bundle'

      job = kwargs.get(job_type)
      if job is not None:
        job = Job.objects.can_read_or_exception(request, job, exception_class=exception_class)
      kwargs[job_type] = job

      return view_func(request, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner


def check_job_edition_permission(authorize_get=False, exception_class=PopupException):
  """
  Decorator ensuring that the user has the permissions to modify a workflow or coordinator.

  Need to appear below @check_job_access_permission
  """
  def inner(view_func):
    def decorate(request, *args, **kwargs):
      if 'workflow' in kwargs:
        job_type = 'workflow'
      elif 'coordinator' in kwargs:
        job_type = 'coordinator'
      else:
        job_type = 'bundle'

      job = kwargs.get(job_type)
      if job is not None and not (authorize_get and request.method == 'GET'):
        Job.objects.can_edit_or_exception(request, job, exception_class=exception_class)

      return view_func(request, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner


def check_action_access_permission(view_func):
  """
  Decorator ensuring that the user has access to the workflow action.

  Arg: 'workflow action' id.
  Return: the workflow action or raise an exception

  Notice: its gets an id in input and returns the full object in output (not an id).
  """
  def decorate(request, *args, **kwargs):
    action_id = kwargs.get('action')
    action = Node.objects.get(id=action_id).get_full_node()
    Job.objects.can_read_or_exception(request, action.workflow.id)
    kwargs['action'] = action

    return view_func(request, *args, **kwargs)
  return wraps(view_func)(decorate)


def check_action_edition_permission(view_func):
  """
  Decorator ensuring that the user has the permissions to modify a workflow action.

  Need to appear below @check_action_access_permission
  """
  def decorate(request, *args, **kwargs):
    action = kwargs.get('action')
    Job.objects.can_edit_or_exception(request, action.workflow)

    return view_func(request, *args, **kwargs)
  return wraps(view_func)(decorate)


def check_dataset_access_permission(view_func):
  """
  Decorator ensuring that the user has access to dataset.

  Arg: 'dataset'.
  Return: the dataset or raise an exception

  Notice: its gets an id in input and returns the full object in output (not an id).
  """
  def decorate(request, *args, **kwargs):
    dataset = kwargs.get('dataset')
    if dataset is not None:
      dataset = Dataset.objects.can_read_or_exception(request, dataset)
    kwargs['dataset'] = dataset

    return view_func(request, *args, **kwargs)
  return wraps(view_func)(decorate)


def check_dataset_edition_permission(authorize_get=False):
  """
  Decorator ensuring that the user has the permissions to modify a dataset.
  A dataset can be edited if the coordinator that owns the dataset can be edited.

  Need to appear below @check_dataset_access_permission
  """
  def inner(view_func):
    def decorate(request, *args, **kwargs):
      dataset = kwargs.get('dataset')
      if dataset is not None and not (authorize_get and request.method == 'GET'):
        Job.objects.can_edit_or_exception(request, dataset.coordinator)

      return view_func(request, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner
