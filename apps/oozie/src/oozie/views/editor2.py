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
import uuid

from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str
from desktop.lib.rest.http_client import RestException
from desktop.models import Document, Document2

from liboozie.credentials import Credentials
from liboozie.oozie_api import get_oozie
from liboozie.submission2 import Submission

from oozie.decorators import check_document_access_permission, check_document_modify_permission
from oozie.forms import ParameterForm
from oozie.models2 import Node, Workflow, Coordinator, Bundle, NODES, WORKFLOW_NODE_PROPERTIES, import_workflows_from_hue_3_7,\
    find_dollar_variables, find_dollar_braced_variables


LOG = logging.getLogger(__name__)



def list_editor_workflows(request):  
  workflows = [d.content_object.to_dict() for d in Document.objects.get_docs(request.user, Document2, extra='workflow2')]

  return render('editor/list_editor_workflows.mako', request, {
      'workflows_json': json.dumps(workflows)
  })


@check_document_access_permission()
def edit_workflow(request):
  workflow_id = request.GET.get('workflow')
  
  if workflow_id:
    wid = {}
    if workflow_id.isdigit():
      wid['id'] = workflow_id
    else:
      wid['uuid'] = workflow_id
    doc = Document2.objects.get(type='oozie-workflow2', **wid)
    workflow = Workflow(document=doc)
  else:
    doc = None
    workflow = Workflow()
    workflow.set_workspace(request.user)
    workflow.check_workspace(request.fs, request.user)
  
  workflow_data = workflow.get_data()

  api = get_oozie(request.user)
  credentials = Credentials()
  
  try:  
    credentials.fetch(api)
  except Exception, e:
    LOG.error(smart_str(e))

  return render('editor/workflow_editor.mako', request, {
      'layout_json': json.dumps(workflow_data['layout']),
      'workflow_json': json.dumps(workflow_data['workflow']),
      'credentials_json': json.dumps(credentials.credentials.keys()),
      'workflow_properties_json': json.dumps(WORKFLOW_NODE_PROPERTIES),
      'doc1_id': doc.doc.get().id if doc else -1,
      'subworkflows_json': json.dumps(_get_workflows(request.user)),
      'can_edit_json': json.dumps(doc is None or doc.doc.get().is_editable(request.user))
  })


def new_workflow(request):
  return edit_workflow(request)


