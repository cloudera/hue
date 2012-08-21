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


from django.forms.models import inlineformset_factory, modelformset_factory
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.functional import wraps
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render, PopupException, extract_field_data
from desktop.lib.rest.http_client import RestException
from desktop.log.access import access_warn
from hadoop.fs.exceptions import WebHdfsException
from liboozie.submittion import Submission

from oozie.conf import SHARE_JOBS
from oozie.management.commands import oozie_setup
from oozie.models import Workflow, Node, Link, History, Coordinator,\
  Dataset, DataInput, DataOutput, Job, _STD_PROPERTIES_JSON
from oozie.forms import NodeForm, WorkflowForm, CoordinatorForm, DatasetForm,\
  DataInputForm, DataInputSetForm, DataOutputForm, DataOutputSetForm, LinkForm,\
  DefaultLinkForm, design_form_by_type


LOG = logging.getLogger(__name__)


"""
Permissions:

A Workflow/Coordinator can be accessed/submitted by its owner, a superuser or by anyone if its 'is_shared'
property and SHARE_JOBS are set to True.

A Workflow/Coordinator can be modified only by its owner or a superuser.

Permissions checking happens by adding the decorators.
"""
def can_access_job(user, job):
  return user.is_superuser or job.owner == user or (SHARE_JOBS.get() and job.is_shared)


def can_access_job_or_exception(request, job_id):
  if job_id is None:
    return
  try:
    job = Job.objects.select_related().get(pk=job_id).get_full_node()
    if can_access_job(request.user, job):
      return job
    else:
      message = _("Permission denied. %(username)s don't have the permissions to access job %(id)s") % \
          {'username': request.user.username, 'id': job.id}
      access_warn(request, message)
      request.error(message)
      raise PopupException(message)

  except Job.DoesNotExist:
    raise PopupException(_('job %(id)s not exist') % {'id': job_id})


def check_job_access_permission(view_func):
  """
  Decorator ensuring that the user has access to the workflow or coordinator.

  Arg: 'workflow' or 'coordinator' id.
  Return: the workflow of coordinator or raise an exception

  Notice: its gets an id in input and returns the full object in output (not an id).
  """
  def decorate(request, *args, **kwargs):
    if 'workflow' in kwargs:
      job_type = 'workflow'
    else:
      job_type = 'coordinator'

    job = kwargs.get(job_type)
    if job is not None:
      job = can_access_job_or_exception(request, job)
    kwargs[job_type] = job

    return view_func(request, *args, **kwargs)
  return wraps(view_func)(decorate)


def can_edit_job(user, job):
  """Only owners or admins can modify a job."""
  return user.is_superuser or job.owner == user


def can_edit_job_or_exception(request, job):
  if not can_edit_job(request.user, job):
    raise PopupException('Not allowed to modified this job')


def check_job_edition_permission(authorize_get=False):
  """
  Decorator ensuring that the user has the permissions to modify a workflow or coordinator.

  Need to appear below @check_job_access_permission
  """
  def inner(view_func):
    def decorate(request, *args, **kwargs):
      if 'workflow' in kwargs:
        job_type = 'workflow'
      else:
        job_type = 'coordinator'

      job = kwargs.get(job_type)
      if job is not None and not (authorize_get and request.method == 'GET'):
        can_edit_job_or_exception(request, job)

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
    can_access_job_or_exception(request, action.workflow.id)
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
    can_edit_job_or_exception(request, action.workflow)

    return view_func(request, *args, **kwargs)
  return wraps(view_func)(decorate)


def list_workflows(request, job_type='workflow'):
  show_install_examples = True

  if job_type == 'coordinators':
    data = Coordinator.objects
    template = "editor/list_coordinators.mako"
  else:
    data = Workflow.objects
    template = "editor/list_workflows.mako"

  if not SHARE_JOBS.get() and not request.user.is_superuser:
    data = data.filter(owner=request.user)
  else:
    data = data.filter(Q(is_shared=True) | Q(owner=request.user))

  data = data.order_by('-last_modified')

  return render(template, request, {
    'jobs': list(data),
    'currentuser': request.user,
    'show_install_examples': show_install_examples,
  })


