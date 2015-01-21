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

from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document, Document2

from oozie.models import Job, Node, Dataset


LOG = logging.getLogger(__name__)


def check_document_access_permission():
  def inner(view_func):
    def decorate(request, *args, **kwargs):
      doc_id = {}

      try:
        if request.GET.get('workflow') or request.POST.get('workflow'):
          workflow_id = request.GET.get('workflow') or request.POST.get('workflow')
          if workflow_id.isdigit():
            doc_id['id'] = workflow_id
          else:
            doc_id['uuid'] = workflow_id
        elif request.GET.get('uuid'):
          doc_id['uuid'] = request.GET.get('uuid')
        elif request.GET.get('coordinator'):
          doc_id['id'] = request.GET.get('coordinator')
        elif request.GET.get('bundle'):
          doc_id['id'] = request.GET.get('bundle')
        elif 'doc_id' in kwargs:
          doc_id['id'] = kwargs['doc_id']

        if doc_id:
          doc2 = Document2.objects.get(**doc_id)
          doc2.doc.get().can_read_or_exception(request.user)
      except Document2.DoesNotExist:
        raise PopupException(_('Job %(id)s does not exist') % {'id': doc_id})

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
          doc2.doc.get().can_write_or_exception(request.user)
        except Document.DoesNotExist:
          raise PopupException(_('Job %(id)s does not exist') % {'id': doc_id})

      return view_func(request, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner



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
