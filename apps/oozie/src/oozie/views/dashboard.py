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

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render, PopupException
from desktop.lib.rest.http_client import RestException
from liboozie.oozie_api import get_oozie

from oozie.models import History , Coordinator


LOG = logging.getLogger(__name__)


def manage_oozie_jobs(request, job_id, action):
  if request.method != 'POST':
    raise PopupException(_('Please use a POST request to manage an Oozie job.'))

  response = {'status': -1, 'data': ''}

  try:
    response['data'] = get_oozie().job_control(job_id, action)
    response['status'] = 0
  except RestException, ex:
    raise PopupException("Error %s Oozie job %s" % (action, job_id,),
                         detail=ex.message)

  return HttpResponse(json.dumps(response), mimetype="application/json")


def split_oozie_jobs(oozie_jobs):
  jobs = {}
  jobs_running = []
  jobs_completed = []

  for job in oozie_jobs:
    if job.status == 'RUNNING':
      jobs_running.append(job)
    else:
      jobs_completed.append(job)

  jobs['running_jobs'] = sorted(jobs_running, key=lambda w: w.status)
  jobs['completed_jobs'] = sorted(jobs_completed, key=lambda w: w.status)

  return jobs


def list_oozie_workflows(request):
  kwargs = {'cnt': 50,}
  if not request.user.is_superuser:
    kwargs['user'] = request.user.username

  workflows = get_oozie().get_workflows(**kwargs)

  return render('dashboard/list_oozie_workflows.mako', request, {
    'user': request.user,
    'jobs': split_oozie_jobs(workflows.jobs),
  })


def list_oozie_coordinators(request):
  kwargs = {'cnt': 50,}
  if not request.user.is_superuser:
    kwargs['user'] = request.user.username

  coordinators = get_oozie().get_coordinators(**kwargs)

  return render('dashboard/list_oozie_coordinators.mako', request, {
    'jobs': split_oozie_jobs(coordinators.jobs),
  })


def list_oozie_coordinator_from_job(request, job_id):
  return list_oozie_coordinator(request, History.objects.get(job__id=job_id).oozie_job_id)


def list_oozie_coordinator(request, job_id):
  try:
    oozie_coordinator = get_oozie().get_coordinator(job_id)
    # Accessing log and definition will trigger Oozie API calls
    log = oozie_coordinator.log
    definition = oozie_coordinator.definition
  except RestException, ex:
    raise PopupException(_("Error accessing Oozie job %s") % (job_id,),
                         detail=ex.message)

  # Cross reference the submission history (if any)
  coordinator = None
  try:
    coordinator = History.objects.get(oozie_job_id=job_id).job.get_full_node()
  except History.DoesNotExist, ex:
    pass

  return render('dashboard/list_oozie_coordinator.mako', request, {
    'oozie_coordinator': oozie_coordinator,
    'coordinator': coordinator,
    'definition': definition,
    'log': log,
  })


def list_oozie_workflow(request, job_id, coordinator_job_id=None):
  try:
    oozie_workflow = get_oozie().get_job(job_id)
    # Accessing log and definition will trigger Oozie API calls
    log = oozie_workflow.log
    definition = oozie_workflow.definition
  except RestException, ex:
    raise PopupException(_("Error accessing Oozie job %s") % (job_id,),
                         detail=ex._headers['oozie-error-message'])

  # Cross reference the submission history (if any)
  history = None
  try:
    history = History.objects.get(oozie_job_id=job_id)
    if history.job.owner != request.user:
      history = None
  except History.DoesNotExist, ex:
    pass


  coord = None
  if coordinator_job_id is not None:
    try:
      coord = get_oozie().get_coordinator(coordinator_job_id)
    except RestException, ex:
      raise PopupException(_("Error accessing Oozie job: %s") % (coordinator_job_id,),
                           detail=ex._headers['oozie-error-message'])

  # TODO move to Wf model
  hue_coord = None
  hue_workflow = None
  coord_id = oozie_workflow.conf_dict.get('hue-id', None) #TODO security
  if coord_id:
    try:
      hue_coord = Coordinator.objects.get(id=coord_id)
      hue_workflow = hue_coord.workflow
    except Coordinator.DoesNotExist:
      pass

  try:
    history = History.objects.filter(job__id=coord_id).latest('id')
    if history.job.owner != request.user:
      history = None
  except History.DoesNotExist, ex:
    pass

  if hue_workflow is None:
    hue_workflow = history is not None and history.job or None

  parameters = {}
  if history and history.properties_dict:
    parameters = history.properties_dict
  elif hue_workflow is not None:
    for param in hue_workflow.find_parameters():
      if param in oozie_workflow.conf_dict:
        parameters[param] = oozie_workflow.conf_dict[param]


  return render('dashboard/list_oozie_workflow.mako', request, {
    'oozie_workflow': oozie_workflow,
    'history': history,
    'workflow': hue_workflow,
    'definition': definition,
    'log': log,
    'coord': coord,
    'hue_coord': hue_coord,
    'parameters': parameters,
  })


def list_oozie_workflow_action(request, action):
  try:
    action = get_oozie().get_action(action)
    workflow = get_oozie().get_job(action.id.split('@')[0])
  except RestException, ex:
    raise PopupException(_t("Error accessing Oozie action %s") % (action,),
                         detail=ex.message)

  return render('dashboard/list_oozie_workflow_action.mako', request, {
    'action': action,
    'workflow': workflow,
  })
