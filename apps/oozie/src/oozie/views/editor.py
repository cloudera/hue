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
import shutil
import time

from django.urls import reverse
from django.db.models import Q
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.defaultfilters import strip_tags
from django.utils.functional import curry
from django.utils.http import http_date
from django.utils.translation import ugettext as _, activate as activate_translation

from desktop.lib.django_util import JsonResponse, render, extract_field_data
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str
from desktop.lib.rest.http_client import RestException
from desktop.models import Document

from liboozie.credentials import Credentials
from liboozie.oozie_api import get_oozie
from liboozie.submittion import Submission

from filebrowser.lib.archives import archive_factory
from oozie.decorators import check_job_access_permission, check_job_edition_permission,\
                             check_dataset_access_permission, check_dataset_edition_permission
from oozie.conf import ENABLE_CRON_SCHEDULING, ENABLE_V2
from oozie.importlib.workflows import import_workflow as _import_workflow
from oozie.importlib.coordinators import import_coordinator as _import_coordinator
from oozie.management.commands import oozie_setup
from oozie.models import Workflow, History, Coordinator,\
                         Dataset, DataInput, DataOutput,\
                         ACTION_TYPES, Bundle, BundledCoordinator, Job
from oozie.forms import WorkflowForm, CoordinatorForm, DatasetForm,\
                        DataInputForm, DataOutputForm, LinkForm,\
                        DefaultLinkForm, ParameterForm, NodeForm,\
                        BundleForm, BundledCoordinatorForm, design_form_by_type,\
                        ImportWorkflowForm, ImportCoordinatorForm

from desktop.auth.backend import is_admin

LOG = logging.getLogger(__name__)


def list_workflows(request):
  data = Document.objects.available(Workflow, request.user)
  data = [job for job in data if job.managed]

  return render('editor/list_workflows.mako', request, {
    'jobs': data,
    'json_jobs': json.dumps([job.id for job in data]),
  })


def list_trashed_workflows(request):
  data = Document.objects.trashed(Workflow, request.user)
  data = [job for job in data if job.managed]

  return render('editor/list_trashed_workflows.mako', request, {
    'jobs': data,
    'json_jobs': json.dumps([job.id for job in data]),
  })


def list_coordinators(request, workflow_id=None):
  data = Document.objects.available(Coordinator, request.user)

  if workflow_id is not None:
    data = [job for job in data if job.workflow.id == workflow_id]

  enable_cron_scheduling = ENABLE_CRON_SCHEDULING.get()

  return render('editor/list_coordinators.mako', request, {
    'jobs': data,
    'json_jobs': json.dumps([job.id for job in data]),
    'enable_cron_scheduling': enable_cron_scheduling,
  })


def list_trashed_coordinators(request):
  data = Document.objects.trashed(Coordinator, request.user)

  return render('editor/list_trashed_coordinators.mako', request, {
    'jobs': data,
    'json_jobs': json.dumps([job.id for job in data]),
  })


def list_bundles(request):
  data = Document.objects.available(Bundle, request.user)

  return render('editor/list_bundles.mako', request, {
    'jobs': data,
    'json_jobs': json.dumps([job.id for job in data]),
  })


def list_trashed_bundles(request):
  data = Document.objects.trashed(Bundle, request.user)

  return render('editor/list_trashed_bundles.mako', request, {
    'jobs': data,
    'json_jobs': json.dumps([job.id for job in data]),
  })


def create_workflow(request):
  workflow = Workflow.objects.new_workflow(request.user)

  if request.method == 'POST':
    workflow_form = WorkflowForm(request.POST, instance=workflow)

    if workflow_form.is_valid():
      wf = workflow_form.save()
      wf.managed = True
      Workflow.objects.initialize(wf, request.fs)
      return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': workflow.id}))
  else:
    workflow_form = WorkflowForm(instance=workflow)

  return render('editor/create_workflow.mako', request, {
    'workflow_form': workflow_form,
    'workflow': workflow,
  })


