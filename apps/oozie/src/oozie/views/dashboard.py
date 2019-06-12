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
import os
import re
import time
import urllib

from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.utils.functional import wraps
from django.utils.translation import ugettext as _
from django.urls import reverse
from django.shortcuts import redirect

from desktop.conf import TIME_ZONE
from desktop.lib import django_mako
from desktop.lib.django_util import JsonResponse, render
from desktop.lib.json_utils import JSONEncoderForHTML
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str, smart_unicode
from desktop.lib.paths import SAFE_CHARACTERS_URI_COMPONENTS
from desktop.lib.rest.http_client import RestException
from desktop.lib.view_util import format_duration_in_millis
from desktop.log.access import access_warn
from desktop.models import Document, Document2

from hadoop.fs.hadoopfs import Hdfs
from liboozie.credentials import Credentials
from liboozie.oozie_api import get_oozie
from liboozie.submission2 import Submission
from liboozie.utils import catch_unicode_time

from oozie.conf import OOZIE_JOBS_COUNT, ENABLE_CRON_SCHEDULING, ENABLE_V2, ENABLE_OOZIE_BACKEND_FILTERING
from oozie.forms import RerunForm, ParameterForm, RerunCoordForm, RerunBundleForm, UpdateCoordinatorForm
from oozie.models import Workflow as OldWorkflow, Job, utc_datetime_format, Bundle, Coordinator, get_link, History as OldHistory
from oozie.models2 import History, Workflow, WORKFLOW_NODE_PROPERTIES
from oozie.settings import DJANGO_APPS
from oozie.utils import convert_to_server_timezone

from desktop.auth.backend import is_admin

def get_history():
  if ENABLE_V2.get():
    return History
  else:
    return OldHistory

def get_workflow():
  if ENABLE_V2.get():
    return Workflow
  else:
    return OldWorkflow


LOG = logging.getLogger(__name__)


"""
Permissions:

A Workflow/Coordinator/Bundle can:
  * be accessed only by its owner or a superuser or by a user with 'dashboard_jobs_access' permissions
  * be submitted/modified only by its owner or a superuser

Permissions checking happens by calling:
  * check_job_access_permission()
  * check_job_edition_permission()
"""

def _get_workflows(user):
  return [{
        'name': workflow.name,
        'owner': workflow.owner.username,
        'value': workflow.uuid,
        'id': workflow.id
      } for workflow in [d.content_object for d in Document.objects.get_docs(user, Document2, extra='workflow2')]
    ]


def manage_oozie_jobs(request, job_id, action):
  if request.method != 'POST':
    raise PopupException(_('Use a POST request to manage an Oozie job.'))

  job = check_job_access_permission(request, job_id)
  check_job_edition_permission(job, request.user)

  response = {'status': -1, 'data': ''}

  try:
    oozie_api = get_oozie(request.user)
    params = None

    if action == 'change':
      pause_time_val = request.POST.get('pause_time')
      if request.POST.get('clear_pause_time') == 'true':
        pause_time_val = ''

      end_time_val = request.POST.get('end_time')
      if end_time_val:
        end_time_val = convert_to_server_timezone(end_time_val, TIME_ZONE.get())
      if pause_time_val:
        pause_time_val = convert_to_server_timezone(pause_time_val, TIME_ZONE.get())
      params = {'value': 'endtime=%s' % (end_time_val) + ';'
                            'pausetime=%s' % (pause_time_val) + ';'
                            'concurrency=%s' % (request.POST.get('concurrency'))}
    elif action == 'ignore':
      oozie_api = get_oozie(request.user, api_version="v2")
      params = {
        'type': 'action',
        'scope': ','.join(job.aggreate(request.POST.get('actions').split())),
      }

    response['data'] = oozie_api.job_control(job_id, action, parameters=params)

    response['status'] = 0
    if 'notification' in request.POST:
      request.info(_(request.POST.get('notification')))
  except RestException, ex:
    ex_message = ex.message
    if ex._headers.get('oozie-error-message'):
      ex_message = ex._headers.get('oozie-error-message')
    msg = "Error performing %s on Oozie job %s: %s." % (action, job_id, ex_message)
    LOG.exception(msg)

    response['data'] = _(msg)

  return JsonResponse(response)


def bulk_manage_oozie_jobs(request):
  if request.method != 'POST':
    raise PopupException(_('Use a POST request to manage the Oozie jobs.'))

  response = {'status': -1, 'data': ''}

  if 'job_ids' in request.POST and 'action' in request.POST:
    jobs = request.POST.get('job_ids').split()
    response = {'totalRequests': len(jobs), 'totalErrors': 0, 'messages': ''}

    oozie_api = get_oozie(request.user)

    for job_id in jobs:
      job = check_job_access_permission(request, job_id)
      check_job_edition_permission(job, request.user)
      try:
        oozie_api.job_control(job_id, request.POST.get('action'))
      except RestException, ex:
        LOG.exception("Error performing bulk operation for job_id=%s", job_id)

        response['totalErrors'] = response['totalErrors'] + 1
        response['messages'] += str(ex)

  return JsonResponse(response)


def show_oozie_error(view_func):
  def decorate(request, *args, **kwargs):
    try:
      return view_func(request, *args, **kwargs)
    except RestException, ex:
      LOG.exception("Error communicating with Oozie in %s", view_func.__name__)

      detail = ex._headers.get('oozie-error-message', ex)
      if 'Max retries exceeded with url' in str(detail) or 'Connection refused' in str(detail):
        detail = _('The Oozie server is not running')
      raise PopupException(_('An error occurred with Oozie.'), detail=detail)
  return wraps(view_func)(decorate)