def delete_workflow(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  jobs = json.loads(request.POST.get('selection'))

  for job in jobs:
    doc2 = Document2.objects.get(id=job['id'])
    doc = doc2.doc.get()
    doc.can_write_or_exception(request.user)
    
    doc.delete()
    doc2.delete()

  response = {}
  request.info(_('Workflows deleted.') if len(jobs) > 1 else _('Workflow deleted.'))
  
  return HttpResponse(json.dumps(response), mimetype="application/json")


@check_document_access_permission()
def copy_workflow(request):
  if request.method != 'POST':
    raise PopupException(_('A POST request is required.'))

  jobs = json.loads(request.POST.get('selection'))

  for job in jobs:
    doc2 = Document2.objects.get(type='oozie-workflow2', id=job['id'])
    
    name = doc2.name + '-copy'
    copy_doc = doc2.doc.get().copy(name=name, owner=request.user)
  
    doc2.pk = None
    doc2.id = None
    doc2.uuid = str(uuid.uuid4())
    doc2.name = name
    doc2.owner = request.user    
    doc2.save()
  
    doc2.doc.all().delete()
    doc2.doc.add(copy_doc)
    
    workflow = Workflow(document=doc2)
    workflow.update_name(name)
    doc2.update_data({'workflow': workflow.get_data()['workflow']})
    doc2.save()

    workflow.set_workspace(request.user)
    workflow.check_workspace(request.fs, request.user)

  response = {}  
  request.info(_('Workflows copied.') if len(jobs) > 1 else _('Workflow copied.'))

  return HttpResponse(json.dumps(response), mimetype="application/json")


@check_document_modify_permission()
def save_workflow(request):
  response = {'status': -1}

  workflow = json.loads(request.POST.get('workflow', '{}'))
  layout = json.loads(request.POST.get('layout', '{}'))

  if workflow.get('id'):
    workflow_doc = Document2.objects.get(id=workflow['id'])
  else:      
    workflow_doc = Document2.objects.create(name=workflow['name'], uuid=workflow['uuid'], type='oozie-workflow2', owner=request.user)
    Document.objects.link(workflow_doc, owner=workflow_doc.owner, name=workflow_doc.name, description=workflow_doc.description, extra='workflow2')

  subworkflows = [node['properties']['workflow'] for node in workflow['nodes'] if node['type'] == 'subworkflow-widget']
  if subworkflows:
    dependencies = Document2.objects.filter(uuid__in=subworkflows)
    workflow_doc.dependencies = dependencies

  workflow_doc.update_data({'workflow': workflow})
  workflow_doc.update_data({'layout': layout})
  workflow_doc.name = workflow['name']
  workflow_doc.save()
  
  workflow_instance = Workflow(document=workflow_doc)
  
  response['status'] = 0
  response['id'] = workflow_doc.id
  response['doc1_id'] = workflow_doc.doc.get().id
  response['message'] = _('Page saved !')

  return HttpResponse(json.dumps(response), mimetype="application/json")


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
  
  return HttpResponse(json.dumps(response), mimetype="application/json")


def _get_workflows(user):
  return [{
        'name': workflow.name,
        'owner': workflow.owner.username,
        'value': workflow.uuid,
        'id': workflow.id
      } for workflow in [d.content_object for d in Document.objects.get_docs(user, Document2, extra='workflow2')]
    ]  


def add_node(request):
  response = {'status': -1}

  node = json.loads(request.POST.get('node', '{}'))
  properties = json.loads(request.POST.get('properties', '{}'))
  copied_properties = json.loads(request.POST.get('copiedProperties', '{}'))

  _properties = dict(NODES[node['widgetType']].get_fields())
  _properties.update(dict([(_property['name'], _property['value']) for _property in properties]))

  if copied_properties:
    _properties.update(copied_properties)

  response['status'] = 0
  response['properties'] = _properties
  response['name'] = '%s-%s' % (node['widgetType'].split('-')[0], node['id'][:4])

  return HttpResponse(json.dumps(response), mimetype="application/json")


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
                
    response['status'] = 0
    response['parameters'] = list(parameters)
  except Exception, e:
    response['message'] = str(e)
    
  return HttpResponse(json.dumps(response), mimetype="application/json")


@check_document_access_permission()
def workflow_parameters(request):
  response = {'status': -1}

  try:
    workflow = Workflow(document=Document2.objects.get(type='oozie-workflow2', uuid=request.GET.get('uuid'))) 

    response['status'] = 0
    response['parameters'] = workflow.find_all_parameters(with_lib_path=False)
  except Exception, e:
    response['message'] = str(e)
    
  return HttpResponse(json.dumps(response), mimetype="application/json")


def gen_xml_workflow(request):
  response = {'status': -1}

  try:
    workflow_json = json.loads(request.POST.get('workflow', '{}'))
  
    workflow = Workflow(workflow=workflow_json)
  
    response['status'] = 0
    response['xml'] = workflow.to_xml()
  except Exception, e:
    response['message'] = str(e)
    
  return HttpResponse(json.dumps(response), mimetype="application/json")


@check_document_access_permission()
def submit_workflow(request, doc_id):
  workflow = Workflow(document=Document2.objects.get(id=doc_id))
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
                     'action': reverse('oozie:editor_submit_workflow', kwargs={'doc_id': workflow.id})
                   }, force_template=True).content
    return HttpResponse(json.dumps(popup), mimetype="application/json")