def import_workflow(request):
  if ENABLE_V2.get():
    raise PopupException('/oozie/import_workflow is deprecated in the version 2 of Editor')

  workflow = Workflow.objects.new_workflow(request.user)

  if request.method == 'POST':
    workflow_form = ImportWorkflowForm(request.POST, request.FILES, instance=workflow)

    if workflow_form.is_valid():
      if workflow_form.cleaned_data.get('resource_archive'):
        # Upload resources to workspace
        source = workflow_form.cleaned_data.get('resource_archive')
        if source.name.endswith('.zip'):
          workflow.save()
          Workflow.objects.initialize(workflow, request.fs)
          temp_path = archive_factory(source).extract()
          request.fs.copyFromLocal(temp_path, workflow.deployment_dir)
          shutil.rmtree(temp_path)
        else:
          raise PopupException(_('Archive should be a Zip.'))
      else:
        workflow.save()
        Workflow.objects.initialize(workflow, request.fs)

      workflow.managed = True
      workflow.save()

      workflow_definition = workflow_form.cleaned_data['definition_file'].read()

      try:
        _import_workflow(fs=request.fs, workflow=workflow, workflow_definition=workflow_definition)
        request.info(_('Workflow imported'))
        return redirect(reverse('oozie:edit_workflow', kwargs={'workflow': workflow.id}))
      except Exception, e:
        request.error(_('Could not import workflow: %s' % e))
        Workflow.objects.destroy(workflow, request.fs)
        raise PopupException(_('Could not import workflow.'), detail=e)

    else:
      request.error(_('Errors on the form: %s') % workflow_form.errors)

  else:
    workflow_form = ImportWorkflowForm(instance=workflow)

  return render('editor/import_workflow.mako', request, {
    'workflow_form': workflow_form,
    'workflow': workflow,
  })


def import_coordinator(request):
  coordinator = Coordinator(owner=request.user, schema_version="uri:oozie:coordinator:0.2")

  if request.method == 'POST':
    coordinator_form = ImportCoordinatorForm(request.POST, request.FILES, instance=coordinator, user=request.user)

    if coordinator_form.is_valid():
      coordinator_definition = coordinator_form.cleaned_data['definition_file'].read()

      try:
        _import_coordinator(coordinator=coordinator, coordinator_definition=coordinator_definition)
        coordinator.managed = True
        coordinator.name = coordinator_form.cleaned_data.get('name')
        coordinator.save()
      except Exception, e:
        request.error(_('Could not import coordinator: %s' % e))
        raise PopupException(_('Could not import coordinator.'), detail=e)

      if coordinator_form.cleaned_data.get('resource_archive'):
        # Upload resources to workspace
        source = coordinator_form.cleaned_data.get('resource_archive')
        if source.name.endswith('.zip'):
          temp_path = archive_factory(source).extract()
          request.fs.copyFromLocal(temp_path, coordinator.deployment_dir)
          shutil.rmtree(temp_path)
        else:
          Coordinator.objects.filter(id=coordinator.id).delete()
          raise PopupException(_('Archive should be a Zip.'))

      Document.objects.link(coordinator, owner=request.user, name=coordinator.name, description=coordinator.description)
      request.info(_('Coordinator imported'))
      return redirect(reverse('oozie:edit_coordinator', kwargs={'coordinator': coordinator.id}))

    else:
      request.error(_('Errors on the form'))

  else:
    coordinator_form = ImportCoordinatorForm(instance=coordinator, user=request.user)

  return render('editor/import_coordinator.mako', request, {
    'coordinator_form': coordinator_form,
    'coordinator': coordinator,
  })


@check_job_access_permission()
def export_workflow(request, workflow):
  mapping = dict([(param['name'], param['value']) for param in workflow.find_all_parameters()])

  oozie_api = get_oozie(request.user)
  credentials = Credentials()
  credentials.fetch(oozie_api)
  mapping['credentials'] = credentials.get_properties()

  zip_file = workflow.compress(mapping=mapping)

  response = HttpResponse(content_type="application/zip")
  response["Last-Modified"] = http_date(time.time())
  response["Content-Length"] = len(zip_file.getvalue())
  response['Content-Disposition'] = 'attachment; filename="workflow-%s-%d.zip"' % (workflow.name, workflow.id)
  response.write(zip_file.getvalue())
  return response