def create_workflow(request):
  workflow = Workflow.objects.new_workflow(request.user)

  if request.method == 'POST':
    workflow_form = WorkflowForm(request.POST, instance=workflow)

    if workflow_form.is_valid():
      wf = workflow_form.save()
      Workflow.objects.initialize(wf, request.fs)
      return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': workflow.id}))
  else:
    workflow_form = WorkflowForm(instance=workflow)

  return render('editor/create_workflow.mako', request, {
    'workflow_form': workflow_form,
    'workflow': workflow,
  })


@check_job_access_permission
def edit_workflow(request, workflow):
  WorkflowFormSet = inlineformset_factory(Workflow, Node, form=NodeForm, max_num=0, can_order=False, can_delete=False)
  history = History.objects.filter(submitter=request.user, job=workflow)

  if request.method == 'POST' and can_edit_job_or_exception(request, workflow):
    workflow_form = WorkflowForm(request.POST, instance=workflow)
    actions_formset = WorkflowFormSet(request.POST, request.FILES, instance=workflow)

    try:
      if 'clone_action' in request.POST: return clone_action(request, action=request.POST['clone_action'])
      if 'delete_action' in request.POST: return delete_action(request, action=request.POST['delete_action'])
      if 'move_up_action' in request.POST: return move_up_action(request, action=request.POST['move_up_action'])
      if 'move_down_action' in request.POST: return move_down_action(request, action=request.POST['move_down_action'])

      if workflow_form.is_valid() and actions_formset.is_valid():
        workflow_form.save()
        actions_formset.save()
        return redirect(reverse('oozie:list_workflows'))
    except Exception, e:
      request.error(_('Sorry, this operation is not supported: %(error)s') % {'error': e})
  else:
    workflow_form = WorkflowForm(instance=workflow)
    actions_formset = WorkflowFormSet(instance=workflow)

  return render('editor/edit_workflow.mako', request, {
    'workflow_form': workflow_form,
    'workflow': workflow,
    'actions_formset': actions_formset,
    'graph': workflow.gen_graph(actions_formset.forms),
    'history': history,
  })


@check_job_access_permission
@check_job_edition_permission()
def delete_workflow(request, workflow):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  workflow.coordinator_set.update(workflow=None) # In Django 1.3 could do ON DELETE set NULL
  workflow.save()
  workflow.delete()
  Submission(request.user, workflow, request.fs, {}).remove_deployment_dir()
  request.info(_('Workflow deleted!'))

  return redirect(reverse('oozie:list_workflows'))


@check_job_access_permission
def clone_workflow(request, workflow):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  clone = workflow.clone(request.user)

  response = {'url': reverse('oozie:edit_workflow', kwargs={'workflow': clone.id})}

  return HttpResponse(json.dumps(response), mimetype="application/json")


@check_job_access_permission
def submit_workflow(request, workflow):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  try:
    mapping = dict(request.POST.iteritems())
    submission = Submission(request.user, workflow, request.fs, mapping)
    job_id = submission.run()
  except RestException, ex:
    raise PopupException(_("Error submitting workflow %s") % (workflow,),
                         detail=ex._headers.get('oozie-error-message', ex))

  History.objects.create_from_submission(submission)
  request.info(_('Workflow submitted'))

  return redirect(reverse('oozie:list_oozie_workflow', kwargs={'job_id': job_id}))


@check_job_access_permission
def get_workflow_parameters(request, workflow):
  """
  Return the parameters found in the workflow as a JSON dictionary of {param_key : label}.
  This expects an Ajax call.
  """
  params = workflow.find_parameters()

  params_with_labels = dict((p, p.upper()) for p in params)
  return render('dont_care_for_ajax', request, { 'params': params_with_labels })


