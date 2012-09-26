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


from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.functional import curry, wraps
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render, extract_field_data
from desktop.lib.exceptions import PopupException
from desktop.lib.rest.http_client import RestException
from hadoop.fs.exceptions import WebHdfsException
from jobsub.models import OozieDesign
from liboozie.submittion import Submission

from oozie.conf import SHARE_JOBS
from oozie.import_jobsub import convert_jobsub_design
from oozie.management.commands import oozie_setup
from oozie.models import Job, Workflow, Node, Link, History, Coordinator,\
  Mapreduce, Java, Streaming, Dataset, DataInput, DataOutput,\
  _STD_PROPERTIES_JSON
from oozie.forms import NodeForm, WorkflowForm, CoordinatorForm, DatasetForm,\
  DataInputForm, DataInputSetForm, DataOutputForm, DataOutputSetForm, LinkForm,\
  DefaultLinkForm, design_form_by_type, ImportJobsubDesignForm, ParameterForm


LOG = logging.getLogger(__name__)



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
      job = Job.objects.is_accessible_or_exception(request, job)
    kwargs[job_type] = job

    return view_func(request, *args, **kwargs)
  return wraps(view_func)(decorate)


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
        Job.objects.can_edit_or_exception(request, job)

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
    Job.objects.is_accessible_or_exception(request, action.workflow.id)
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
      dataset = Dataset.objects.is_accessible_or_exception(request, dataset)
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


def list_workflows(request):
  show_setup_app = True
  data = Workflow.objects

  if not SHARE_JOBS.get() and not request.user.is_superuser:
    data = data.filter(owner=request.user)
  else:
    data = data.filter(Q(is_shared=True) | Q(owner=request.user))

  data = data.order_by('-last_modified')

  return render('editor/list_workflows.mako', request, {
    'jobs': list(data),
    'currentuser': request.user,
    'show_setup_app': show_setup_app,
  })