def _submit_workflow(user, fs, jt, workflow, mapping):
  try:
    submission = Submission(user, workflow, fs, jt, mapping)
    job_id = submission.run()
    return job_id
  except RestException, ex:
    detail = ex._headers.get('oozie-error-message', ex)
    if 'Max retries exceeded with url' in str(detail):
      detail = '%s: %s' % (_('The Oozie server is not running'), detail)
    LOG.error(smart_str(detail))
    raise PopupException(_("Error submitting workflow %s") % (workflow,), detail=detail)

  return redirect(reverse('oozie:list_oozie_workflow', kwargs={'job_id': job_id}))



def list_editor_coordinators(request):
  coordinators = [d.content_object for d in Document.objects.get_docs(request.user, Document2, extra='coordinator2')]

  return render('editor/list_editor_coordinators.mako', request, {
      'coordinators': coordinators
  })


@check_document_access_permission()
def edit_coordinator(request):
  coordinator_id = request.GET.get('coordinator')
  doc = None
  
  if coordinator_id:
    doc = Document2.objects.get(id=coordinator_id)
    coordinator = Coordinator(document=doc)
  else:
    coordinator = Coordinator()

  api = get_oozie(request.user)
  credentials = Credentials()
  
  try:  
    credentials.fetch(api)
  except Exception, e:
    LOG.error(smart_str(e))

  workflows = [dict([('uuid', d.content_object.uuid), ('name', d.content_object.name)])
                                    for d in Document.objects.get_docs(request.user, Document2, extra='workflow2')]

  if coordinator_id and not filter(lambda a: a['uuid'] == coordinator.data['properties']['workflow'], workflows):
    raise PopupException(_('You don\'t have access to the workflow of this coordinator.'))

  return render('editor/coordinator_editor.mako', request, {
      'coordinator_json': coordinator.json,
      'credentials_json': json.dumps(credentials.credentials.keys()),
      'workflows_json': json.dumps(workflows),
      'doc1_id': doc.doc.get().id if doc else -1,
      'can_edit_json': json.dumps(doc is None or doc.doc.get().is_editable(request.user))
  })


def new_coordinator(request):
  return edit_coordinator(request)


@check_document_modify_permission()
def save_coordinator(request):
  response = {'status': -1}

  coordinator_data = json.loads(request.POST.get('coordinator', '{}'))

  if coordinator_data.get('id'):
    coordinator_doc = Document2.objects.get(id=coordinator_data['id'])
  else:      
    coordinator_doc = Document2.objects.create(name=coordinator_data['name'], uuid=coordinator_data['uuid'], type='oozie-coordinator2', owner=request.user)
    Document.objects.link(coordinator_doc, owner=coordinator_doc.owner, name=coordinator_doc.name, description=coordinator_doc.description, extra='coordinator2')

  if coordinator_data['properties']['workflow']:
    dependencies = Document2.objects.filter(type='oozie-workflow2', uuid=coordinator_data['properties']['workflow'])
    for doc in dependencies:
      doc.doc.get().can_read_or_exception(request.user)
    coordinator_doc.dependencies = dependencies

  coordinator_doc.update_data(coordinator_data)
  coordinator_doc.name = coordinator_data['name']
  coordinator_doc.save()
  
  response['status'] = 0
  response['id'] = coordinator_doc.id
  response['message'] = _('Saved !')

  return HttpResponse(json.dumps(response), mimetype="application/json")


def gen_xml_coordinator(request):
  response = {'status': -1}

  coordinator_dict = json.loads(request.POST.get('coordinator', '{}'))

  coordinator = Coordinator(data=coordinator_dict)

  response['status'] = 0
  response['xml'] = coordinator.to_xml()
    
  return HttpResponse(json.dumps(response), mimetype="application/json") 


@check_document_access_permission()
def submit_coordinator(request, doc_id):
  coordinator = Coordinator(document=Document2.objects.get(id=doc_id))  
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
                 'action': reverse('oozie:editor_submit_coordinator',  kwargs={'doc_id': coordinator.id})
                }, force_template=True).content
  return HttpResponse(json.dumps(popup), mimetype="application/json")