@check_job_access_permission
def new_action(request, workflow, node_type, parent_action_id):
  ActionForm = design_form_by_type(node_type)

  if request.method == 'POST':
    action_form = ActionForm(request.POST)

    if action_form.is_valid():
      action = action_form.save(commit=False)
      action.node_type = node_type
      action.workflow = workflow
      action.save()

      workflow.add_action(action, parent_action_id)

      return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': workflow.id}))
  else:
    action_form = ActionForm()

  return render('editor/edit_workflow_action.mako', request, {
      'workflow': workflow,
      'job_properties': extract_field_data(action_form['job_properties']),
      'files': extract_field_data(action_form['files']),
      'archives': extract_field_data(action_form['archives']),
      'params': 'params' in action_form.fields and extract_field_data(action_form['params']) or '[]',
      'action_form': action_form,
      'node_type': node_type,
      'properties_hint': _STD_PROPERTIES_JSON,
      'form_url': reverse('oozie:new_action', kwargs={'workflow': workflow.id,
                                                     'node_type': node_type,
                                                     'parent_action_id': parent_action_id}),
    })


@check_action_access_permission
def edit_action(request, action):
  ActionForm = design_form_by_type(action.node_type)

  if request.method == 'POST' and can_edit_job_or_exception(request, action.workflow):
    action_form = ActionForm(request.POST, instance=action)
    if action_form.is_valid():
      action = action_form.save()
      return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': action.workflow.id}))
  else:
    action_form = ActionForm(instance=action)

  return render('editor/edit_workflow_action.mako', request, {
    'workflow': action.workflow,
    'job_properties': extract_field_data(action_form['job_properties']),
    'files': extract_field_data(action_form['files']),
    'archives': extract_field_data(action_form['archives']),
    'params': 'params' in action_form.fields and extract_field_data(action_form['params']) or '[]',
    'action_form': action_form,
    'node_type': action.node_type,
    'properties_hint': _STD_PROPERTIES_JSON,
    'form_url': reverse('oozie:edit_action', kwargs={'action': action.id}),
  })


@check_action_access_permission
@check_action_edition_permission
def edit_workflow_fork(request, action):
  fork = action

  LinkFormSet = modelformset_factory(Link, form=LinkForm, max_num=0)

  if request.method == 'POST':
    link_formset = LinkFormSet(request.POST)
    default_link_form = DefaultLinkForm(request.POST, action=fork)

    if link_formset.is_valid():
      is_decision = fork.has_decisions()
      link_formset.save()
      if not is_decision and fork.has_decisions():
        default_link = default_link_form.save(commit=False)
        default_link.parent = fork
        default_link.name = 'default'
        default_link.comment = 'default'
        default_link.save()
        fork.convert_to_decision()
      fork.update_description()

      return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': fork.workflow.id}))
  else:
    link_formset = LinkFormSet(queryset=fork.get_children_links().exclude(name__in=['related', 'default']))
    default_link = Link(parent=fork, name='default', comment='default')
    default_link_form = DefaultLinkForm(action=fork, instance=default_link)

  return render('editor/edit_workflow_fork.mako', request, {
    'workflow': fork.workflow,
    'fork': fork,
    'link_formset': link_formset,
    'default_link_form': default_link_form,
  })


@check_action_access_permission
@check_action_edition_permission
def delete_action(request, action):
  if request.method == 'POST':
    action.workflow.delete_action(action)
    return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': action.workflow.id}))
  else:
    raise PopupException(_('A POST request is required.'))


@check_action_access_permission
def clone_action(request, action):
  # Really weird: action is like a clone object with the old id here
  action_id = action.id
  workflow = action.workflow
  clone = action.clone()
  workflow.add_action(clone, action_id)
  return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': workflow.id}))


@check_action_access_permission
@check_action_edition_permission
def move_up_action(request, action):
  if request.method == 'POST':
    action.workflow.move_action_up(action)
    return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': action.workflow.id}))
  else:
    raise PopupException(_('A POST request is required.'))


