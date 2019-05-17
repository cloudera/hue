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

from django.urls import reverse
from django.forms.formsets import formset_factory
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from desktop.conf import USE_NEW_EDITOR, IS_MULTICLUSTER_ONLY, has_multi_cluster
from desktop.lib import django_mako
from desktop.lib.django_util import JsonResponse, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str, force_unicode
from desktop.lib.rest.http_client import RestException
from desktop.lib.json_utils import JSONEncoderForHTML
from desktop.models import Document, Document2

from liboozie.credentials import Credentials
from liboozie.oozie_api import get_oozie
from liboozie.submission2 import Submission
from metadata.conf import DEFAULT_PUBLIC_KEY
from notebook.connectors.base import Notebook

from oozie.decorators import check_document_access_permission, check_document_modify_permission,\
  check_editor_access_permission
from oozie.forms import ParameterForm
from oozie.models import Workflow as OldWorklow, Coordinator as OldCoordinator, Bundle as OldBundle, Job
from oozie.models2 import Node, Workflow, Coordinator, Bundle, NODES, WORKFLOW_NODE_PROPERTIES, import_workflow_from_hue_3_7,\
    find_dollar_variables, find_dollar_braced_variables, WorkflowBuilder,\
  _import_workspace, _save_workflow
from oozie.utils import convert_to_server_timezone
from oozie.views.editor import edit_workflow as old_edit_workflow, edit_coordinator as old_edit_coordinator, edit_bundle as old_edit_bundle


LOG = logging.getLogger(__name__)


@check_editor_access_permission
def list_editor_workflows(request):
  if USE_NEW_EDITOR.get():
    docs = Document2.objects.documents(user=request.user).search_documents(types=['oozie-workflow2'])
    workflows = [doc.to_dict() for doc in docs]
  else:
    workflows = [d.content_object.to_dict() for d in Document.objects.get_docs(request.user, Document2, extra='workflow2')]

  workflows_v1 = [job.doc.get().to_dict() for job in Document.objects.available(OldWorklow, request.user) if job.managed]
  if workflows_v1:
    workflows.extend(workflows_v1)

  return render('editor2/list_editor_workflows.mako', request, {
    'workflows_json': json.dumps(workflows, cls=JSONEncoderForHTML),
  })


@check_editor_access_permission
def open_old_workflow(request):
  doc_id = request.GET.get('workflow')
  workflow = Document.objects.get(id=doc_id).content_object.get_full_node()

  try:
    _workflow = import_workflow_from_hue_3_7(workflow)
    return _edit_workflow(request, None, _workflow)
  except Exception, e:
    LOG.warn('Could not open old worklow: %s' % smart_str(e))
    return old_edit_workflow(request, workflow=workflow.id)


@check_editor_access_permission
@check_document_access_permission()
def edit_workflow(request):
  workflow_id = request.GET.get('workflow')

  wid = {}
  if workflow_id.isdigit():
    wid['id'] = workflow_id
  else:
    wid['uuid'] = workflow_id
  doc = Document2.objects.get(type='oozie-workflow2', **wid)
  workflow = Workflow(document=doc)

  return _edit_workflow(request, doc, workflow)


def _edit_workflow(request, doc, workflow):
  workflow_data = workflow.get_data()

  api = get_oozie(request.user)
  credentials = Credentials()

  try:
    credentials.fetch(api)
  except Exception, e:
    LOG.error(smart_str(e))

  can_edit_json = doc is None or (doc.can_write(request.user) if USE_NEW_EDITOR.get() else doc.doc.get().is_editable(request.user))

  return render('editor2/workflow_editor.mako', request, {
      'layout_json': json.dumps(workflow_data['layout'], cls=JSONEncoderForHTML),
      'workflow_json': json.dumps(workflow_data['workflow'], cls=JSONEncoderForHTML),
      'credentials_json': json.dumps(credentials.credentials.keys(), cls=JSONEncoderForHTML),
      'workflow_properties_json': json.dumps(WORKFLOW_NODE_PROPERTIES, cls=JSONEncoderForHTML),
      'doc_uuid': doc.uuid if doc else '',
      'subworkflows_json': json.dumps(_get_workflows(request.user), cls=JSONEncoderForHTML),
      'can_edit_json': json.dumps(can_edit_json),
      'is_embeddable': request.GET.get('is_embeddable', False),
  })


@check_editor_access_permission
def new_workflow(request):
  doc = None
  workflow = Workflow(user=request.user)
  workflow.set_workspace(request.user)
  workflow.check_workspace(request.fs, request.user)

  return _edit_workflow(request, doc, workflow)