@show_oozie_error
def list_oozie_workflows(request):
  kwargs = {'cnt': OOZIE_JOBS_COUNT.get(), 'filters': []}
  if not has_dashboard_jobs_access(request.user):
    kwargs['filters'].append(('user', request.user.username))
  oozie_api = get_oozie(request.user)

  if request.GET.get('format') == 'json':
    just_sla = request.GET.get('justsla') == 'true'

    if request.GET.get('startcreatedtime'):
      kwargs['filters'].extend([('startcreatedtime', request.GET.get('startcreatedtime'))])

    if request.GET.get('text') and ENABLE_OOZIE_BACKEND_FILTERING.get():
      kwargs['filters'].extend([('text', request.GET.get('text'))])

    if request.GET.get('offset'):
      kwargs['offset'] = request.GET.get('offset')

    json_jobs = []
    total_jobs = 0
    if request.GET.getlist('status'):
      kwargs['filters'].extend([('status', status) for status in request.GET.getlist('status')])
      wf_list = oozie_api.get_workflows(**kwargs)
      json_jobs = wf_list.jobs
      total_jobs = wf_list.total

    if request.GET.get('type') == 'progress':
      json_jobs = [oozie_api.get_job(job.id) for job in json_jobs]

    response = massaged_oozie_jobs_for_json(json_jobs, request.user, just_sla)
    response['total_jobs'] = total_jobs
    return JsonResponse(response, encoder=JSONEncoderForHTML)

  return render('dashboard/list_oozie_workflows.mako', request, {
    'user': request.user,
    'jobs': [],
    'has_job_edition_permission':  has_job_edition_permission,
  })


@show_oozie_error
def list_oozie_coordinators(request):
  kwargs = {'cnt': OOZIE_JOBS_COUNT.get(), 'filters': []}
  if not has_dashboard_jobs_access(request.user):
    kwargs['filters'].append(('user', request.user.username))
  oozie_api = get_oozie(request.user)

  enable_cron_scheduling = ENABLE_CRON_SCHEDULING.get()

  if request.GET.get('format') == 'json':
    if request.GET.get('offset'):
      kwargs['offset'] = request.GET.get('offset')

    if request.GET.get('text') and ENABLE_OOZIE_BACKEND_FILTERING.get():
      kwargs['filters'].extend([('text', request.GET.get('text'))])

    json_jobs = []
    total_jobs = 0
    if request.GET.getlist('status'):
      kwargs['filters'].extend([('status', status) for status in request.GET.getlist('status')])
      co_list = oozie_api.get_coordinators(**kwargs)
      json_jobs = co_list.jobs
      total_jobs = co_list.total

    if request.GET.get('type') == 'progress':
      json_jobs = [oozie_api.get_coordinator(job.id) for job in json_jobs]

    response = massaged_oozie_jobs_for_json(json_jobs, request.user)
    response['total_jobs'] = total_jobs
    return JsonResponse(response, encoder=JSONEncoderForHTML)

  return render('dashboard/list_oozie_coordinators.mako', request, {
    'jobs': [],
    'has_job_edition_permission': has_job_edition_permission,
    'enable_cron_scheduling': enable_cron_scheduling,
  })


@show_oozie_error
def list_oozie_bundles(request):
  kwargs = {'cnt': OOZIE_JOBS_COUNT.get(), 'filters': []}
  if not has_dashboard_jobs_access(request.user):
    kwargs['filters'].append(('user', request.user.username))
  oozie_api = get_oozie(request.user)

  if request.GET.get('format') == 'json':
    if request.GET.get('offset'):
      kwargs['offset'] = request.GET.get('offset')

    if request.GET.get('text') and ENABLE_OOZIE_BACKEND_FILTERING.get():
      kwargs['filters'].extend([('text', request.GET.get('text'))])

    json_jobs = []
    total_jobs = 0
    if request.GET.getlist('status'):
      kwargs['filters'].extend([('status', status) for status in request.GET.getlist('status')])
      bundle_list = oozie_api.get_bundles(**kwargs)
      json_jobs = bundle_list.jobs
      total_jobs = bundle_list.total

    if request.GET.get('type') == 'progress':
      json_jobs = [oozie_api.get_coordinator(job.id) for job in json_jobs]

    response = massaged_oozie_jobs_for_json(json_jobs, request.user)
    response['total_jobs'] = total_jobs
    return JsonResponse(response, encoder=JSONEncoderForHTML)


  return render('dashboard/list_oozie_bundles.mako', request, {
    'jobs': [],
    'has_job_edition_permission': has_job_edition_permission,
  })