@check_job_access_permission()
def edit_workflow(request, workflow):
  history = History.objects.filter(submitter=request.user, job=workflow).order_by('-submission_date')
  workflow_form = WorkflowForm(instance=workflow)
  user_can_access_job = workflow.can_read(request.user)
  user_can_edit_job = workflow.is_editable(request.user)
  oozie_api = get_oozie(request.user)
  credentials = Credentials()
  credentials.fetch(oozie_api)

  return render('editor/edit_workflow.mako', request, {
    'oozie_api': oozie_api,
    'workflow_form': workflow_form,
    'workflow': workflow,
    'history': history,
    'user_can_access_job': user_can_access_job,
    'user_can_edit_job': user_can_edit_job,
    'job_properties': extract_field_data(workflow_form['job_properties']),
    'link_form': LinkForm(),
    'default_link_form': DefaultLinkForm(action=workflow.start),
    'node_form': NodeForm(),
    'action_forms': [(node_type, design_form_by_type(node_type, request.user, workflow)())
                     for node_type in ACTION_TYPES.iterkeys()],
    'credentials': json.dumps(credentials.credentials.keys())
  })


def delete_workflow(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  skip_trash = 'skip_trash' in request.GET

  job_ids = request.POST.getlist('job_selection')

  for job_id in job_ids:
    job = Job.objects.can_read_or_exception(request, job_id)
    Job.objects.can_edit_or_exception(request, job)
    if skip_trash:
      Workflow.objects.destroy(job, request.fs)
    else:
      job.workflow.delete(skip_trash=False)

  if skip_trash:
    request.info(_('Workflow(s) deleted.'))
  else:
    request.info(_('Workflow(s) trashed.'))

  return redirect(reverse('oozie:list_workflows'))


def restore_workflow(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  job_ids = request.POST.getlist('job_selection')

  for job_id in job_ids:
    job = Document.objects.can_read_or_exception(request.user, Job, job_id)
    Job.objects.can_edit_or_exception(request, job)
    job.workflow.restore()

  request.info(_('Workflow(s) restored.'))

  return redirect(reverse('oozie:list_workflows'))


@check_job_access_permission()
def clone_workflow(request, workflow):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  clone = workflow.clone(request.fs, request.user)

  response = {'url': reverse('oozie:edit_workflow', kwargs={'workflow': clone.id})}

  return JsonResponse(response)



@check_job_access_permission()
def submit_workflow(request, workflow):
  ParametersFormSet = formset_factory(ParameterForm, extra=0)

  if request.method == 'POST':
    params_form = ParametersFormSet(request.POST)

    if params_form.is_valid():
      mapping = dict([(param['name'], param['value']) for param in params_form.cleaned_data])

      job_id = _submit_workflow(request.user, request.fs, request.jt, workflow, mapping)

      request.info(_('Workflow submitted'))
      return redirect(reverse('oozie:list_oozie_workflow', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s' % params_form.errors))
  else:
    parameters = workflow.find_all_parameters()
    initial_params = ParameterForm.get_initial_params(dict([(param['name'], param['value']) for param in parameters]))
    params_form = ParametersFormSet(initial=initial_params)

  popup = render('editor/submit_job_popup.mako', request, {
                   'params_form': params_form,
                   'action': reverse('oozie:submit_workflow', kwargs={'workflow': workflow.id})
                 }, force_template=True).content
  return JsonResponse(popup, safe=False)


def _submit_workflow(user, fs, jt, workflow, mapping):
  try:
    submission = Submission(user, workflow, fs, jt, mapping)
    job_id = submission.run()
    History.objects.create_from_submission(submission)
    return job_id
  except RestException, ex:
    detail = ex._headers.get('oozie-error-message', ex)
    if 'Max retries exceeded with url' in str(detail):
      detail = '%s: %s' % (_('The Oozie server is not running'), detail)
    LOG.error(smart_str(detail))
    raise PopupException(_("Error submitting workflow %s") % (workflow,), detail=detail)

  return redirect(reverse('oozie:list_oozie_workflow', kwargs={'job_id': job_id}))


@check_job_access_permission()
def schedule_workflow(request, workflow):
  data = Document.objects.available(Coordinator, request.user)
  data = [coordinator for coordinator in data if coordinator.coordinatorworkflow == workflow]
  if data:
    request.info(_('You already have some coordinators for this workflow. Submit one or create a new one.'))
    return list_coordinators(request, workflow_id=workflow.id)
  else:
    return create_coordinator(request, workflow=workflow.id)


@check_job_access_permission()
def create_coordinator(request, workflow=None):
  if workflow is not None:
    coordinator = Coordinator(owner=request.user, schema_version="uri:oozie:coordinator:0.2", coordinatorworkflow=workflow)
  else:
    coordinator = Coordinator(owner=request.user, schema_version="uri:oozie:coordinator:0.2")

  enable_cron_scheduling = ENABLE_CRON_SCHEDULING.get()

  if request.method == 'POST':
    coordinator_form = CoordinatorForm(request.POST, instance=coordinator, user=request.user)

    if coordinator_form.is_valid():
      coordinator = coordinator_form.save()
      if enable_cron_scheduling:
        coordinator.cron_frequency = {'frequency': request.POST.get('cron_frequency'), 'isAdvancedCron': request.POST.get('isAdvancedCron') == 'on'}
      coordinator.save()
      Document.objects.link(coordinator, owner=coordinator.owner, name=coordinator.name, description=coordinator.description)
      return redirect(reverse('oozie:edit_coordinator', kwargs={'coordinator': coordinator.id}) + "#step3")
    else:
      request.error(_('Errors on the form: %s') % coordinator_form.errors)
  else:
    coordinator_form = CoordinatorForm(instance=coordinator, user=request.user)

  return render('editor/create_coordinator.mako', request, {
    'coordinator': coordinator,
    'coordinator_form': coordinator_form,
    'coordinator_frequency': json.dumps(coordinator.cron_frequency),
    'enable_cron_scheduling': enable_cron_scheduling,
  })


def delete_coordinator(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  skip_trash = 'skip_trash' in request.GET

  job_ids = request.POST.getlist('job_selection')

  for job_id in job_ids:
    job = Job.objects.can_read_or_exception(request, job_id)
    Job.objects.can_edit_or_exception(request, job)
    if skip_trash:
      Submission(request.user, job, request.fs, {}).remove_deployment_dir()
    job.delete(skip_trash=skip_trash)

  if skip_trash:
    request.info(_('Coordinator(s) deleted.'))
  else:
    request.info(_('Coordinator(s) trashed.'))

  return redirect(reverse('oozie:list_coordinators'))


def restore_coordinator(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  job_ids = request.POST.getlist('job_selection')

  for job_id in job_ids:
    job = Job.objects.can_read_or_exception(request, job_id)
    Job.objects.can_edit_or_exception(request, job)
    job.restore()

  request.info(_('Coordinator(s) restored.'))

  return redirect(reverse('oozie:list_coordinators'))


@check_job_access_permission()
@check_job_edition_permission(True)
def edit_coordinator(request, coordinator):
  history = History.objects.filter(submitter=request.user, job=coordinator).order_by('-submission_date')

  DatasetFormSet = inlineformset_factory(Coordinator, Dataset, form=DatasetForm, max_num=0, can_order=False, can_delete=True)
  DataInputFormSet = inlineformset_factory(Coordinator, DataInput, form=DataInputForm, max_num=0, can_order=False, can_delete=True)
  DataInputFormSet.form = staticmethod(curry(DataInputForm, coordinator=coordinator))
  DataOutputFormSet = inlineformset_factory(Coordinator, DataOutput, form=DataOutputForm, max_num=0, can_order=False, can_delete=True)
  DataOutputFormSet.form = staticmethod(curry(DataOutputForm, coordinator=coordinator))

  dataset = Dataset(coordinator=coordinator)
  dataset_form = DatasetForm(instance=dataset, prefix='create')

  NewDataInputFormSet = inlineformset_factory(Coordinator, DataInput, form=DataInputForm, extra=0, can_order=False, can_delete=False)
  NewDataInputFormSet.form = staticmethod(curry(DataInputForm, coordinator=coordinator))
  NewDataOutputFormSet = inlineformset_factory(Coordinator, DataOutput, form=DataOutputForm, extra=0, can_order=False, can_delete=False)
  NewDataOutputFormSet.form = staticmethod(curry(DataOutputForm, coordinator=coordinator))

  enable_cron_scheduling = ENABLE_CRON_SCHEDULING.get()

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
      coordinator.sla = json.loads(request.POST.get('sla'))
      if enable_cron_scheduling:
        coordinator.cron_frequency = {'frequency': strip_tags(request.POST.get('cron_frequency')), 'isAdvancedCron': request.POST.get('isAdvancedCron') == 'on'}
      coordinator.save()

      request.info(_('Coordinator saved.'))
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
    'dataset': dataset,
    'dataset_form': dataset_form,
    'new_data_input_formset': new_data_input_formset,
    'new_data_output_formset': new_data_output_formset,
    'history': history,
    'coordinator_frequency': json.dumps(coordinator.cron_frequency),
    'enable_cron_scheduling': enable_cron_scheduling,
  })


@check_job_access_permission()
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
      response['data'] = reverse('oozie:edit_coordinator', kwargs={'coordinator': coordinator.id}) + "#listDataset"
      request.info(_('Dataset created'))
  else:
    ## Bad
    response['data'] = _('A POST request is required.')

  if response['status'] != 0:
    response['data'] = render('editor/create_coordinator_dataset.mako', request, {
                            'coordinator': coordinator,
                            'dataset_form': dataset_form,
                            'dataset': dataset,
                          }, force_template=True).content

  return JsonResponse(response, safe=False)


@check_dataset_access_permission
@check_dataset_edition_permission()
def edit_coordinator_dataset(request, dataset):
  """Returns HTML for modal to edit datasets"""

  response = {'status': -1, 'data': 'None'}

  if request.method == 'POST':
    dataset_form = DatasetForm(request.POST, instance=dataset, prefix='edit')

    if dataset_form.is_valid():
      dataset = dataset_form.save()
      response['status'] = 0
      response['data'] = reverse('oozie:edit_coordinator', kwargs={'coordinator': dataset.coordinator.id}) + "#listDataset"
      request.info(_('Dataset modified'))
      if dataset.start > dataset.coordinator.start:
        request.warn(_('Beware: dataset start date was after the coordinator start date.'))
    else:
      response['data'] = dataset_form.errors
  else:
    dataset_form = DatasetForm(instance=dataset, prefix='edit')

  if response['status'] != 0:
    response['data'] = render('editor/edit_coordinator_dataset.mako', request, {
                          'coordinator': dataset.coordinator,
                          'dataset_form': dataset_form,
                          'dataset': dataset,
                          'path': request.path,
                        }, force_template=True).content

  return JsonResponse(response, safe=False)


@check_job_access_permission()
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
      response['data'] = data_form.errors
  else:
    response['data'] = _('A POST request is required.')

  return JsonResponse(response)


@check_job_access_permission()
def clone_coordinator(request, coordinator):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  clone = coordinator.clone(request.user)

  response = {'url': reverse('oozie:edit_coordinator', kwargs={'coordinator': clone.id})}

  return JsonResponse(response)


@check_job_access_permission()
def submit_coordinator(request, coordinator):
  ParametersFormSet = formset_factory(ParameterForm, extra=0)

  if request.method == 'POST':
    params_form = ParametersFormSet(request.POST)

    if params_form.is_valid():
      mapping = dict([(param['name'], param['value']) for param in params_form.cleaned_data])
      job_id = _submit_coordinator(request, coordinator, mapping)

      request.info(_('Coordinator submitted.'))
      return redirect(reverse('oozie:list_oozie_coordinator', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s' % params_form.errors))
  else:
    parameters = coordinator.find_all_parameters()
    initial_params = ParameterForm.get_initial_params(dict([(param['name'], param['value']) for param in parameters]))
    params_form = ParametersFormSet(initial=initial_params)

  popup = render('editor/submit_job_popup.mako', request, {
                 'params_form': params_form,
                 'action': reverse('oozie:submit_coordinator',  kwargs={'coordinator': coordinator.id})
                }, force_template=True).content
  return JsonResponse(popup, safe=False)


def _submit_coordinator(request, coordinator, mapping):
  try:
    wf_dir = Submission(request.user, coordinator.workflow, request.fs, request.jt, mapping).deploy()

    properties = {'wf_application_path': request.fs.get_hdfs_path(wf_dir)}
    properties.update(mapping)

    submission = Submission(request.user, coordinator, request.fs, request.jt, properties=properties)
    job_id = submission.run()

    History.objects.create_from_submission(submission)

    return job_id
  except RestException, ex:
    raise PopupException(_("Error submitting coordinator %s") % (coordinator,),
                         detail=ex._headers.get('oozie-error-message', ex))


def create_bundle(request):
  bundle = Bundle(owner=request.user, schema_version='uri:oozie:bundle:0.2')

  if request.method == 'POST':
    bundle_form = BundleForm(request.POST, instance=bundle)

    if bundle_form.is_valid():
      bundle = bundle_form.save()
      Document.objects.link(bundle, owner=bundle.owner, name=bundle.name, description=bundle.description)
      return redirect(reverse('oozie:edit_bundle', kwargs={'bundle': bundle.id}))
    else:
      request.error(_('Errors on the form: %s') % bundle_form.errors)
  else:
    bundle_form = BundleForm(instance=bundle)

  return render('editor/create_bundle.mako', request, {
    'bundle': bundle,
    'bundle_form': bundle_form,
  })



def delete_bundle(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  skip_trash = 'skip_trash' in request.GET

  job_ids = request.POST.getlist('job_selection')

  for job_id in job_ids:
    job = Job.objects.can_read_or_exception(request, job_id)
    Job.objects.can_edit_or_exception(request, job)
    if skip_trash:
      Submission(request.user, job, request.fs, {}).remove_deployment_dir()
    job.delete(skip_trash=skip_trash)

  request.info(_('Bundle(s) deleted.'))

  return redirect(reverse('oozie:list_bundles'))


def restore_bundle(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  job_ids = request.POST.getlist('job_selection')

  for job_id in job_ids:
    job = Job.objects.can_read_or_exception(request, job_id)
    Job.objects.can_edit_or_exception(request, job)
    job.restore()

  request.info(_('Bundle(s) restored.'))

  return redirect(reverse('oozie:list_bundles'))


@check_job_access_permission()
@check_job_edition_permission(True)
def edit_bundle(request, bundle):
  history = History.objects.filter(submitter=request.user, job=bundle).order_by('-submission_date')

  BundledCoordinatorFormSet = inlineformset_factory(Bundle, BundledCoordinator, form=BundledCoordinatorForm, max_num=0, can_order=False, can_delete=True)
  bundle_form = BundleForm(instance=bundle)

  if request.method == 'POST':
    bundle_form = BundleForm(request.POST, instance=bundle)
    bundled_coordinator_formset = BundledCoordinatorFormSet(request.POST, instance=bundle)

    if bundle_form.is_valid() and bundled_coordinator_formset.is_valid():
      bundle = bundle_form.save()
      bundled_coordinator_formset.save()

      request.info(_('Bundle saved.'))
      return redirect(reverse('oozie:list_bundles'))
  else:
    bundle_form = BundleForm(instance=bundle)
    bundled_coordinator_formset = BundledCoordinatorFormSet(instance=bundle)

  return render('editor/edit_bundle.mako', request, {
    'bundle': bundle,
    'bundle_form': bundle_form,
    'bundled_coordinator_formset': bundled_coordinator_formset,
    'bundled_coordinator_html_form': get_create_bundled_coordinator_html(request, bundle),
    'history': history
  })


@check_job_access_permission()
@check_job_edition_permission(True)
def create_bundled_coordinator(request, bundle):
  bundled_coordinator_instance = BundledCoordinator(bundle=bundle)

  response = {'status': -1, 'data': 'None'}

  if request.method == 'POST':
    bundled_coordinator_form = BundledCoordinatorForm(request.POST, instance=bundled_coordinator_instance, prefix='create-bundled-coordinator')

    if bundled_coordinator_form.is_valid():
      bundled_coordinator_form.save()
      response['status'] = 0
      response['data'] = reverse('oozie:edit_bundle', kwargs={'bundle': bundle.id}) + "#listCoordinators"
      request.info(_('Coordinator added to the bundle!'))
  else:
    bundled_coordinator_form = BundledCoordinatorForm(instance=bundled_coordinator_instance, prefix='create-bundled-coordinator')

  if response['status'] != 0:
    response['data'] = get_create_bundled_coordinator_html(request, bundle, bundled_coordinator_form=bundled_coordinator_form)

  return JsonResponse(response)


def get_create_bundled_coordinator_html(request, bundle, bundled_coordinator_form=None):
  if bundled_coordinator_form is None:
    bundled_coordinator_instance = BundledCoordinator(bundle=bundle)
    bundled_coordinator_form = BundledCoordinatorForm(instance=bundled_coordinator_instance, prefix='create-bundled-coordinator')

  return render('editor/create_bundled_coordinator.mako', request, {
                            'bundle': bundle,
                            'bundled_coordinator_form': bundled_coordinator_form,
                          }, force_template=True).content.decode('utf-8', 'replace')


@check_job_access_permission()
@check_job_edition_permission(True)
def edit_bundled_coordinator(request, bundle, bundled_coordinator):
  bundled_coordinator_instance = BundledCoordinator.objects.get(id=bundled_coordinator) # todo secu

  response = {'status': -1, 'data': 'None'}

  if request.method == 'POST':
    bundled_coordinator_form = BundledCoordinatorForm(request.POST, instance=bundled_coordinator_instance, prefix='edit-bundled-coordinator')

    if bundled_coordinator_form.is_valid():
      bundled_coordinator_form.save()
      response['status'] = 0
      response['data'] = reverse('oozie:edit_bundle', kwargs={'bundle': bundle.id}) + "#listCoordinators"
      request.info(_('Bundled coordinator updated!'))
  else:
    bundled_coordinator_form = BundledCoordinatorForm(instance=bundled_coordinator_instance, prefix='edit-bundled-coordinator')

  if response['status'] != 0:
    response['data'] = render('editor/edit_bundled_coordinator.mako', request, {
                            'bundle': bundle,
                            'bundled_coordinator_form': bundled_coordinator_form,
                            'bundled_coordinator_instance': bundled_coordinator_instance,
                          }, force_template=True).content

  return JsonResponse(response, safe=False)


@check_job_access_permission()
def clone_bundle(request, bundle):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  clone = bundle.clone(request.user)

  response = {'url': reverse('oozie:edit_bundle', kwargs={'bundle': clone.id})}

  return JsonResponse(response)


@check_job_access_permission()
def submit_bundle(request, bundle):
  ParametersFormSet = formset_factory(ParameterForm, extra=0)

  if request.method == 'POST':
    params_form = ParametersFormSet(request.POST)

    if params_form.is_valid():
      mapping = dict([(param['name'], param['value']) for param in params_form.cleaned_data])
      job_id = _submit_bundle(request, bundle, mapping)

      request.info(_('Bundle submitted.'))
      return redirect(reverse('oozie:list_oozie_bundle', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s' % params_form.errors))
  else:
    parameters = bundle.find_all_parameters()
    initial_params = ParameterForm.get_initial_params(dict([(param['name'], param['value']) for param in parameters]))
    params_form = ParametersFormSet(initial=initial_params)

  popup = render('editor/submit_job_popup.mako', request, {
                 'params_form': params_form,
                 'action': reverse('oozie:submit_bundle',  kwargs={'bundle': bundle.id})
                }, force_template=True).content
  return JsonResponse(popup, safe=False)


def _submit_bundle(request, bundle, properties):
  try:
    deployment_dirs = {}

    for bundled in bundle.coordinators.all():
      wf_dir = Submission(request.user, bundled.coordinator.coordinatorworkflow, request.fs, request.jt, properties).deploy()
      deployment_dirs['wf_%s_dir' % bundled.coordinator.coordinatorworkflow.id] = request.fs.get_hdfs_path(wf_dir)
      coord_dir = Submission(request.user, bundled.coordinator, request.fs, request.jt, properties).deploy()
      deployment_dirs['coord_%s_dir' % bundled.coordinator.id] = coord_dir

    properties.update(deployment_dirs)
    submission = Submission(request.user, bundle, request.fs, request.jt, properties=properties)
    job_id = submission.run()

    History.objects.create_from_submission(submission)

    return job_id
  except RestException, ex:
    raise PopupException(_("Error submitting bundle %s") % (bundle,),
                         detail=ex._headers.get('oozie-error-message', ex))


def list_history(request):
  """
  List the job submission history.
  Normal users can only look at their own submissions.
  """
  history = History.objects

  if not is_admin(request.user):
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

  if not is_admin(request.user):
    history.filter(submitter=request.user)
  history = history.get(id=record_id)

  return render('editor/list_history_record.mako', request, {
    'record': history,
  })


def install_examples(request):
  result = {'status': -1, 'message': ''}

  if request.method != 'POST':
    result['message'] = _('A POST request is required.')
  else:
    try:
      oozie_setup.Command().handle()
      activate_translation(request.LANGUAGE_CODE)
      result['status'] = 0
    except Exception, e:
      LOG.exception(e)
      result['message'] = str(e)

  return JsonResponse(result)