@check_editor_access_permission
def delete_job(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  jobs = json.loads(request.POST.get('selection'))

  for job in jobs:
    if job.get('uuid'):
      doc2 = Document2.objects.get(id=job['id'])
      if USE_NEW_EDITOR.get():
        doc2 = Document2.objects.get(id=job['id'])
        doc2.can_write_or_exception(request.user)
        doc2.trash()
      else:
        doc = doc2.doc.get()
        doc.can_write_or_exception(request.user)
        doc.delete()
        doc2.delete()
    else: # Old version
      job = Job.objects.can_read_or_exception(request, job['object_id'])
      Job.objects.can_edit_or_exception(request, job)
      OldWorklow.objects.destroy(job, request.fs)

  response = {}
  request.info(_('Document deleted.') if len(jobs) > 1 else _('Document deleted.'))

  return JsonResponse(response)


@check_editor_access_permission
@check_document_access_permission()
def copy_workflow(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  jobs = json.loads(request.POST.get('selection'))

  for job in jobs:
    doc2 = Document2.objects.get(type='oozie-workflow2', id=job['id'])
    doc = doc2.doc.get()

    name = doc2.name + '-copy'
    doc2 = doc2.copy(name=name, owner=request.user)

    doc.copy(content_object=doc2, name=name, owner=request.user)

    workflow = Workflow(document=doc2)
    workflow.update_name(name)

    _import_workspace(request.fs, request.user, workflow)

    doc2.update_data({'workflow': workflow.get_data()['workflow']})
    doc2.save()

  response = {}
  request.info(_('Workflows copied.') if len(jobs) > 1 else _('Workflow copied.'))

  return JsonResponse(response)


@check_editor_access_permission
@check_document_modify_permission()
def save_workflow(request):
  response = {'status': -1}

  workflow = json.loads(request.POST.get('workflow', '{}'))
  layout = json.loads(request.POST.get('layout', '{}'))

  is_imported = workflow['properties'].get('imported')

  workflow_doc = _save_workflow(workflow, layout, request.user, fs=request.fs)

  # For old workflow import
  if is_imported:
    response['url'] = reverse('oozie:edit_workflow') + '?workflow=' + str(workflow_doc.id)

  response['status'] = 0
  response['id'] = workflow_doc.id
  response['doc_uuid'] = workflow_doc.uuid
  response['message'] = _('Page saved !')

  return JsonResponse(response)


@check_editor_access_permission
def new_node(request):
  response = {'status': -1}

  node = json.loads(request.POST.get('node', '{}'))

  properties = NODES[node['widgetType']].get_mandatory_fields()
  workflows = []

  if node['widgetType'] == 'subworkflow-widget':
    workflows = _get_workflows(request.user)

  response['status'] = 0
  response['properties'] = properties
  response['workflows'] = workflows

  return JsonResponse(response)


def _get_workflows(user):
  if USE_NEW_EDITOR.get():
    workflows = [{
          'name': workflow.name,
          'owner': workflow.owner.username,
          'value': workflow.uuid,
          'id': workflow.id
        } for workflow in [doc for doc in Document2.objects.documents(user).search_documents(types=['oozie-workflow2']).order_by('-id')]
      ]
  else:
    workflows = [{
          'name': workflow.name,
          'owner': workflow.owner.username,
          'value': workflow.uuid,
          'id': workflow.id
        } for workflow in [d.content_object for d in Document.objects.get_docs(user, Document2, extra='workflow2').order_by('-id')]
    ]
  return workflows

@check_editor_access_permission
def add_node(request):
  response = {'status': -1}

  node = json.loads(request.POST.get('node', '{}'))
  properties = json.loads(request.POST.get('properties', '{}'))
  copied_properties = json.loads(request.POST.get('copiedProperties', '{}'))

  _properties = dict(NODES[node['widgetType']].get_fields())
  _properties.update(dict([(_property['name'], _property['value']) for _property in properties]))

  if node['widgetType'] == 'spark-widget':
    _properties['files'] = [{'value': _properties['files']}]

  if copied_properties:
    _properties.update(copied_properties)

  response['status'] = 0
  response['properties'] = _properties
  response['name'] = '%s-%s' % (node['widgetType'].split('-')[0], node['id'][:4])

  return JsonResponse(response)


@check_editor_access_permission
def action_parameters(request):
  response = {'status': -1}
  parameters = set()

  try:
    node_data = json.loads(request.POST.get('node', '{}'))

    parameters = parameters.union(set(Node(node_data).find_parameters()))

    script_path = node_data.get('properties', {}).get('script_path', {})
    if script_path:
      script_path = script_path.replace('hdfs://', '')

      if request.fs.do_as_user(request.user, request.fs.exists, script_path):
        data = request.fs.do_as_user(request.user, request.fs.read, script_path, 0, 16 * 1024 ** 2)

        if node_data['type'] in ('hive', 'hive2'):
          parameters = parameters.union(set(find_dollar_braced_variables(data)))
        elif node_data['type'] == 'pig':
          parameters = parameters.union(set(find_dollar_variables(data)))
    elif node_data['type'] == 'hive-document':
      notebook = Notebook(document=Document2.objects.get_by_uuid(user=request.user, uuid=node_data['properties']['uuid']))
      parameters = parameters.union(set(find_dollar_braced_variables(notebook.get_str())))
    elif node_data['type'] == 'sqoop-document':
      notebook = Notebook(document=Document2.objects.get_by_uuid(user=request.user, uuid=node_data['properties']['uuid']))
      parameters = parameters.union(set(find_dollar_braced_variables(notebook.get_str())))
    elif node_data['type'] == 'spark-document':
      notebook = Notebook(document=Document2.objects.get_by_uuid(user=request.user, uuid=node_data['properties']['uuid']))
      for arg in notebook.get_data()['snippets'][0]['properties']['spark_arguments']:
        parameters = parameters.union(set(find_dollar_braced_variables(arg)))

    response['status'] = 0
    response['parameters'] = list(parameters)
  except Exception, e:
    response['message'] = str(e)

  return JsonResponse(response)


@check_editor_access_permission
@check_document_access_permission()
def workflow_parameters(request):
  response = {'status': -1}

  try:
    workflow_doc = Document2.objects.get(uuid=request.GET.get('uuid') or request.GET.get('document'))

    if workflow_doc.type == 'oozie-workflow2':
      workflow = Workflow(document=workflow_doc, user=request.user)
    else:
      wf_doc = WorkflowBuilder().create_workflow(document=workflow_doc, user=request.user, managed=True)
      workflow = Workflow(data=wf_doc.data)
      wf_doc.delete()

    response['status'] = 0
    response['parameters'] = workflow.find_all_parameters(with_lib_path=False)
  except Exception, e:
    response['message'] = str(e)

  return JsonResponse(response)


@check_editor_access_permission
def gen_xml_workflow(request):
  response = {'status': -1}

  try:
    workflow_json = json.loads(request.POST.get('workflow', '{}'))

    workflow = Workflow(workflow=workflow_json, user=request.user)

    response['status'] = 0
    response['xml'] = workflow.to_xml()
  except Exception, e:
    response['message'] = str(e)

  return JsonResponse(response)


@check_editor_access_permission
@check_document_access_permission()
def submit_workflow(request, doc_id):
  workflow = Workflow(document=Document2.objects.get(id=doc_id), user=request.user)

  return _submit_workflow_helper(request, workflow, submit_action=reverse('oozie:editor_submit_workflow', kwargs={'doc_id': workflow.id}))


@check_editor_access_permission
@check_document_access_permission()
def submit_single_action(request, doc_id, node_id):
  parent_doc = Document2.objects.get(id=doc_id)
  parent_wf = Workflow(document=parent_doc)
  workflow_data = parent_wf.create_single_action_workflow_data(node_id)
  _data = json.loads(workflow_data)

  # Create separate wf object for the submit node with new deployment_dir
  workflow = Workflow(data=workflow_data)
  workflow.set_workspace(request.user)

  workflow.check_workspace(request.fs, request.user)

  # The imported wf deployment directory might not neccessarily exist on first submission
  if not request.fs.exists(parent_wf.deployment_dir):
    request.fs.do_as_user(request.user.username, request.fs.mkdir, parent_wf.deployment_dir)
  workflow.import_workspace(request.fs, parent_wf.deployment_dir, request.user)
  workflow.document = parent_doc

  return _submit_workflow_helper(request, workflow, submit_action=reverse('oozie:submit_single_action', kwargs={'doc_id': doc_id, 'node_id': node_id}))


def _submit_workflow_helper(request, workflow, submit_action):
  ParametersFormSet = formset_factory(ParameterForm, extra=0)

  if request.method == 'POST':
    cluster = json.loads(request.POST.get('cluster', '{}'))
    params_form = ParametersFormSet(request.POST)

    if params_form.is_valid():
      mapping = dict([(param['name'], param['value']) for param in params_form.cleaned_data])
      mapping['dryrun'] = request.POST.get('dryrun_checkbox') == 'on'
      mapping['send_email'] = request.POST.get('email_checkbox') == 'on'
      if '/submit_single_action/' in submit_action:
        mapping['submit_single_action'] = True

      if 'altus' in cluster.get('type', ''):
        mapping['cluster'] = cluster.get('id')

      try:
        job_id = _submit_workflow(request.user, request.fs, request.jt, workflow, mapping)
      except Exception, e:
        raise PopupException(_('Workflow submission failed'), detail=smart_str(e), error_code=200)
      jsonify = request.POST.get('format') == 'json'
      if jsonify:
        return JsonResponse({'status': 0, 'job_id': job_id, 'type': 'workflow'}, safe=False)
      else:
        request.info(_('Workflow submitted'))
        return redirect(reverse('oozie:list_oozie_workflow', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s' % params_form.errors))
  else:
    cluster_json = request.GET.get('cluster', '{}')
    parameters = workflow and workflow.find_all_parameters() or []
    initial_params = ParameterForm.get_initial_params(dict([(param['name'], param['value']) for param in parameters]))
    params_form = ParametersFormSet(initial=initial_params)


    return render('editor2/submit_job_popup.mako', request, {
                     'params_form': params_form,
                     'name': workflow.name,
                     'action': submit_action,
                     'show_dryrun': True,
                     'email_id': request.user.email,
                     'is_oozie_mail_enabled': _is_oozie_mail_enabled(request.user),
                     'return_json': request.GET.get('format') == 'json',
                     'cluster_json': cluster_json
                   }, force_template=True)


def _is_oozie_mail_enabled(user):
  api = get_oozie(user)
  oozie_conf = api.get_configuration()
  return oozie_conf.get('oozie.email.smtp.host') != 'localhost'


def _submit_workflow(user, fs, jt, workflow, mapping):
  try:
    submission = Submission(user, workflow, fs, jt, mapping)
    job_id = submission.run()

    workflow.document.add_to_history(submission.user, {'properties': submission.properties, 'oozie_id': submission.oozie_id})

    return job_id
  except RestException, ex:
    detail = ex._headers.get('oozie-error-message', ex)
    if 'Max retries exceeded with url' in str(detail):
      detail = '%s: %s' % (_('The Oozie server is not running'), detail)
    LOG.exception('Error submitting workflow: %s' % smart_str(detail))
    raise PopupException(_("Error submitting workflow %s: %s") % (workflow, detail))


@check_editor_access_permission
def list_editor_coordinators(request):
  if USE_NEW_EDITOR.get():
    docs = Document2.objects.documents(user=request.user).search_documents(types=['oozie-coordinator2'])
    coordinators = [doc.to_dict() for doc in docs]
  else:
    coordinators = [d.content_object.to_dict() for d in Document.objects.get_docs(request.user, Document2, extra='coordinator2')]

  coordinators_v1 = [job.doc.get().to_dict() for job in Document.objects.available(OldCoordinator, request.user)]
  if coordinators_v1:
    coordinators.extend(coordinators_v1)

  return render('editor2/list_editor_coordinators.mako', request, {
    'coordinators_json': json.dumps(coordinators, cls=JSONEncoderForHTML),
  })


@check_editor_access_permission
@check_document_access_permission()
def edit_coordinator(request):
  coordinator_id = request.GET.get('coordinator', request.GET.get('uuid'))
  doc = None
  workflow_uuid = None

  if coordinator_id:
    cid = {}
    if coordinator_id.isdigit():
      cid['id'] = coordinator_id
    else:
      cid['uuid'] = coordinator_id
    doc = Document2.objects.get(**cid)
    coordinator = Coordinator(document=doc)
  else:
    coordinator = Coordinator()
    coordinator.set_workspace(request.user)

  if request.GET.get('workflow'):
    workflow_uuid = request.GET.get('workflow')

  if workflow_uuid:
    coordinator.data['properties']['workflow'] = workflow_uuid

  api = get_oozie(request.user)
  credentials = Credentials()

  try:
    credentials.fetch(api)
  except Exception, e:
    LOG.error(smart_str(e))

  if USE_NEW_EDITOR.get():
    scheduled_uuid = coordinator.data['properties']['workflow'] or coordinator.data['properties']['document']
    if scheduled_uuid:
      try:
        document = Document2.objects.get(uuid=scheduled_uuid)
      except Document2.DoesNotExist as e:
        document = None
        coordinator.data['properties']['workflow'] = ''
        LOG.warn("Workflow with uuid %s doesn't exist: %s" % (scheduled_uuid, e))

      if document and document.is_trashed:
        raise PopupException(_('Your workflow %s has been trashed!') % (document.name if document.name else ''))

      if document and not document.can_read(request.user):
        raise PopupException(_('You don\'t have access to the workflow or document of this coordinator.'))
  else:
    workflows = [dict([('uuid', d.content_object.uuid), ('name', d.content_object.name)])
                      for d in Document.objects.available_docs(Document2, request.user).filter(extra='workflow2')]

    if coordinator_id and not filter(lambda a: a['uuid'] == coordinator.data['properties']['workflow'], workflows):
      raise PopupException(_('You don\'t have access to the workflow of this coordinator.'))

  if USE_NEW_EDITOR.get(): # In Hue 4, merge with above
    workflows = [dict([('uuid', d.uuid), ('name', d.name)])
                      for d in Document2.objects.documents(request.user, include_managed=False).search_documents(types=['oozie-workflow2'])]

  can_edit = doc is None or (doc.can_write(request.user) if USE_NEW_EDITOR.get() else doc.doc.get().is_editable(request.user))
  if request.GET.get('format') == 'json': # For Editor
    return JsonResponse({
      'coordinator': coordinator.get_data_for_json(),
      'credentials': credentials.credentials.keys(),
      'workflows': workflows,
      'doc_uuid': doc.uuid if doc else '',
      'is_embeddable': request.GET.get('is_embeddable', False),
      'can_edit': can_edit,
      'layout': django_mako.render_to_string('editor2/common_scheduler.mako', {'coordinator_json': coordinator.to_json_for_html()})
    })
  else:
    return render('editor2/coordinator_editor.mako', request, {
      'coordinator_json': coordinator.to_json_for_html(),
      'credentials_json': json.dumps(credentials.credentials.keys(), cls=JSONEncoderForHTML),
      'workflows_json': json.dumps(workflows, cls=JSONEncoderForHTML),
      'doc_uuid': doc.uuid if doc else '',
      'is_embeddable': request.GET.get('is_embeddable', False),
      'can_edit_json': json.dumps(can_edit)
  })


@check_editor_access_permission
def new_coordinator(request):
  return edit_coordinator(request)


@check_editor_access_permission
def open_old_coordinator(request):
  doc_id = request.GET.get('coordinator')
  coordinator_id = Document.objects.get(id=doc_id).object_id

  return old_edit_coordinator(request, coordinator=coordinator_id)


@check_editor_access_permission
@check_document_access_permission()
def copy_coordinator(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  jobs = json.loads(request.POST.get('selection'))

  for job in jobs:
    doc2 = Document2.objects.get(type='oozie-coordinator2', id=job['id'])
    doc = doc2.doc.get()

    name = doc2.name + '-copy'
    doc2 = doc2.copy(name=name, owner=request.user)

    doc.copy(content_object=doc2, name=name, owner=request.user)

    coord = Coordinator(document=doc2)
    coordinator_data = coord.get_data_for_json()
    coordinator_data['name'] = name

    _import_workspace(request.fs, request.user, coord)
    doc2.update_data(coordinator_data)
    doc2.save()

  response = {}
  request.info(_('Coordinator copied.') if len(jobs) > 1 else _('Coordinator copied.'))

  return JsonResponse(response)


@check_editor_access_permission
@check_document_modify_permission()
def save_coordinator(request):
  response = {'status': -1}

  coordinator_data = json.loads(request.POST.get('coordinator', '{}'))

  if coordinator_data.get('id'):
    coordinator_doc = Document2.objects.get(id=coordinator_data['id'])
  else:
    coordinator_doc = Document2.objects.create(
        name=coordinator_data['name'],
        uuid=coordinator_data['uuid'],
        type='oozie-coordinator2',
        owner=request.user,
        is_managed=coordinator_data.get('isManaged')
    )
    Document.objects.link(coordinator_doc, owner=coordinator_doc.owner, name=coordinator_doc.name, description=coordinator_doc.description, extra='coordinator2')

  scheduled_id = coordinator_data['properties']['workflow'] or coordinator_data['properties']['document']
  if scheduled_id:
    scheduled_doc = Document2.objects.get(uuid=scheduled_id)
    scheduled_doc.can_read_or_exception(request.user)
    coordinator_doc.dependencies = [scheduled_doc]

  coordinator_doc1 = coordinator_doc._get_doc1(doc2_type='coordinator2')
  coordinator_doc.update_data(coordinator_data)
  coordinator_doc.name = coordinator_doc1.name = coordinator_data['name']
  coordinator_doc.description = coordinator_doc1.description = coordinator_data['properties']['description']
  coordinator_doc.save()
  coordinator_doc1.save()

  response['status'] = 0
  response['id'] = coordinator_doc.id
  response['uuid'] = coordinator_doc.uuid
  response['message'] = _('Saved!') if coordinator_data.get('id') else _('Updated!')

  return JsonResponse(response)


@check_editor_access_permission
def gen_xml_coordinator(request):
  response = {'status': -1}

  coordinator_dict = json.loads(request.POST.get('coordinator', '{}'))

  coordinator = Coordinator(data=coordinator_dict)

  response['status'] = 0
  response['xml'] = coordinator.to_xml()

  return JsonResponse(response)


@check_editor_access_permission
@check_document_access_permission()
def coordinator_parameters(request):
  response = {'status': -1}

  try:
    coordinator = Coordinator(document=Document2.objects.get(type='oozie-coordinator2', uuid=request.GET.get('uuid')))

    response['status'] = 0
    response['parameters'] = coordinator.find_all_parameters(with_lib_path=False)
  except Exception, e:
    response['message'] = str(e)

  return JsonResponse(response)


@check_editor_access_permission
@check_document_access_permission()
def submit_coordinator(request, doc_id):
  if doc_id.isdigit():
    coordinator = Coordinator(document=Document2.objects.get(id=doc_id))
  else:
    coordinator = Coordinator(document=Document2.objects.get_by_uuid(user=request.user, uuid=doc_id))

  ParametersFormSet = formset_factory(ParameterForm, extra=0)

  if request.method == 'POST':
    params_form = ParametersFormSet(request.POST)

    if params_form.is_valid():
      mapping = dict([(param['name'], param['value']) for param in params_form.cleaned_data])
      mapping['dryrun'] = request.POST.get('dryrun_checkbox') == 'on'
      jsonify = request.POST.get('format') == 'json'
      try:
        job_id = _submit_coordinator(request, coordinator, mapping)
      except Exception, e:
        message = force_unicode(str(e))
        return JsonResponse({'status': -1, 'message': message}, safe=False)
      if jsonify:
        return JsonResponse({'status': 0, 'job_id': job_id, 'type': 'schedule'}, safe=False)
      else:
        request.info(_('Coordinator submitted.'))
        return redirect(reverse('oozie:list_oozie_coordinator', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s' % params_form.errors))
  else:
    parameters = coordinator.find_all_parameters()
    initial_params = ParameterForm.get_initial_params(dict([(param['name'], param['value']) for param in parameters]))
    params_form = ParametersFormSet(initial=initial_params)

    return render('editor2/submit_job_popup.mako', request, {
                 'params_form': params_form,
                 'name': coordinator.name,
                 'action': reverse('oozie:editor_submit_coordinator',  kwargs={'doc_id': coordinator.id}),
                 'show_dryrun': True,
                 'return_json': request.GET.get('format') == 'json'
                }, force_template=True)


def _submit_coordinator(request, coordinator, mapping):
  try:
    wf = coordinator.workflow
    if IS_MULTICLUSTER_ONLY.get() and has_multi_cluster():
      mapping['auto-cluster'] = {
        u'additionalClusterResourceTags': [],
        u'automaticTerminationCondition': u'EMPTY_JOB_QUEUE', #'u'NONE',
        u'cdhVersion': u'CDH514',
        u'clouderaManagerPassword': u'guest',
        u'clouderaManagerUsername': u'guest',
        u'clusterName': u'analytics4', # Add time variable
        u'computeWorkersConfiguration': {
          u'bidUSDPerHr': 0,
          u'groupSize': 0,
          u'useSpot': False
        },
        u'environmentName': u'crn:altus:environments:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:environment:analytics/236ebdda-18bd-428a-9d2b-cd6973d42946',
        u'instanceBootstrapScript': u'',
        u'instanceType': u'm4.xlarge',
        u'jobSubmissionGroupName': u'',
        u'jobs': [{
            u'failureAction': u'INTERRUPT_JOB_QUEUE',
            u'name': u'a87e20d7-5c0d-49ee-ab37-625fa2803d51',
            u'sparkJob': {
              u'applicationArguments': ['5'],
              u'jars': [u's3a://datawarehouse-customer360/ETL/spark-examples.jar'],
              u'mainClass': u'org.apache.spark.examples.SparkPi'
            }
          },
  #         {
  #           u'failureAction': u'INTERRUPT_JOB_QUEUE',
  #           u'name': u'a87e20d7-5c0d-49ee-ab37-625fa2803d51',
  #           u'sparkJob': {
  #             u'applicationArguments': ['10'],
  #             u'jars': [u's3a://datawarehouse-customer360/ETL/spark-examples.jar'],
  #             u'mainClass': u'org.apache.spark.examples.SparkPi'
  #           }
  #         },
  #         {
  #           u'failureAction': u'INTERRUPT_JOB_QUEUE',
  #           u'name': u'a87e20d7-5c0d-49ee-ab37-625fa2803d51',
  #           u'sparkJob': {
  #             u'applicationArguments': [u'filesystems3.conf'],
  #             u'jars': [u's3a://datawarehouse-customer360/ETL/envelope-0.6.0-SNAPSHOT-c6.jar'],
  #             u'mainClass': u'com.cloudera.labs.envelope.EnvelopeMain',
  #             u'sparkArguments': u'--archives=s3a://datawarehouse-customer360/ETL/filesystems3.conf'
  #           }
  #         }
        ],
        u'namespaceName': u'crn:altus:sdx:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:namespace:analytics/7ea35fe5-dbc9-4b17-92b1-97a1ab32e410',
        u'publicKey': DEFAULT_PUBLIC_KEY.get(),
        u'serviceType': u'SPARK',
        u'workersConfiguration': {},
        u'workersGroupSize': u'3'
      }
    wf_dir = Submission(request.user, wf, request.fs, request.jt, mapping, local_tz=coordinator.data['properties']['timezone']).deploy()

    properties = {'wf_application_path': request.fs.get_hdfs_path(wf_dir)}
    properties.update(mapping)

    submission = Submission(request.user, coordinator, request.fs, request.jt, properties=properties)
    job_id = submission.run()

    return job_id
  except RestException, ex:
    LOG.exception('Error submitting coordinator')
    raise PopupException(_("Error submitting coordinator %s") % (coordinator,), detail=ex._headers.get('oozie-error-message', ex), error_code=200)


@check_editor_access_permission
def list_editor_bundles(request):
  if USE_NEW_EDITOR.get():
    docs = Document2.objects.documents(request.user).search_documents(types=['oozie-bundle2'])
    bundles = [doc.to_dict() for doc in docs]
  else:
    bundles = [d.content_object.to_dict() for d in Document.objects.get_docs(request.user, Document2, extra='bundle2')]

  bundles_v1 = [job.doc.get().to_dict() for job in Document.objects.available(OldBundle, request.user)]
  if bundles_v1:
    bundles.extend(bundles_v1)

  return render('editor2/list_editor_bundles.mako', request, {
    'bundles_json': json.dumps(bundles, cls=JSONEncoderForHTML),
  })


@check_editor_access_permission
@check_document_access_permission()
def edit_bundle(request):
  bundle_id = request.GET.get('bundle')
  doc = None

  if bundle_id:
    doc = Document2.objects.get(id=bundle_id)
    bundle = Bundle(document=doc)
  else:
    bundle = Bundle()
    bundle.set_workspace(request.user)

  if USE_NEW_EDITOR.get():
    coordinators = [dict([('id', d.id), ('uuid', d.uuid), ('name', d.name)])
                      for d in Document2.objects.documents(request.user).search_documents(types=['oozie-coordinator2'])]
  else:
    coordinators = [dict([('id', d.content_object.id), ('uuid', d.content_object.uuid), ('name', d.content_object.name)])
                      for d in Document.objects.get_docs(request.user, Document2, extra='coordinator2')]

  can_edit_json = doc is None or (doc.can_write(request.user) if USE_NEW_EDITOR.get() else doc.doc.get().is_editable(request.user))
  return render('editor2/bundle_editor.mako', request, {
      'bundle_json': bundle.to_json_for_html(),
      'coordinators_json': json.dumps(coordinators, cls=JSONEncoderForHTML),
      'doc_uuid': doc.uuid if doc else '',
      'is_embeddable': request.GET.get('is_embeddable', False),
      'can_edit_json': json.dumps(can_edit_json)
  })


@check_editor_access_permission
def new_bundle(request):
  return edit_bundle(request)


@check_editor_access_permission
def open_old_bundle(request):
  doc_id = request.GET.get('bundle')
  bundle_id = Document.objects.get(id=doc_id).object_id

  return old_edit_bundle(request, bundle=bundle_id)


@check_editor_access_permission
@check_document_modify_permission()
def save_bundle(request):
  response = {'status': -1}

  bundle_data = json.loads(request.POST.get('bundle', '{}'))

  if bundle_data.get('id'):
    bundle_doc = Document2.objects.get(id=bundle_data['id'])
  else:
    bundle_doc = Document2.objects.create(name=bundle_data['name'], uuid=bundle_data['uuid'], type='oozie-bundle2', owner=request.user)
    Document.objects.link(bundle_doc, owner=bundle_doc.owner, name=bundle_doc.name, description=bundle_doc.description, extra='bundle2')

  if bundle_data['coordinators']:
    dependencies = Document2.objects.filter(type='oozie-coordinator2', uuid__in=[c['coordinator'] for c in bundle_data['coordinators']])
    for doc in dependencies:
      doc._get_doc1(doc2_type='coordinator2').can_read_or_exception(request.user)
    bundle_doc.dependencies = dependencies

  bundle_doc1 = bundle_doc.doc.get()
  bundle_doc.update_data(bundle_data)
  bundle_doc.name = bundle_doc1.name = bundle_data['name']
  bundle_doc.description = bundle_doc1.description = bundle_data['properties']['description']
  bundle_doc.save()
  bundle_doc1.save()

  response['status'] = 0
  response['id'] = bundle_doc.id
  response['uuid'] = bundle_doc.uuid
  response['message'] = _('Saved !')

  return JsonResponse(response)


@check_editor_access_permission
@check_document_access_permission()
def copy_bundle(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  jobs = json.loads(request.POST.get('selection'))

  for job in jobs:
    doc2 = Document2.objects.get(type='oozie-bundle2', id=job['id'])
    doc = doc2.doc.get()

    name = doc2.name + '-copy'
    doc2 = doc2.copy(name=name, owner=request.user)

    doc.copy(content_object=doc2, name=name, owner=request.user)

    bundle = Bundle(document=doc2)
    bundle_data = bundle.get_data_for_json()
    bundle_data['name'] = name

    _import_workspace(request.fs, request.user, bundle)
    doc2.update_data(bundle_data)
    doc2.save()

  response = {}
  request.info(_('Bundle copied.') if len(jobs) > 1 else _('Bundle copied.'))

  return JsonResponse(response)


@check_editor_access_permission
@check_document_access_permission()
def submit_bundle(request, doc_id):
  bundle = Bundle(document=Document2.objects.get(id=doc_id))
  ParametersFormSet = formset_factory(ParameterForm, extra=0)

  if request.method == 'POST':
    params_form = ParametersFormSet(request.POST)

    if params_form.is_valid():
      mapping = dict([(param['name'], param['value']) for param in params_form.cleaned_data])
      job_id = _submit_bundle(request, bundle, mapping)

      jsonify = request.POST.get('format') == 'json'
      if jsonify:
        return JsonResponse({'status': 0, 'job_id': job_id, 'type': 'bundle'}, safe=False)
      else:
        request.info(_('Bundle submitted.'))
        return redirect(reverse('oozie:list_oozie_bundle', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s' % params_form.errors))
  else:
    parameters = bundle.find_all_parameters()
    initial_params = ParameterForm.get_initial_params(dict([(param['name'], param['value']) for param in parameters]))
    params_form = ParametersFormSet(initial=initial_params)

    return render('editor2/submit_job_popup.mako', request, {
                 'params_form': params_form,
                 'name': bundle.name,
                 'action': reverse('oozie:editor_submit_bundle',  kwargs={'doc_id': bundle.id}),
                 'return_json': request.GET.get('format') == 'json',
                 'show_dryrun': False
                }, force_template=True)


def _submit_bundle(request, bundle, properties):
  try:
    deployment_mapping = {}
    coords = dict([(c.uuid, c) for c in Document2.objects.filter(type='oozie-coordinator2', uuid__in=[b['coordinator'] for b in bundle.data['coordinators']])])

    for i, bundled in enumerate(bundle.data['coordinators']):
      coord = coords[bundled['coordinator']]
      workflow = Workflow(document=coord.dependencies.filter(type='oozie-workflow2')[0])
      wf_dir = Submission(request.user, workflow, request.fs, request.jt, properties).deploy()
      deployment_mapping['wf_%s_dir' % i] = request.fs.get_hdfs_path(wf_dir)

      coordinator = Coordinator(document=coord)
      coord_dir = Submission(request.user, coordinator, request.fs, request.jt, properties).deploy()
      deployment_mapping['coord_%s_dir' % i] = request.fs.get_hdfs_path(coord_dir)
      deployment_mapping['coord_%s' % i] = coord

      # Convert start/end dates of coordinator to server timezone
      for prop in bundled['properties']:
        if prop['name'] in ('end_date', 'start_date'):
          prop['value'] = convert_to_server_timezone(prop['value'], local_tz=coordinator.data['properties']['timezone'])

    properties.update(deployment_mapping)

    submission = Submission(request.user, bundle, request.fs, request.jt, properties=properties)
    job_id = submission.run()

    return job_id
  except RestException, ex:
    LOG.exception('Error submitting bundle')
    raise PopupException(_("Error submitting bundle %s") % (bundle,), detail=ex._headers.get('oozie-error-message', ex), error_code=200)