@show_oozie_error
def list_oozie_workflow(request, job_id):
  oozie_workflow = check_job_access_permission(request, job_id)

  oozie_coordinator = None
  if request.GET.get('coordinator_job_id'):
    oozie_coordinator = check_job_access_permission(request, request.GET.get('coordinator_job_id'))

  oozie_bundle = None
  if request.GET.get('bundle_job_id'):
    oozie_bundle = check_job_access_permission(request, request.GET.get('bundle_job_id'))

  if oozie_coordinator is not None:
    setattr(oozie_workflow, 'oozie_coordinator', oozie_coordinator)
  if oozie_bundle is not None:
    setattr(oozie_workflow, 'oozie_bundle', oozie_bundle)

  oozie_parent = oozie_workflow.get_parent_job_id()
  if oozie_parent:
    oozie_parent = check_job_access_permission(request, oozie_parent)

  workflow_data = {}
  credentials = None
  doc = None
  hue_workflow = None
  hue_coord = None
  workflow_graph = 'MISSING'  # default to prevent loading the graph tab for deleted workflows
  full_node_list = None

  if ENABLE_V2.get():
    try:
      # To update with the new History document model
      hue_coord = get_history().get_coordinator_from_config(oozie_workflow.conf_dict)
      hue_workflow = get_history().get_workflow_from_config(oozie_workflow.conf_dict)
      # When a workflow is submitted by a coordinator
      if not hue_workflow and hue_coord and hue_coord.workflow.document:
        hue_workflow = hue_coord.workflow

      if hue_coord and hue_coord.workflow and hue_coord.workflow.document: hue_coord.workflow.document.doc.get().can_read_or_exception(request.user)
      if hue_workflow: hue_workflow.document.doc.get().can_read_or_exception(request.user)

      if hue_workflow:
        full_node_list = hue_workflow.nodes
        workflow_id = hue_workflow.id
        wid = {
          'id': workflow_id
        }
        doc = Document2.objects.get(type='oozie-workflow2', **wid)
        new_workflow = get_workflow()(document=doc)
        workflow_data = new_workflow.get_data()

    except Exception, e:
      LOG.exception("Error generating full page for running workflow %s with exception: %s" % (job_id, e.message))
    finally:
      workflow_graph = ''
      credentials = Credentials()
      if not workflow_data.get('layout') or oozie_workflow.conf_dict.get('submit_single_action'):
        try:
          workflow_data = Workflow.gen_workflow_data_from_xml(request.user, oozie_workflow)
          # Hide graph tab when node count > 30
          if workflow_data.get('workflow') and len(workflow_data.get('workflow')['nodes']) > 30:
            workflow_data = {}
        except Exception, e:
          LOG.exception('Graph data could not be generated from Workflow %s: %s' % (oozie_workflow.id, e))
  else:
    history = get_history().cross_reference_submission_history(request.user, job_id)

    hue_coord = history and history.get_coordinator() or get_history().get_coordinator_from_config(oozie_workflow.conf_dict)
    hue_workflow = (hue_coord and hue_coord.workflow) or (history and history.get_workflow()) or get_history().get_workflow_from_config(oozie_workflow.conf_dict)

    if hue_coord and hue_coord.workflow: Job.objects.can_read_or_exception(request, hue_coord.workflow.id)
    if hue_workflow: Job.objects.can_read_or_exception(request, hue_workflow.id)

    if hue_workflow:
      workflow_graph = hue_workflow.gen_status_graph(oozie_workflow)
      full_node_list = hue_workflow.node_list
    else:
      workflow_graph, full_node_list = get_workflow().gen_status_graph_from_xml(request.user, oozie_workflow)

  parameters = oozie_workflow.conf_dict.copy()

  for action in oozie_workflow.actions:
    action.oozie_coordinator = oozie_coordinator
    action.oozie_bundle = oozie_bundle


  if request.GET.get('format') == 'json':
    if not workflow_graph and request.GET.get('is_jb2'):
      workflow_graph = django_mako.render_to_string('dashboard/list_oozie_workflow_graph.mako', {})
    return_obj = {
      'id': oozie_workflow.id,
      'status':  oozie_workflow.status,
      'progress': oozie_workflow.get_progress(full_node_list),
      'graph': workflow_graph,
      'actions': massaged_workflow_actions_for_json(oozie_workflow.get_working_actions(), oozie_coordinator, oozie_bundle),
      'doc_url': doc.get_absolute_url() if doc else '',
    }
    return JsonResponse(return_obj, encoder=JSONEncoderForHTML)

  if request.GET.get('format') == 'svg':
    oozie_api = get_oozie(request.user, api_version="v2")
    svg_data = oozie_api.get_job_graph(job_id)
    return HttpResponse(svg_data)

  if request.GET.get('graph'):
    return render('dashboard/list_oozie_workflow_graph.mako', request, {
      'oozie_workflow': oozie_workflow,
      'workflow_graph': workflow_graph,
      'layout_json': json.dumps(workflow_data.get('layout', ''), cls=JSONEncoderForHTML) if workflow_data else '',
      'workflow_json': json.dumps(workflow_data.get('workflow', ''), cls=JSONEncoderForHTML) if workflow_data else '',
      'credentials_json': json.dumps(credentials.credentials.keys(), cls=JSONEncoderForHTML) if credentials else '',
      'workflow_properties_json': json.dumps(WORKFLOW_NODE_PROPERTIES, cls=JSONEncoderForHTML),
      'doc_uuid': doc.uuid if doc else '',
      'graph_element_id': request.GET.get('element') if request.GET.get('element') else 'loaded ' + doc.uuid + ' graph',
      'subworkflows_json': json.dumps(_get_workflows(request.user), cls=JSONEncoderForHTML),
      'can_edit_json': json.dumps(doc is None or doc.doc.get().is_editable(request.user)),
      'is_jb2': request.GET.get('is_jb2', False)
    })

  oozie_slas = []
  if oozie_workflow.has_sla:
    oozie_api = get_oozie(request.user, api_version="v2")
    params = {
      'id': oozie_workflow.id,
      'parent_id': oozie_workflow.id
    }
    oozie_slas = oozie_api.get_oozie_slas(**params)

  return render('dashboard/list_oozie_workflow.mako', request, {
    'oozie_workflow': oozie_workflow,
    'oozie_coordinator': oozie_coordinator,
    'oozie_bundle': oozie_bundle,
    'oozie_parent': oozie_parent,
    'oozie_slas': oozie_slas,
    'hue_workflow': hue_workflow,
    'hue_coord': hue_coord,
    'parameters': dict((var, val) for var, val in parameters.iteritems() if var not in ParameterForm.NON_PARAMETERS and var != 'oozie.use.system.libpath' or var == 'oozie.wf.application.path'),
    'has_job_edition_permission': has_job_edition_permission,
    'workflow_graph': workflow_graph,
    'layout_json': json.dumps(workflow_data.get('layout', ''), cls=JSONEncoderForHTML) if workflow_data else '',
    'workflow_json': json.dumps(workflow_data.get('workflow', ''), cls=JSONEncoderForHTML) if workflow_data else '',
    'credentials_json': json.dumps(credentials.credentials.keys(), cls=JSONEncoderForHTML) if credentials else '',
    'workflow_properties_json': json.dumps(WORKFLOW_NODE_PROPERTIES, cls=JSONEncoderForHTML),
    'doc_uuid': doc.uuid if doc else '',
    'subworkflows_json': json.dumps(_get_workflows(request.user), cls=JSONEncoderForHTML),
    'can_edit_json': json.dumps(doc is None or doc.doc.get().is_editable(request.user))
  })