def list_coordinators(request, workflow_id=None):
  show_setup_app = True

  data = Coordinator.objects
  if workflow_id is not None:
    data = data.filter(workflow__id=workflow_id)

  if not SHARE_JOBS.get() and not request.user.is_superuser:
    data = data.filter(owner=request.user)
  else:
    data = data.filter(Q(is_shared=True) | Q(owner=request.user))

  data = data.order_by('-last_modified')

  return render('editor/list_coordinators.mako', request, {
    'jobs': list(data),
    'currentuser': request.user,
    'show_setup_app': show_setup_app,
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
      request.error(_('Errors on the form: %s') % workflow_form.errors)
  else:
    workflow_form = WorkflowForm(instance=workflow)

  return render('editor/create_workflow.mako', request, {
    'workflow_form': workflow_form,
    'workflow': workflow,
  })


@check_job_access_permission
def edit_workflow(request, workflow):
  WorkflowFormSet = inlineformset_factory(Workflow, Node, form=NodeForm, max_num=0, can_order=False, can_delete=False)
  history = History.objects.filter(submitter=request.user, job=workflow).order_by('-submission_date')

  if request.method == 'POST' and Job.objects.can_edit_or_exception(request, workflow):
    try:
      workflow_form = WorkflowForm(request.POST, instance=workflow)
      actions_formset = WorkflowFormSet(request.POST, request.FILES, instance=workflow)

      if 'clone_action' in request.POST: return clone_action(request, action=request.POST['clone_action'])
      if 'delete_action' in request.POST: return delete_action(request, action=request.POST['delete_action'])
      if 'move_up_action' in request.POST: return move_up_action(request, action=request.POST['move_up_action'])
      if 'move_down_action' in request.POST: return move_down_action(request, action=request.POST['move_down_action'])

      if workflow_form.is_valid() and actions_formset.is_valid():
        workflow = workflow_form.save()
        actions_formset.save()

        if workflow.has_cycle():
          raise PopupException(_('Sorry, this operation is not creating a cycle which would break the workflow.'))

        Workflow.objects.check_workspace(workflow, request.fs)

        request.info(_("Workflow saved!"))
        return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': workflow.id}))
    except Exception, e:
      request.error(_('Sorry, this operation is not supported: %(error)s') % {'error': e})

  workflow_form = WorkflowForm(instance=workflow)
  actions_formset = WorkflowFormSet(instance=workflow)

  graph_options = {}
  user_can_edit_job = workflow.is_editable(request.user)
  if not user_can_edit_job:
    graph_options = {'template': 'editor/gen/workflow-graph-readonly.xml.mako'}

  graph = workflow.gen_graph(actions_formset.forms, **graph_options)

  return render('editor/edit_workflow.mako', request, {
    'workflow_form': workflow_form,
    'workflow': workflow,
    'actions_formset': actions_formset,
    'graph': graph,
    'history': history,
    'user_can_edit_job': user_can_edit_job,
    'parameters': extract_field_data(workflow_form['parameters']),
    'job_properties': extract_field_data(workflow_form['job_properties'])
  })


@check_job_access_permission
@check_job_edition_permission()
def delete_workflow(request, workflow):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  Workflow.objects.destroy(workflow, request.fs)
  request.info(_('Workflow deleted!'))

  return redirect(reverse('oozie:list_workflows'))


@check_job_access_permission
def clone_workflow(request, workflow):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  clone = workflow.clone(request.fs, request.user)

  response = {'url': reverse('oozie:edit_workflow', kwargs={'workflow': clone.id})}

  return HttpResponse(json.dumps(response), mimetype="application/json")


@check_job_access_permission
def submit_workflow(request, workflow):
  ParametersFormSet = formset_factory(ParameterForm, extra=0)

  if request.method == 'POST':
    params_form = ParametersFormSet(request.POST)

    if params_form.is_valid():
      mapping = dict([(param['name'], param['value']) for param in params_form.cleaned_data])

      job_id = _submit_workflow(request, workflow, mapping)

      request.info(_('Workflow submitted'))
      return redirect(reverse('oozie:list_oozie_workflow', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s' % params_form.errors))
  else:
    parameters = workflow.find_all_parameters()
    params_form = ParametersFormSet(initial=parameters)

  popup = render('editor/submit_job_popup.mako', request, {
                 'params_form': params_form,
                 'action': reverse('oozie:submit_workflow', kwargs={'workflow': workflow.id})
                 }, force_template=True).content
  return HttpResponse(json.dumps(popup), mimetype="application/json")



def _submit_workflow(request, workflow, mapping):
  try:
    submission = Submission(request.user, workflow, request.fs, mapping)
    job_id = submission.run()
    History.objects.create_from_submission(submission)
    return job_id
  except RestException, ex:
    raise PopupException(_("Error submitting workflow %s") % (workflow,),
                         detail=ex._headers.get('oozie-error-message', ex))

  request.info(_('Workflow submitted'))
  return redirect(reverse('oozie:list_oozie_workflow', kwargs={'job_id': job_id}))


def resubmit_workflow(request, oozie_wf_id):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  history = History.objects.get(oozie_job_id=oozie_wf_id)
  Job.objects.is_accessible_or_exception(request, history.job.id)

  workflow = history.get_workflow().get_full_node()
  properties = history.properties_dict
  job_id = _submit_workflow(request, workflow, properties)

  request.info(_('Workflow re-submitted'))
  return redirect(reverse('oozie:list_oozie_workflow', kwargs={'job_id': job_id}))


@check_job_access_permission
def schedule_workflow(request, workflow):
  if Coordinator.objects.filter(workflow=workflow).exists():
    request.info(_('You already have some coordinators for this workflow. Please submit one or create a new one.'))
    return list_coordinators(request, workflow_id=workflow.id)
  else:
    return create_coordinator(request, workflow=workflow.id)


@check_job_access_permission
@check_job_edition_permission()
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
      'job_properties': 'job_properties' in action_form.fields and extract_field_data(action_form['job_properties']) or '[]',
      'files': 'files' in action_form.fields and extract_field_data(action_form['files']) or '[]',
      'archives': 'archives' in action_form.fields and extract_field_data(action_form['archives']) or '[]',
      'params': 'params' in action_form.fields and extract_field_data(action_form['params']) or '[]',
      'prepares': 'prepares' in action_form.fields and extract_field_data(action_form['prepares']) or '[]',
      'action_form': action_form,
      'node_type': node_type,
      'properties_hint': _STD_PROPERTIES_JSON,
      'form_url': reverse('oozie:new_action', kwargs={'workflow': workflow.id,
                                                      'node_type': node_type,
                                                      'parent_action_id': parent_action_id}),
      'can_edit_action': True,
    })


@check_action_access_permission
def edit_action(request, action):
  ActionForm = design_form_by_type(action.node_type)

  if request.method == 'POST' and Job.objects.can_edit_or_exception(request, action.workflow):
    action_form = ActionForm(request.POST, instance=action)
    if action_form.is_valid():
      action = action_form.save()
      return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': action.workflow.id}))
  else:
    action_form = ActionForm(instance=action)

  return render('editor/edit_workflow_action.mako', request, {
    'workflow': action.workflow,
    'job_properties': 'job_properties' in action_form.fields and extract_field_data(action_form['job_properties']) or '[]',
    'files': 'files' in action_form.fields and extract_field_data(action_form['files']) or '[]',
    'archives': 'archives' in action_form.fields and extract_field_data(action_form['archives']) or '[]',
    'params': 'params' in action_form.fields and extract_field_data(action_form['params']) or '[]',
    'prepares': 'prepares' in action_form.fields and extract_field_data(action_form['prepares']) or '[]',
    'action_form': action_form,
    'node_type': action.node_type,
    'properties_hint': _STD_PROPERTIES_JSON,
    'form_url': reverse('oozie:edit_action', kwargs={'action': action.id}),
    'can_edit_action': action.workflow.is_editable(request.user)
  })


@check_job_access_permission
def import_action(request, workflow, parent_action_id):
  available_actions = OozieDesign.objects.all()

  if request.method == 'POST':
    form = ImportJobsubDesignForm(data=request.POST, choices=[(action.id, action.name) for action in available_actions])
    if form.is_valid():
      try:
        design = OozieDesign.objects.get(id=form.cleaned_data['action_id'])
        action = convert_jobsub_design(design)
        action.workflow = workflow
        action.save()

        workflow.add_action(action, parent_action_id)
      except OozieDesign.DoesNotExist:
        request.error(_('Jobsub design doesn\'t exist.'))
      except (Mapreduce.DoesNotExist, Streaming.DoesNotExist, Java.DoesNotExist):
        request.error(_('Could not convert jobsub design'))
      except:
        request.error(_('Could not convert jobsub design or add action to workflow'))

    return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': action.workflow.id}))

  return render('editor/import_workflow_action.mako', request, {
    'workflow': workflow,
    'available_actions': available_actions,
    'form_url': reverse('oozie:import_action', kwargs={'workflow': workflow.id, 'parent_action_id': parent_action_id}),
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
    if filter(lambda link: link.child.id != action.workflow.end.id,
              [link for link in fork.get_child_join().get_children_links()]):
      raise PopupException(_('Sorry, this Fork has some other actions below its Join and cannot be converted. '
                             'Please delete the nodes below the Join.'))

    link_formset = LinkFormSet(queryset=fork.get_children_links())
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
@check_action_edition_permission
def clone_action(request, action):
  if request.method == 'POST':
    # Really weird: action is like a clone object with the old id here
    action_id = action.id
    workflow = action.workflow
    clone = action.clone()
    workflow.add_action(clone, action_id)
    return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': workflow.id}))
  else:
    raise PopupException(_('A POST request is required.'))


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
    coordinator = Coordinator(owner=request.user, schema_version="uri:oozie:coordinator:0.1", workflow=workflow)
  else:
    coordinator = Coordinator(owner=request.user, schema_version="uri:oozie:coordinator:0.1")

  if request.method == 'POST':
    coordinator_form = CoordinatorForm(request.POST, instance=coordinator, user=request.user)

    if coordinator_form.is_valid():
      coordinator = coordinator_form.save()
      return redirect(reverse('oozie:edit_coordinator', kwargs={'coordinator': coordinator.id}))
    else:
      request.error(_('Errors on the form: %s') % coordinator_form.errors)
  else:
    coordinator_form = CoordinatorForm(instance=coordinator, user=request.user)

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

  return redirect(reverse('oozie:list_coordinators'))


@check_job_access_permission
@check_job_edition_permission(True)
def edit_coordinator(request, coordinator):
  history = History.objects.filter(submitter=request.user, job=coordinator).order_by('-submission_date')

  DatasetFormSet = inlineformset_factory(Coordinator, Dataset, form=DatasetForm, max_num=0, can_order=False, can_delete=True)
  DataInputFormSet = inlineformset_factory(Coordinator, DataInput, form=DataInputSetForm, max_num=0, can_order=False, can_delete=True)
  DataOutputFormSet = inlineformset_factory(Coordinator, DataOutput, form=DataOutputSetForm, max_num=0, can_order=False, can_delete=True)

  dataset = Dataset(coordinator=coordinator)
  dataset_form = DatasetForm(instance=dataset, prefix='create')

  NewDataInputFormSet = inlineformset_factory(Coordinator, DataInput, form=DataInputForm, extra=0, can_order=False, can_delete=False)
  NewDataInputFormSet.form = staticmethod(curry(DataInputForm, coordinator=coordinator))
  NewDataOutputFormSet = inlineformset_factory(Coordinator, DataOutput, form=DataOutputForm, extra=0, can_order=False, can_delete=False)
  NewDataOutputFormSet.form = staticmethod(curry(DataOutputForm, coordinator=coordinator))

  if request.method == 'POST':
    coordinator_form = CoordinatorForm(request.POST, instance=coordinator, user=request.user)
    dataset_formset = DatasetFormSet(request.POST, request.FILES, instance=coordinator)
    data_input_formset = DataInputFormSet(request.POST, request.FILES, instance=coordinator)
    data_output_formset = DataOutputFormSet(request.POST, request.FILES, instance=coordinator)
    new_data_input_formset = NewDataInputFormSet(request.POST, request.FILES, instance=coordinator, prefix='input')
    new_data_output_formset = NewDataOutputFormSet(request.POST, request.FILES, instance=coordinator, prefix='output')

    if coordinator_form.is_valid() and dataset_formset.is_valid() and data_input_formset.is_valid() and data_output_formset.is_valid() \
        and new_data_input_formset.is_valid() and new_data_output_formset.is_valid():
      coordinator = coordinator_form.save()
      dataset_formset.save()
      data_input_formset.save()
      data_output_formset.save()
      new_data_input_formset.save()
      new_data_output_formset.save()

      request.info(_('Coordinator saved!'))
      return redirect(reverse('oozie:edit_coordinator', kwargs={'coordinator': coordinator.id}))
  else:
    coordinator_form = CoordinatorForm(instance=coordinator, user=request.user)
    dataset_formset = DatasetFormSet(instance=coordinator)
    data_input_formset = DataInputFormSet(instance=coordinator)
    data_output_formset = DataOutputFormSet(instance=coordinator)
    new_data_input_formset = NewDataInputFormSet(queryset=DataInput.objects.none(), instance=coordinator, prefix='input')
    new_data_output_formset = NewDataOutputFormSet(queryset=DataOutput.objects.none(), instance=coordinator, prefix='output')

  return render('editor/edit_coordinator.mako', request, {
    'coordinator': coordinator,
    'coordinator_form': coordinator_form,
    'dataset_formset': dataset_formset,
    'data_input_formset': data_input_formset,
    'data_output_formset': data_output_formset,
    'dataset_form': dataset_form,
    'new_data_input_formset': new_data_input_formset,
    'new_data_output_formset': new_data_output_formset,
    'history': history,
    'parameters': extract_field_data(coordinator_form['parameters'])
  })


@check_job_access_permission
@check_job_edition_permission()
def create_coordinator_dataset(request, coordinator):
  """Returns {'status' 0/1, data:html or url}"""

  dataset = Dataset(coordinator=coordinator)
  response = {'status': -1, 'data': 'None'}

  if request.method == 'POST':
    dataset_form = DatasetForm(request.POST, instance=dataset, prefix='create')

    if dataset_form.is_valid():
      dataset_form.save()
      response['status'] = 0
      response['data'] = reverse('oozie:edit_coordinator', kwargs={'coordinator': coordinator.id})
      request.info(_('Dataset created'));
    else:
      dataset_form = DatasetForm(request.POST, instance=dataset, prefix='create')
  else:
    ## Bad
    response['data'] = _('A POST request is required.')

  if response['status'] != 0:
    response['data'] = render('editor/create_coordinator_dataset.mako', request, {
                            'coordinator': coordinator,
                            'dataset_form': dataset_form,
                          }, force_template=True).content

  return HttpResponse(json.dumps(response), mimetype="application/json")


@check_dataset_access_permission
@check_dataset_edition_permission()
def edit_coordinator_dataset(request, dataset):
  """Returns HTML for modal to edit datasets"""

  if request.method == 'POST':
    dataset_form = DatasetForm(request.POST, instance=dataset)

    if dataset_form.is_valid():
      dataset_form.save()
      request.info(_('Dataset modified'));
      return redirect(reverse('oozie:edit_coordinator', kwargs={'coordinator': dataset.coordinator.id}))
    else:
      dataset_form = DatasetForm(request.POST, instance=dataset)
  else:
    dataset_form = DatasetForm(instance=dataset)

  return render('editor/edit_coordinator_dataset.mako', request, {
    'coordinator': dataset.coordinator,
    'dataset_form': dataset_form,
    'path': request.path,
  }, force_template=True)


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
    data_form = DataForm(request.POST, instance=data_instance, coordinator=coordinator, prefix=data_type)

    if data_form.is_valid():
      data_form.save()
      response['status'] = 0
      response['data'] = reverse('oozie:edit_coordinator', kwargs={'coordinator': coordinator.id})
      request.info(_('Coordinator data created'));
    else:
      data_form = DataForm(request.POST, instance=data_instance, coordinator=coordinator)
      response['data'] = data_form.errors
  else:
    response['data'] = _('A POST request is required.')

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
  ParametersFormSet = formset_factory(ParameterForm, extra=0)

  if request.method == 'POST':
    params_form = ParametersFormSet(request.POST)

    if params_form.is_valid():
      mapping = dict([(param['name'], param['value']) for param in params_form.cleaned_data])
      job_id = _submit_coordinator(request, coordinator, mapping)

      request.info(_('Coordinator submitted'))
      return redirect(reverse('oozie:list_oozie_coordinator', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s' % params_form.errors))
  else:
    parameters = coordinator.find_all_parameters()
    params_form = ParametersFormSet(initial=parameters)

  popup = render('editor/submit_job_popup.mako', request, {
                 'params_form': params_form,
                 'action': reverse('oozie:submit_coordinator',  kwargs={'coordinator': coordinator.id})
                }, force_template=True).content
  return HttpResponse(json.dumps(popup), mimetype="application/json")


def _submit_coordinator(request, coordinator, mapping):
  try:
    submission = Submission(request.user, coordinator.workflow, request.fs, mapping)
    wf_dir = submission.deploy()

    properties = {'wf_application_path': request.fs.get_hdfs_path(wf_dir)}
    properties.update(mapping)

    submission = Submission(request.user, coordinator, request.fs, properties=properties)
    job_id = submission.run()

    History.objects.create_from_submission(submission)

    return job_id
  except RestException, ex:
    raise PopupException(_("Error submitting coordinator %s") % (coordinator,),
                         detail=ex._headers.get('oozie-error-message', ex))


def resubmit_coordinator(request, oozie_coord_id):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  history = History.objects.get(oozie_job_id=oozie_coord_id)
  Job.objects.is_accessible_or_exception(request, history.job.id)

  coordinator = history.get_coordinator().get_full_node()
  properties = history.properties_dict
  job_id = _submit_coordinator(request, coordinator, properties)

  request.info(_('Coordinator re-submitted'))
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


def setup_app(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))
  try:
    oozie_setup.Command().handle_noargs()
    request.info(_('Workspaces and examples installed!'))
  except WebHdfsException, e:
    raise PopupException(_('The app setup could complete.'), detail=e)
  return redirect(reverse('oozie:list_workflows'))