@check_action_access_permission
@check_action_edition_permission
def move_down_action(request, action):
  if request.method == 'POST':
    action.workflow.move_action_down(action)
    return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': action.workflow.id}))
  else:
    raise PopupException(_('A POST request is required.'))


@check_job_access_permission
def create_coordinator(request, workflow=None):
  if workflow is not None:
    coordinator = Coordinator(owner=request.user, workflow=workflow)
  else:
    coordinator = Coordinator(owner=request.user)

  if request.method == 'POST':
    coordinator_form = CoordinatorForm(request.POST, instance=coordinator)

    if coordinator_form.is_valid():
      coordinator = coordinator_form.save()
      return redirect(reverse('oozie:edit_coordinator', kwargs={'coordinator': coordinator.id}))
  else:
    coordinator_form = CoordinatorForm(instance=coordinator)

  return render('editor/create_coordinator.mako', request, {
    'coordinator': coordinator,
    'coordinator_form': coordinator_form,
  })


@check_job_access_permission
@check_job_edition_permission()
def delete_coordinator(request, coordinator):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  coordinator.delete()
  Submission(request.user, coordinator, request.fs, {}).remove_deployment_dir()
  request.info(_('Coordinator deleted!'))

  return redirect(reverse('oozie:list_coordinator'))


@check_job_access_permission
@check_job_edition_permission(True)
def edit_coordinator(request, coordinator):
  history = History.objects.filter(submitter=request.user, job=coordinator)

  DatasetFormSet = inlineformset_factory(Coordinator, Dataset, form=DatasetForm, max_num=0, can_order=False, can_delete=True)
  DataInputFormSet = inlineformset_factory(Coordinator, DataInput, form=DataInputSetForm, max_num=0, can_order=False, can_delete=True)
  DataOutputFormSet = inlineformset_factory(Coordinator, DataOutput, form=DataOutputSetForm, max_num=0, can_order=False, can_delete=True)

  dataset = Dataset(coordinator=coordinator)
  dataset_form = DatasetForm(instance=dataset)
  data_input = DataInput(coordinator=coordinator)
  data_input_form = DataInputForm(instance=data_input, coordinator=coordinator)
  data_output = DataOutput(coordinator=coordinator)
  data_output_form = DataOutputForm(instance=data_output, coordinator=coordinator)

  if request.method == 'POST':
    coordinator_form = CoordinatorForm(request.POST, instance=coordinator)
    dataset_formset = DatasetFormSet(request.POST, request.FILES, instance=coordinator)
    data_input_formset = DataInputFormSet(request.POST, request.FILES, instance=coordinator)
    data_output_formset = DataOutputFormSet(request.POST, request.FILES, instance=coordinator)

    if coordinator_form.is_valid() and dataset_formset.is_valid() and data_input_formset.is_valid() and data_output_formset.is_valid():
      coordinator = coordinator_form.save()
      dataset_formset.save()
      data_input_formset.save()
      data_output_formset.save()

      return redirect(reverse('oozie:list_coordinator'))
  else:
    coordinator_form = CoordinatorForm(instance=coordinator)
    dataset_formset = DatasetFormSet(instance=coordinator)
    data_input_formset = DataInputFormSet(instance=coordinator)
    data_output_formset = DataOutputFormSet(instance=coordinator)

  return render('editor/edit_coordinator.mako', request, {
    'coordinator': coordinator,
    'coordinator_form': coordinator_form,
    'dataset_formset': dataset_formset,
    'data_input_formset': data_input_formset,
    'data_output_formset': data_output_formset,
    'dataset_form': dataset_form,
    'data_input_form': data_input_form,
    'data_output_form': data_output_form,
    'history': history,
  })