@show_oozie_error
def list_oozie_coordinator(request, job_id):
  kwargs = {'cnt': 50, 'filters': []}
  kwargs['offset'] = request.GET.get('offset', 1)
  if request.GET.getlist('status'):
      kwargs['filters'].extend([('status', status) for status in request.GET.getlist('status')])

  oozie_coordinator = check_job_access_permission(request, job_id, **kwargs)

  # Cross reference the submission history (if any)
  coordinator = get_history().get_coordinator_from_config(oozie_coordinator.conf_dict)
  try:
    if not ENABLE_V2.get():
      coordinator = get_history().objects.get(oozie_job_id=job_id).job.get_full_node()
  except:
    LOG.exception("Ignoring error getting oozie job coordinator for job_id=%s", job_id)

  oozie_bundle = None
  if request.GET.get('bundle_job_id'):
    try:
      oozie_bundle = check_job_access_permission(request, request.GET.get('bundle_job_id'))
    except:
      LOG.exception("Ignoring error getting oozie bundle for job_id=%s", job_id)

  if request.GET.get('format') == 'json':
    actions = massaged_coordinator_actions_for_json(oozie_coordinator, oozie_bundle)

    return_obj = {
      'id': oozie_coordinator.id,
      'status':  oozie_coordinator.status,
      'progress': oozie_coordinator.get_progress(),
      'nextTime': format_time(oozie_coordinator.nextMaterializedTime),
      'endTime': format_time(oozie_coordinator.endTime),
      'actions': actions,
      'total_actions': oozie_coordinator.total,
      'doc_url': coordinator.get_absolute_url() if coordinator else '',
    }
    return JsonResponse(return_obj, encoder=JSONEncoderForHTML)

  oozie_slas = []
  if oozie_coordinator.has_sla:
    oozie_api = get_oozie(request.user, api_version="v2")
    params = {
      'id': oozie_coordinator.id,
      'parent_id': oozie_coordinator.id
    }
    oozie_slas = oozie_api.get_oozie_slas(**params)

  enable_cron_scheduling = ENABLE_CRON_SCHEDULING.get()
  update_coord_form = UpdateCoordinatorForm(oozie_coordinator=oozie_coordinator)

  return render('dashboard/list_oozie_coordinator.mako', request, {
    'oozie_coordinator': oozie_coordinator,
    'oozie_slas': oozie_slas,
    'coordinator': coordinator,
    'oozie_bundle': oozie_bundle,
    'has_job_edition_permission': has_job_edition_permission,
    'enable_cron_scheduling': enable_cron_scheduling,
    'update_coord_form': update_coord_form,
  })


@show_oozie_error
def list_oozie_bundle(request, job_id):
  oozie_bundle = check_job_access_permission(request, job_id)

  # Cross reference the submission history (if any)
  bundle = None
  try:
    if ENABLE_V2.get():
      bundle = get_history().get_bundle_from_config(oozie_bundle.conf_dict)
    else:
      bundle = get_history().objects.get(oozie_job_id=job_id).job.get_full_node()
  except:
    LOG.exception("Ignoring error getting oozie job bundle for job_id=%s", job_id)

  if request.GET.get('format') == 'json':
    return_obj = {
      'id': oozie_bundle.id,
      'user': oozie_bundle.user,
      'name': oozie_bundle.bundleJobName,
      'status':  oozie_bundle.status,
      'progress': oozie_bundle.get_progress(),
      'endTime': format_time(oozie_bundle.endTime),
      'actions': massaged_bundle_actions_for_json(oozie_bundle),
      'submitted': format_time(oozie_bundle.kickoffTime),
      'doc_url': bundle.get_absolute_url() if bundle else '',
      'canEdit': has_job_edition_permission(oozie_bundle, request.user),
    }
    return HttpResponse(json.dumps(return_obj).replace('\\\\', '\\'), content_type="application/json")

  return render('dashboard/list_oozie_bundle.mako', request, {
    'oozie_bundle': oozie_bundle,
    'bundle': bundle,
    'has_job_edition_permission': has_job_edition_permission,
  })


@show_oozie_error
def list_oozie_workflow_action(request, action):
  try:
    action = get_oozie(request.user).get_action(action)
    workflow = check_job_access_permission(request, action.id.split('@')[0])
  except RestException, ex:
    msg = _("Error accessing Oozie action %s.") % (action,)
    LOG.exception(msg)

    raise PopupException(msg, detail=ex.message)

  oozie_coordinator = None
  if request.GET.get('coordinator_job_id'):
    oozie_coordinator = check_job_access_permission(request, request.GET.get('coordinator_job_id'))

  oozie_bundle = None
  if request.GET.get('bundle_job_id'):
    oozie_bundle = check_job_access_permission(request, request.GET.get('bundle_job_id'))

  workflow.oozie_coordinator = oozie_coordinator
  workflow.oozie_bundle = oozie_bundle

  oozie_parent = workflow.get_parent_job_id()
  if oozie_parent:
    oozie_parent = check_job_access_permission(request, oozie_parent)

  return render('dashboard/list_oozie_workflow_action.mako', request, {
    'action': action,
    'workflow': workflow,
    'oozie_coordinator': oozie_coordinator,
    'oozie_bundle': oozie_bundle,
    'oozie_parent': oozie_parent,
  })


@show_oozie_error
def get_oozie_job_log(request, job_id):
  oozie_api = get_oozie(request.user, api_version="v2")
  check_job_access_permission(request, job_id)
  kwargs = {'logfilter' : []}

  if request.GET.get('format') == 'json':
    if request.GET.get('recent'):
      kwargs['logfilter'].extend([('recent', val) for val in request.GET.get('recent').split(':')])
    if request.GET.get('limit'):
      kwargs['logfilter'].extend([('limit', request.GET.get('limit'))])
    if request.GET.get('loglevel'):
      kwargs['logfilter'].extend([('loglevel', request.GET.get('loglevel'))])
    if request.GET.get('text'):
      kwargs['logfilter'].extend([('text', request.GET.get('text'))])

  status_resp = oozie_api.get_job_status(job_id)
  log = oozie_api.get_job_log(job_id, **kwargs)

  return_obj = {
    'id': job_id,
    'status': status_resp['status'],
    'log': log,
  }

  return JsonResponse(return_obj, encoder=JSONEncoderForHTML)


@show_oozie_error
def list_oozie_info(request):
  api = get_oozie(request.user)

  configuration = api.get_configuration()
  oozie_status = api.get_oozie_status()
  instrumentation = {}
  metrics = {}

  if 'org.apache.oozie.service.MetricsInstrumentationService' in [c.strip() for c in configuration.get('oozie.services.ext', '').split(',')]:
    api2 = get_oozie(request.user, api_version="v2")
    metrics = api2.get_metrics()
  else:
    instrumentation = api.get_instrumentation()

  return render('dashboard/list_oozie_info.mako', request, {
    'instrumentation': instrumentation,
    'metrics': metrics,
    'configuration': configuration,
    'oozie_status': oozie_status,
    'is_embeddable': request.GET.get('is_embeddable', False),
  })