def _submit_coordinator(request, coordinator, mapping):
  try:
    wf_doc = Document2.objects.get(uuid=coordinator.data['properties']['workflow'])
    wf_dir = Submission(request.user, Workflow(document=wf_doc), request.fs, request.jt, mapping).deploy()

    properties = {'wf_application_path': request.fs.get_hdfs_path(wf_dir)}
    properties.update(mapping)

    submission = Submission(request.user, coordinator, request.fs, request.jt, properties=properties)
    job_id = submission.run()

    return job_id
  except RestException, ex:
    raise PopupException(_("Error submitting coordinator %s") % (coordinator,),
                         detail=ex._headers.get('oozie-error-message', ex))
    
    
    

def list_editor_bundles(request):
  bundles = [d.content_object for d in Document.objects.get_docs(request.user, Document2, extra='bundle2')]

  return render('editor/list_editor_bundles.mako', request, {
      'bundles': bundles
  })


@check_document_access_permission()
def edit_bundle(request):
  bundle_id = request.GET.get('bundle')
  doc = None
  
  if bundle_id:
    doc = Document2.objects.get(id=bundle_id)
    bundle = Bundle(document=doc)
  else:
    bundle = Bundle()

  coordinators = [dict([('uuid', d.content_object.uuid), ('name', d.content_object.name)])
                      for d in Document.objects.get_docs(request.user, Document2, extra='coordinator2')]

  return render('editor/bundle_editor.mako', request, {
      'bundle_json': bundle.json,
      'coordinators_json': json.dumps(coordinators),
      'doc1_id': doc.doc.get().id if doc else -1,
      'can_edit_json': json.dumps(doc is None or doc.doc.get().is_editable(request.user))      
  })


def new_bundle(request):
  return edit_bundle(request)


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
      doc.doc.get().can_read_or_exception(request.user)    
    bundle_doc.dependencies = dependencies

  bundle_doc.update_data(bundle_data)
  bundle_doc.name = bundle_data['name']
  bundle_doc.save()
  
  response['status'] = 0
  response['id'] = bundle_doc.id
  response['message'] = _('Saved !')

  return HttpResponse(json.dumps(response), mimetype="application/json")


@check_document_access_permission()
def submit_bundle(request, doc_id):
  bundle = Bundle(document=Document2.objects.get(id=doc_id))  
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
                 'action': reverse('oozie:editor_submit_bundle',  kwargs={'doc_id': bundle.id})
                }, force_template=True).content
  return HttpResponse(json.dumps(popup), mimetype="application/json")


def _submit_bundle(request, bundle, properties):
  try:
    deployment_mapping = {}
    coords = dict([(c.uuid, c) for c in Document2.objects.filter(type='oozie-coordinator2', uuid__in=[b['coordinator'] for b in bundle.data['coordinators']])])
    
    for i, bundled in enumerate(bundle.data['coordinators']):
      coord = coords[bundled['coordinator']]
      workflow = Workflow(document=coord.dependencies.all()[0])
      wf_dir = Submission(request.user, workflow, request.fs, request.jt, properties).deploy()      
      deployment_mapping['wf_%s_dir' % i] = request.fs.get_hdfs_path(wf_dir)
      
      coordinator = Coordinator(document=coord)
      coord_dir = Submission(request.user, coordinator, request.fs, request.jt, properties).deploy()
      deployment_mapping['coord_%s_dir' % i] = coord_dir
      deployment_mapping['coord_%s' % i] = coord

    properties.update(deployment_mapping)
    
    submission = Submission(request.user, bundle, request.fs, request.jt, properties=properties)
    job_id = submission.run()

    return job_id
  except RestException, ex:
    raise PopupException(_("Error submitting bundle %s") % (bundle,), detail=ex._headers.get('oozie-error-message', ex))