@check_job_access_permission
@check_job_edition_permission()
def create_coordinator_dataset(request, coordinator):
  """Returns {'status' 0/1, data:html or url}"""

  dataset = Dataset(coordinator=coordinator)
  response = {'status': -1, 'data': 'None'}

  if request.method == 'POST':
    dataset_form = DatasetForm(request.POST, instance=dataset)

    if dataset_form.is_valid():
      dataset_form.save()
      response['status'] = 0
      response['data'] = reverse('oozie:edit_coordinator', kwargs={'coordinator': coordinator.id})
      request.info(_('Dataset created'));
    else:
      dataset_form = DatasetForm(request.POST, instance=dataset)
  else:
    ## Bad
    response['data'] = _('A POST request is required.')

  if response['status'] != 0:
    response['data'] = render('editor/create_coordinator_dataset.mako', request, {
                            'coordinator': coordinator,
                            'dataset_form': dataset_form,
                          }, force_template=True).content

  return HttpResponse(json.dumps(response), mimetype="application/json")


@check_job_access_permission
@check_job_edition_permission()
def create_coordinator_data(request, coordinator, data_type):
  """Returns {'status' 0/1, data:html or url}"""

  if data_type == 'input':
    data_instance = DataInput(coordinator=coordinator)
    DataForm = DataInputForm
  else:
    data_instance = DataOutput(coordinator=coordinator)
    DataForm = DataOutputForm

  response = {'status': -1, 'data': 'None'}

  if request.method == 'POST':
    data_form = DataForm(request.POST, instance=data_instance, coordinator=coordinator)

    if data_form.is_valid():
      data_form.save()
      response['status'] = 0
      response['data'] = reverse('oozie:edit_coordinator', kwargs={'coordinator': coordinator.id})
      request.info(_('Coordinator data created'));
    else:
      data_form = DataForm(request.POST, instance=data_instance, coordinator=coordinator)
  else:
    ## Bad
    response['data'] = _('A POST request is required.')

  if response['status'] != 0:
    response['data'] = render('editor/create_coordinator_data.mako', request, {
                              'coordinator': coordinator,
                              'form': data_form, },
                              force_template=True).content

  return HttpResponse(json.dumps(response), mimetype="application/json")


@check_job_access_permission
def clone_coordinator(request, coordinator):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  clone = coordinator.clone(request.user)

  response = {'url': reverse('oozie:edit_coordinator', kwargs={'coordinator': clone.id})}

  return HttpResponse(json.dumps(response), mimetype="application/json")


@check_job_access_permission
def submit_coordinator(request, coordinator):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  try:
    if not coordinator.workflow.is_deployed(request.fs):
      submission = Submission(request.user, coordinator.workflow, request.fs, request.POST)
      wf_dir = submission.deploy()
      coordinator.workflow.deployment_dir = wf_dir
      coordinator.workflow.save()

    coordinator.deployment_dir = coordinator.workflow.deployment_dir
    properties = {'wf_application_path': coordinator.workflow.deployment_dir}
    properties.update(dict(request.POST.iteritems()))

    submission = Submission(request.user, coordinator, request.fs, properties=properties)
    job_id = submission.run()
  except RestException, ex:
    raise PopupException(_("Error submitting coordinator %s") % (coordinator,),
                         detail=ex._headers.get('oozie-error-message', ex))

  History.objects.create_from_submission(submission)
  request.info(_('Coordinator submitted'))

  return redirect(reverse('oozie:list_oozie_coordinator', kwargs={'job_id': job_id}))


def list_history(request):
  """
  List the job submission history.
  Normal users can only look at their own submissions.
  """
  history = History.objects

  if not request.user.is_superuser:
    history = history.filter(submitter=request.user)
  history = history.order_by('-submission_date')

  return render('editor/list_history.mako', request, {
    'history': history,
  })


def list_history_record(request, record_id):
  """
  List a job submission history.
  Normal users can only look at their own jobs.
  """
  history = History.objects

  if not request.user.is_superuser:
    history.filter(submitter=request.user)
  history = history.get(id=record_id)

  return render('editor/list_history_record.mako', request, {
    'record': history,
  })


def install_examples(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))
  try:
    oozie_setup.Command().handle_noargs()
    request.info(_('Examples installed!'))
  except WebHdfsException, e:
    raise PopupException(_('The examples could not be installed.'), detail=e)
  return redirect(reverse('oozie:list_workflows'))