@show_oozie_error
def list_oozie_sla(request):
  oozie_api = get_oozie(request.user, api_version="v2")

  if request.method == 'POST':
    params = {}

    job_name = request.POST.get('job_name')

    if re.match('.*-oozie-\w+-[WCB]', job_name):
      params['id'] = job_name
      params['parent_id'] = job_name
    else:
      params['app_name'] = job_name

    if 'useDates' in request.POST:
      if request.POST.get('start'):
        params['nominal_start'] = request.POST.get('start')
      if request.POST.get('end'):
        params['nominal_end'] = request.POST.get('end')

    oozie_slas = oozie_api.get_oozie_slas(**params)

  else:
    oozie_slas = [] # or get latest?

  if request.GET.get('format') == 'json':
    massaged_slas = []
    for sla in oozie_slas:
      massaged_slas.append(massaged_sla_for_json(sla))

    return HttpResponse(json.dumps({'oozie_slas': massaged_slas}), content_type="text/json")

  configuration = oozie_api.get_configuration()
  show_slas_hint = 'org.apache.oozie.sla.service.SLAService' not in configuration.get('oozie.services.ext', '')

  return render('dashboard/list_oozie_sla.mako', request, {
    'oozie_slas': oozie_slas,
    'show_slas_hint': show_slas_hint,
    'is_embeddable': request.GET.get('is_embeddable', False),
  })


def massaged_sla_for_json(sla):
  massaged_sla = {
    'slaStatus': sla['slaStatus'],
    'id': sla['id'],
    'appType': sla['appType'],
    'appName': sla['appName'],
    'appUrl': get_link(sla['id']),
    'user': sla['user'],
    'nominalTime': sla['nominalTime'],
    'expectedStart': sla['expectedStart'],
    'actualStart': sla['actualStart'],
    'expectedEnd': sla['expectedEnd'],
    'actualEnd': sla['actualEnd'],
    'jobStatus': sla['jobStatus'],
    'expectedDuration': sla['expectedDuration'],
    'actualDuration': sla['actualDuration'],
    'lastModified': sla['lastModified']
  }

  return massaged_sla


@show_oozie_error
def sync_coord_workflow(request, job_id):
  ParametersFormSet = formset_factory(ParameterForm, extra=0)
  job = check_job_access_permission(request, job_id)
  check_job_edition_permission(job, request.user)

  hue_coord = get_history().get_coordinator_from_config(job.conf_dict)
  hue_wf = (hue_coord and hue_coord.workflow) or get_history().get_workflow_from_config(job.conf_dict)
  wf_application_path = job.conf_dict.get('wf_application_path') and Hdfs.urlsplit(job.conf_dict['wf_application_path'])[2] or ''
  coord_application_path = job.conf_dict.get('oozie.coord.application.path') and Hdfs.urlsplit(job.conf_dict['oozie.coord.application.path'])[2] or ''
  properties = hue_coord and hue_coord.properties and dict([(param['name'], param['value']) for param in hue_coord.properties]) or None

  if request.method == 'POST':
    params_form = ParametersFormSet(request.POST)
    if params_form.is_valid():
      mapping = dict([(param['name'], param['value']) for param in params_form.cleaned_data])

      # Update workflow params in coordinator
      hue_coord.clear_workflow_params()
      properties = dict([(param['name'], param['value']) for param in hue_coord.properties])

      # Deploy WF XML
      submission = Submission(user=request.user, job=hue_wf, fs=request.fs, jt=request.jt, properties=properties)
      submission.deploy(deployment_dir=wf_application_path)
      submission._create_file(wf_application_path, hue_wf.XML_FILE_NAME, hue_wf.to_xml(mapping=properties), do_as=True)

      # Deploy Coordinator XML
      job.conf_dict.update(mapping)
      submission = Submission(user=request.user, job=hue_coord, fs=request.fs, jt=request.jt, properties=job.conf_dict, oozie_id=job.id)
      submission._create_file(coord_application_path, hue_coord.XML_FILE_NAME, hue_coord.to_xml(mapping=job.conf_dict), do_as=True)
      # Server picks up deployed Coordinator XML changes after running 'update' action
      submission.update_coord()

      request.info(_('Successfully updated Workflow definition'))
      return redirect(reverse('oozie:list_oozie_coordinator', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s' % params_form.errors))
  else:
    new_params = hue_wf and hue_wf.find_all_parameters() or []
    new_params = dict([(param['name'], param['value']) for param in new_params])

    # Set previous values
    if properties:
      new_params = dict([(key, properties[key]) if key in properties.keys() else (key, new_params[key]) for key, value in new_params.iteritems()])

    initial_params = ParameterForm.get_initial_params(new_params)
    params_form = ParametersFormSet(initial=initial_params)

  popup = render('editor2/submit_job_popup.mako', request, {
             'params_form': params_form,
             'name': _('Job'),
             'header': _('Sync Workflow definition?'),
             'action': reverse('oozie:sync_coord_workflow', kwargs={'job_id': job_id})
           }, force_template=True).content
  return JsonResponse(popup, safe=False)

@show_oozie_error
def rerun_oozie_job(request, job_id, app_path=None):
  ParametersFormSet = formset_factory(ParameterForm, extra=0)
  oozie_workflow = check_job_access_permission(request, job_id)
  check_job_edition_permission(oozie_workflow, request.user)
  if app_path is None:
    app_path = oozie_workflow.appPath
  else:
    app_path = urllib.unquote(app_path)
  return_json = request.GET.get('format') == 'json'

  if request.method == 'POST':
    rerun_form = RerunForm(request.POST, oozie_workflow=oozie_workflow)
    params_form = ParametersFormSet(request.POST)

    if sum([rerun_form.is_valid(), params_form.is_valid()]) == 2:
      args = {}

      if request.POST.get('rerun_form_choice') == 'fail_nodes':
        args['fail_nodes'] = 'true'
      else:
        args['skip_nodes'] = ','.join(rerun_form.cleaned_data['skip_nodes'])
      args['deployment_dir'] = app_path

      mapping = dict([(param['name'], param['value']) for param in params_form.cleaned_data])

      _rerun_workflow(request, job_id, args, mapping)

      if rerun_form.cleaned_data['return_json']:
        return JsonResponse({'status': 0, 'job_id': job_id}, safe=False)
      else:
        request.info(_('Workflow re-running.'))
        return redirect(reverse('oozie:list_oozie_workflow', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s %s' % (rerun_form.errors, params_form.errors)))
  else:
    rerun_form = RerunForm(oozie_workflow=oozie_workflow, return_json=return_json)
    initial_params = ParameterForm.get_initial_params(oozie_workflow.conf_dict)
    params_form = ParametersFormSet(initial=initial_params)

    return render('dashboard/rerun_workflow_popup.mako', request, {
                   'rerun_form': rerun_form,
                   'params_form': params_form,
                   'action': reverse('oozie:rerun_oozie_job', kwargs={'job_id': job_id, 'app_path': urllib.quote(app_path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS) }), 
                   'return_json': return_json,
                   'is_mini': request.GET.get('is_mini', False),
                 }, force_template=True)


def _rerun_workflow(request, oozie_id, run_args, mapping):
  try:
    submission = Submission(user=request.user, fs=request.fs, jt=request.jt, properties=mapping, oozie_id=oozie_id)
    job_id = submission.rerun(**run_args)
    return job_id
  except RestException, ex:
    msg = _("Error re-running workflow %s.") % (oozie_id,)
    LOG.exception(msg)

    raise PopupException(msg, detail=ex._headers.get('oozie-error-message', ex))


@show_oozie_error
def rerun_oozie_coordinator(request, job_id, app_path=None):
  oozie_coordinator = check_job_access_permission(request, job_id)
  check_job_edition_permission(oozie_coordinator, request.user)
  ParametersFormSet = formset_factory(ParameterForm, extra=0)
  if app_path is None:
    app_path = oozie_coordinator.coordJobPath
  else:
    app_path = urllib.unquote(app_path)
  return_json = request.GET.get('format') == 'json'

  if request.method == 'POST':
    params_form = ParametersFormSet(request.POST)
    rerun_form = RerunCoordForm(request.POST, oozie_coordinator=oozie_coordinator)

    if sum([rerun_form.is_valid(), params_form.is_valid()]) == 2:
      args = {}
      args['deployment_dir'] = app_path

      params = {
        'type': 'action',
        'scope': ','.join(oozie_coordinator.aggreate(rerun_form.cleaned_data['actions'])),
        'refresh': rerun_form.cleaned_data['refresh'],
        'nocleanup': rerun_form.cleaned_data['nocleanup'],
      }

      properties = dict([(param['name'], param['value']) for param in params_form.cleaned_data])

      _rerun_coordinator(request, job_id, args, params, properties)

      if rerun_form.cleaned_data['return_json']:
        return JsonResponse({'status': 0, 'job_id': job_id}, safe=False)
      else:
        request.info(_('Coordinator re-running.'))
        return redirect(reverse('oozie:list_oozie_coordinator', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s') % smart_unicode(rerun_form.errors))
      return list_oozie_coordinator(request, job_id)
  else:
    rerun_form = RerunCoordForm(oozie_coordinator=oozie_coordinator, return_json=return_json)
    initial_params = ParameterForm.get_initial_params(oozie_coordinator.conf_dict)
    params_form = ParametersFormSet(initial=initial_params)

    return render('dashboard/rerun_coord_popup.mako', request, {
                   'rerun_form': rerun_form,
                   'params_form': params_form,
                   'action': reverse('oozie:rerun_oozie_coord', kwargs={'job_id': job_id, 'app_path': urllib.quote(app_path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)}),
                   'return_json': return_json,
                   'is_mini': request.GET.get('is_mini', False),
                 }, force_template=True)


def _rerun_coordinator(request, oozie_id, args, params, properties):
  try:
    submission = Submission(user=request.user, fs=request.fs, jt=request.jt, oozie_id=oozie_id, properties=properties)
    job_id = submission.rerun_coord(params=params, **args)
    return job_id
  except RestException, ex:
    msg = _("Error re-running coordinator %s.") % (oozie_id,)
    LOG.exception(msg)

    raise PopupException(msg, detail=ex._headers.get('oozie-error-message', ex))


@show_oozie_error
def rerun_oozie_bundle(request, job_id, app_path):
  oozie_bundle = check_job_access_permission(request, job_id)
  check_job_edition_permission(oozie_bundle, request.user)
  ParametersFormSet = formset_factory(ParameterForm, extra=0)
  app_path = urllib.unquote(app_path)
  if request.method == 'POST':
    params_form = ParametersFormSet(request.POST)
    rerun_form = RerunBundleForm(request.POST, oozie_bundle=oozie_bundle)

    if sum([rerun_form.is_valid(), params_form.is_valid()]) == 2:
      args = {}
      args['deployment_dir'] = app_path

      params = {
        'coord-scope': ','.join(rerun_form.cleaned_data['coordinators']),
        'refresh': rerun_form.cleaned_data['refresh'],
        'nocleanup': rerun_form.cleaned_data['nocleanup'],
      }

      if rerun_form.cleaned_data['start'] and rerun_form.cleaned_data['end']:
        date = {
            'date-scope':
                '%(start)s::%(end)s' % {
                    'start': utc_datetime_format(rerun_form.cleaned_data['start']),
                    'end': utc_datetime_format(rerun_form.cleaned_data['end'])
                }
        }
        params.update(date)

      properties = dict([(param['name'], param['value']) for param in params_form.cleaned_data])

      _rerun_bundle(request, job_id, args, params, properties)

      request.info(_('Bundle re-running.'))
      return redirect(reverse('oozie:list_oozie_bundle', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s' % (rerun_form.errors,)))
      return list_oozie_bundle(request, job_id)
  else:
    rerun_form = RerunBundleForm(oozie_bundle=oozie_bundle)
    initial_params = ParameterForm.get_initial_params(oozie_bundle.conf_dict)
    params_form = ParametersFormSet(initial=initial_params)

    return render('dashboard/rerun_bundle_popup.mako', request, {
                   'rerun_form': rerun_form,
                   'params_form': params_form,
                   'action': reverse('oozie:rerun_oozie_bundle', kwargs={'job_id': job_id, 'app_path': urllib.quote(app_path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)}),
                 }, force_template=True)


def _rerun_bundle(request, oozie_id, args, params, properties):
  try:
    submission = Submission(user=request.user, fs=request.fs, jt=request.jt, oozie_id=oozie_id, properties=properties)
    job_id = submission.rerun_bundle(params=params, **args)
    return job_id
  except RestException, ex:
    msg = _("Error re-running bundle %s.") % (oozie_id,)
    LOG.exception(msg)

    raise PopupException(msg, detail=ex._headers.get('oozie-error-message', ex))


def submit_external_job(request, application_path):
  ParametersFormSet = formset_factory(ParameterForm, extra=0)

  if request.method == 'POST':
    params_form = ParametersFormSet(request.POST)

    if params_form.is_valid():
      mapping = dict([(param['name'], param['value']) for param in params_form.cleaned_data])
      mapping['dryrun'] = request.POST.get('dryrun_checkbox') == 'on'
      application_name = os.path.basename(application_path)
      application_class = Bundle if application_name == 'bundle.xml' else Coordinator if application_name == 'coordinator.xml' else get_workflow()
      mapping[application_class.get_application_path_key()] = os.path.dirname(application_path)

      try:
        submission = Submission(request.user, fs=request.fs, jt=request.jt, properties=mapping)
        job_id = submission.run(application_path)
      except RestException, ex:
        detail = ex._headers.get('oozie-error-message', ex)
        if 'Max retries exceeded with url' in str(detail):
          detail = '%s: %s' % (_('The Oozie server is not running'), detail)
        LOG.exception(smart_str(detail))
        raise PopupException(_("Error submitting job %s") % (application_path,), detail=detail)

      jsonify = request.POST.get('format') == 'json'
      if jsonify:
        return JsonResponse({'status': 0, 'job_id': job_id, 'type': 'external_workflow'}, safe=False)
      else:
        request.info(_('Oozie job submitted'))
        view = 'list_oozie_bundle' if application_name == 'bundle.xml' else 'list_oozie_coordinator' if application_name == 'coordinator.xml' else 'list_oozie_workflow'
        return redirect(reverse('oozie:%s' % view, kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s' % params_form.errors))
  else:
    parameters = Submission(request.user, fs=request.fs, jt=request.jt).get_external_parameters(application_path)
    initial_params = ParameterForm.get_initial_params(parameters)
    params_form = ParametersFormSet(initial=initial_params)

  popup = render('editor/submit_job_popup.mako', request, {
                   'params_form': params_form,
                   'name': _('Job'),
                   'action': reverse('oozie:submit_external_job', kwargs={'application_path': application_path}),
                   'show_dryrun': os.path.basename(application_path) != 'bundle.xml',
                   'return_json': request.GET.get('format') == 'json'
                 }, force_template=True).content
  return JsonResponse(popup, safe=False)


def massaged_workflow_actions_for_json(workflow_actions, oozie_coordinator, oozie_bundle):
  actions = []

  for action in workflow_actions:
    if oozie_coordinator is not None:
      setattr(action, 'oozie_coordinator', oozie_coordinator)
    if oozie_bundle is not None:
      setattr(action, 'oozie_bundle', oozie_bundle)

    massaged_action = {
      'id': action.id,
      'log': action.get_absolute_log_url(),
      'url': action.get_absolute_url(),
      'name': action.name,
      'type': action.type,
      'status': action.status,
      'externalIdUrl': action.get_external_id_url(),
      'externalId': action.externalId,
      'externalJobId': action.externalId,
      'startTime': format_time(action.startTime),
      'endTime': format_time(action.endTime),
      'retries': action.retries,
      'errorCode': action.errorCode,
      'errorMessage': action.errorMessage,
      'transition': action.transition,
      'data': action.data,
    }
    actions.append(massaged_action)

  return actions

def massaged_coordinator_actions_for_json(coordinator, oozie_bundle):
  coordinator_id = coordinator.id
  coordinator_actions = coordinator.get_working_actions()
  actions = []

  related_job_ids = []
  related_job_ids.append('coordinator_job_id=%s' % coordinator_id)
  if oozie_bundle is not None:
    related_job_ids.append('bundle_job_id=%s' %oozie_bundle.id)

  for action in coordinator_actions:
    massaged_action = {
      'id': action.id,
      'url': action.externalId and reverse('oozie:list_oozie_workflow', kwargs={'job_id': action.externalId}) + '?%s' % '&'.join(related_job_ids) or '',
      'number': action.actionNumber,
      'type': 'schedule-task',
      'status': action.status,
      'externalId': action.externalId or '-',
      'externalIdUrl': action.externalId and reverse('oozie:list_oozie_workflow_action', kwargs={'action': action.externalId}) or '',
      'nominalTime': format_time(action.nominalTime),
      'title': action.title,
      'createdTime': format_time(action.createdTime),
      'lastModifiedTime': format_time(action.lastModifiedTime),
      'errorCode': action.errorCode,
      'errorMessage': action.errorMessage,
      'missingDependencies': action.missingDependencies
    }

    actions.append(massaged_action)

  # Sorting for Oozie < 4.1 backward compatibility
  actions.sort(key=lambda k: k['number'], reverse=True)

  return actions


def massaged_bundle_actions_for_json(bundle):
  bundle_actions = bundle.get_working_actions()
  actions = []

  for action in bundle_actions:
    massaged_action = {
      'id': action.coordJobId,
      'url': action.coordJobId and reverse('oozie:list_oozie_coordinator', kwargs={'job_id': action.coordJobId}) + '?bundle_job_id=%s' % bundle.id or '',
      'name': action.coordJobName,
      'type': action.type,
      'status': action.status,
      'externalId': action.coordExternalId or '-',
      'frequency': action.frequency,
      'timeUnit': action.timeUnit,
      'nextMaterializedTime': action.nextMaterializedTime,
      'concurrency': action.concurrency,
      'pauseTime': action.pauseTime,
      'user': action.user,
      'acl': action.acl,
      'timeOut': action.timeOut,
      'coordJobPath': action.coordJobPath,
      'executionPolicy': action.executionPolicy,
      'startTime': action.startTime,
      'endTime': action.endTime,
      'lastAction': action.lastAction
    }

    actions.insert(0, massaged_action)

  return actions


def format_time(st_time):
  if st_time is None:
    return '-'
  elif type(st_time) == time.struct_time:
    return time.strftime("%a, %d %b %Y %H:%M:%S", st_time)
  else:
    return st_time


def massaged_oozie_jobs_for_json(oozie_jobs, user, just_sla=False):
  jobs = []

  for job in oozie_jobs:
    if not just_sla or (just_sla and job.has_sla) and job.appName != 'pig-app-hue-script':
      last_modified_time_millis = hasattr(job, 'lastModTime') and job.lastModTime and (time.time() - time.mktime(job.lastModTime)) * 1000 or 0
      duration_millis = job.durationTime
      massaged_job = {
        'id': job.id,
        'lastModTime': hasattr(job, 'lastModTime') and job.lastModTime and format_time(job.lastModTime) or None,
        'lastModTimeInMillis': last_modified_time_millis,
        'lastModTimeFormatted': last_modified_time_millis and format_duration_in_millis(last_modified_time_millis) or None,
        'kickoffTime': hasattr(job, 'kickoffTime') and job.kickoffTime and format_time(job.kickoffTime) or '',
        'kickoffTimeInMillis': hasattr(job, 'kickoffTime') and job.kickoffTime and time.mktime(catch_unicode_time(job.kickoffTime)) or 0,
        'nextMaterializedTime': hasattr(job, 'nextMaterializedTime') and job.nextMaterializedTime and format_time(job.nextMaterializedTime) or '',
        'nextMaterializedTimeInMillis': hasattr(job, 'nextMaterializedTime') and job.nextMaterializedTime and time.mktime(job.nextMaterializedTime) or 0,
        'timeOut': hasattr(job, 'timeOut') and job.timeOut or None,
        'endTime': job.endTime and format_time(job.endTime) or None,
        'pauseTime': hasattr(job, 'pauseTime') and job.pauseTime and format_time(job.endTime) or None,
        'concurrency': hasattr(job, 'concurrency') and job.concurrency or None,
        'endTimeInMillis': job.endTime and time.mktime(job.endTime) or 0,
        'lastActionInMillis': hasattr(job, 'lastAction') and job.lastAction and time.mktime(job.lastAction) or 0,
        'status': job.status,
        'group': job.group,
        'isRunning': job.is_running(),
        'duration': duration_millis and format_duration_in_millis(duration_millis) or None,
        'durationInMillis': duration_millis,
        'appName': job.appName,
        'progress': job.get_progress(),
        'user': job.user,
        'absoluteUrl': job.get_absolute_url(),
        'canEdit': has_job_edition_permission(job, user),
        'killUrl': reverse('oozie:manage_oozie_jobs', kwargs={'job_id':job.id, 'action':'kill'}),
        'suspendUrl': reverse('oozie:manage_oozie_jobs', kwargs={'job_id':job.id, 'action':'suspend'}),
        'resumeUrl': reverse('oozie:manage_oozie_jobs', kwargs={'job_id':job.id, 'action':'resume'}),
        'created': hasattr(job, 'createdTime') and job.createdTime and format_time(job.createdTime) or '',
        'createdInMillis': job.submissionTime,
        'startTime': hasattr(job, 'startTime') and format_time(job.startTime) or None,
        'startTimeInMillis': hasattr(job, 'startTime') and job.startTime and time.mktime(job.startTime) or 0,
        'run': hasattr(job, 'run') and job.run or 0,
        'frequency': hasattr(job, 'frequency') and Coordinator.CRON_MAPPING.get(job.frequency, job.frequency) or None,
        'timeUnit': hasattr(job, 'timeUnit') and job.timeUnit or None,
        'parentUrl': hasattr(job, 'parentId') and job.parentId and get_link(job.parentId) or '',
        'submittedManually': hasattr(job, 'parentId') and (job.parentId is None or 'C@' not in job.parentId)
      }
      jobs.append(massaged_job)

  return { 'jobs': jobs }


def check_job_access_permission(request, job_id, **kwargs):
  """
  Decorator ensuring that the user has access to the job submitted to Oozie.

  Arg: Oozie 'workflow', 'coordinator' or 'bundle' ID.
  Return: the Oozie workflow, coordinator or bundle or raise an exception

  Notice: its gets an id in input and returns the full object in output (not an id).
  """
  if job_id is not None:
    oozie_api = get_oozie(request.user)
    if job_id.endswith('W'):
      get_job = oozie_api.get_job
    elif job_id.endswith('C'):
      get_job = oozie_api.get_coordinator
    else:
      get_job = oozie_api.get_bundle

    try:
      if job_id.endswith('C'):
        oozie_job = get_job(job_id, **kwargs)
      else:
        oozie_job = get_job(job_id)
    except RestException, ex:
      msg = _("Error accessing Oozie job %s.") % (job_id,)
      LOG.exception(msg)
      raise PopupException(msg, detail=ex._headers.get('oozie-error-message'))

  if is_admin(request.user) \
      or oozie_job.user == request.user.username \
      or has_dashboard_jobs_access(request.user):
    return oozie_job
  else:
    message = _("Permission denied. %(username)s does not have the permissions to access job %(id)s.") % \
        {'username': request.user.username, 'id': oozie_job.id}
    access_warn(request, message)
    raise PopupException(message)


def check_job_edition_permission(oozie_job, user):
  if has_job_edition_permission(oozie_job, user):
    return oozie_job
  else:
    message = _("Permission denied. %(username)s does not have the permissions to modify job %(id)s.") % \
        {'username': user.username, 'id': oozie_job.id}
    raise PopupException(message)


def has_job_edition_permission(oozie_job, user):
  return is_admin(user) or oozie_job.user == user.username or (oozie_job.group and user.groups.filter(name__in=oozie_job.group.split(",")).exists()) or (oozie_job.acl and user.username in oozie_job.acl.split(','))


def has_dashboard_jobs_access(user):
  return is_admin(user) or user.has_hue_permission(action="dashboard_jobs_access", app=DJANGO_APPS[0])
