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
Oozie API classes.

This is mostly just codifying the datastructure of the Oozie REST API.
http://incubator.apache.org/oozie/docs/3.2.0-incubating/docs/WebServicesAPI.html
"""

import re

from cStringIO import StringIO
from time import mktime

from desktop.lib import i18n
from desktop.lib.exceptions_renderable import PopupException
from desktop.log.access import access_warn

import hadoop.confparse
from liboozie.utils import parse_timestamp, format_time

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse


class Action(object):

  def __init__(self, json_dict):
    for attr in self._ATTRS:
      setattr(self, attr, json_dict.get(attr))
    self._fixup()

  def _fixup(self): pass

  def is_finished(self):
    return self.status in ('OK', 'SUCCEEDED', 'DONE')

  @classmethod
  def create(self, action_class, action_dict):
    if ControlFlowAction.is_control_flow(action_dict.get('type')):
      return ControlFlowAction(action_dict)
    else:
      return action_class(action_dict)

  def __str__(self):
    return '%s - %s' % (self.type, self.name)


class ControlFlowAction(Action):
  _ATTRS = [
    'errorMessage',
    'status',
    'stats',
    'data',
    'transition',
    'externalStatus',
    'cred',
    'conf',
    'type',
    'endTime',
    'externalId',
    'id',
    'startTime',
    'externalChildIDs',
    'name',
    'errorCode',
    'trackerUri',
    'retries',
    'toString',
    'consoleUrl'
  ]

  @classmethod
  def is_control_flow(self, action_type):
    return action_type is not None and ( ':' in action_type or action_type == 'switch' )

  def _fixup(self):
    """
    Fixup:
      - time fields as struct_time
      - config dict
      - protect externalId
    """
    super(ControlFlowAction, self)._fixup()

    if self.startTime:
      self.startTime = parse_timestamp(self.startTime)
    if self.endTime:
      self.endTime = parse_timestamp(self.endTime)
    if self.retries:
      self.retries = int(self.retries)
    if self.externalId and not re.match('job_.*', self.externalId):
      self.externalId = None

    self.conf_dict = {}


class WorkflowAction(Action):
  _ATTRS = [
    'conf',
    'consoleUrl',
    'data',
    'endTime',
    'errorCode',
    'errorMessage',
    'externalId',
    'externalStatus',
    'id',
    'name',
    'retries',
    'startTime',
    'status',
    'trackerUri',
    'transition',
    'type',
    'externalChildIDs',
  ]

  def _fixup(self):
    """
    Fixup:
      - time fields as struct_time
      - config dict
    """
    super(WorkflowAction, self)._fixup()

    if self.startTime:
      self.startTime = parse_timestamp(self.startTime)
    if self.endTime:
      self.endTime = parse_timestamp(self.endTime)
    if self.retries:
      self.retries = int(self.retries)

    if self.conf:
      xml = StringIO(i18n.smart_str(self.conf))
      self.conf_dict = hadoop.confparse.ConfParse(xml)
    else:
      self.conf_dict = {}

    if self.externalId is not None and not re.match('job_.*', self.externalId):
      self.externalId = None

  def get_absolute_url(self):
    kwargs = {'action': self.id}
    if hasattr(self, 'oozie_coordinator') and self.oozie_coordinator:
      kwargs['coordinator_job_id'] = self.oozie_coordinator.id
    if hasattr(self, 'oozie_bundle') and self.oozie_bundle:
      kwargs['bundle_job_id'] = self.oozie_bundle.id

    return reverse('oozie:list_oozie_workflow_action', kwargs=kwargs)


class CoordinatorAction(Action):
  _ATTRS = [
    'status',
    'runConf',
    'errorMessage',
    'missingDependencies',
    'coordJobId',
    'errorCode',
    'actionNumber',
    'consoleUrl',
    'nominalTime',
    'externalStatus',
    'createdConf',
    'createdTime',
    'externalId',
    'lastModifiedTime',
    'type',
    'id',
    'trackerUri'
  ]

  def _fixup(self):
    """
    Fixup:
      - time fields as struct_time
      - config dict
    """
    super(CoordinatorAction, self)._fixup()

    if self.createdTime:
      self.createdTime = parse_timestamp(self.createdTime)
    if self.nominalTime:
      self.nominalTime = parse_timestamp(self.nominalTime)
    if self.lastModifiedTime:
      self.lastModifiedTime = parse_timestamp(self.lastModifiedTime)

    if self.runConf:
      xml = StringIO(i18n.smart_str(self.runConf))
      self.conf_dict = hadoop.confparse.ConfParse(xml)
    else:
      self.conf_dict = {}

    self.title = ' %s-%s'% (self.actionNumber, format_time(self.nominalTime))


class BundleAction(Action):
  _ATTRS = [
      'startTime',
      'actions',
      'frequency',
      'concurrency',
      'pauseTime',
      'group',
      'toString',
      'consoleUrl',
      'mat_throttling',
      'status',
      'conf',
      'user',
      'timeOut',
      'coordJobPath',
      'timeUnit',
      'coordJobId',
      'coordJobName',
      'nextMaterializedTime',
      'coordExternalId',
      'acl',
      'lastAction',
      'executionPolicy',
      'timeZone',
      'endTime'
  ]

  def _fixup(self):
    """
    Fixup:
      - time fields as struct_time
      - config dict
    """
    super(BundleAction, self)._fixup()

    self.type = 'coord-action'
    self.name = self.coordJobName

    if self.conf:
      xml = StringIO(i18n.smart_str(self.conf))
      self.conf_dict = hadoop.confparse.ConfParse(xml)
    else:
      self.conf_dict = {}

  def get_progress(self):
    """How much more time before the next action."""
    next = mktime(parse_timestamp(self.lastAction))
    start = mktime(parse_timestamp(self.startTime))
    end = mktime(parse_timestamp(self.endTime))

    if end != start:
      progress = min(int((1 - (end - next) / (end - start)) * 100), 100)
    else:
      progress = 100

    return progress


class Job(object):
  RUNNING_STATUSES = set(['PREP', 'RUNNING', 'SUSPENDED', 'PREP', # Workflow
                          'RUNNING', 'PREPSUSPENDED', 'SUSPENDED', 'PREPPAUSED', 'PAUSED' # Coordinator
                          ])
  """
  Accessing log and definition will trigger Oozie API calls.
  """
  def __init__(self, api, json_dict):
    for attr in self._ATTRS:
      setattr(self, attr, json_dict.get(attr))
    self._fixup()

    self._api = api
    self._log = None
    self._definition = None

  def _fixup(self):
    """
    Fixup fields:
      - expand actions
      - time fields are struct_time
      - run is integer
      - configuration dict
      - log
      - definition
    """
    if self.startTime:
      self.startTime = parse_timestamp(self.startTime)
    if self.endTime:
      self.endTime = parse_timestamp(self.endTime)

    self.actions = [Action.create(self.ACTION, act_dict) for act_dict in self.actions]
    if self.conf is not None:
      xml = StringIO(i18n.smart_str(self.conf))
      self.conf_dict = hadoop.confparse.ConfParse(xml)
    else:
      self.conf_dict = {}

  def _get_log(self):
    """Get the log lazily, trigger Oozie API call at the first access."""
    if self._log is None:
      self._log = self._api.get_job_log(self.id)
    return self._log
  log = property(_get_log)

  def _get_definition(self):
    """Get the definition lazily, trigger Oozie API call at the first access."""
    if self._definition is None:
      self._definition = self._api.get_job_definition(self.id)
    return self._definition
  definition = property(_get_definition)

  def start(self):
    self._api.job_control(self.id, 'start')

  def suspend(self):
    self._api.job_control(self.id, 'suspend')

  def resume(self):
    self._api.job_control(self.id, 'resume')

  def kill(self):
    self._api.job_control(self.id, 'kill')

  def available_actions(self):
    """
    available_actions() -> Zero or more of [ 'start', 'suspend', 'resume', 'kill' ]
    """
    if self.status in ('SUCCEEDED', 'KILLED', 'FAILED'):
      return []

    res = []
    if self.status == 'PREP':
      res.append('start')
    if self.status == 'RUNNING':
      res.append('suspend')
    if self.status == 'SUSPENDED':
      res.append('resume')
    res.append('kill')
    return res

  def check_request_permission(self, request):
    """Raise PopupException if request user doesn't have permission to modify workflow"""
    if not request.user.is_superuser and request.user.username != self.user:
      access_warn(request, _('Insufficient permission.'))
      raise PopupException(_("Permission denied. User %(username)s cannot modify user %(user)s's job.") %
                           dict(username=request.user.username, user=self.user))

  def get_control_flow_actions(self):
    return [action for action in self.actions if ControlFlowAction.is_control_flow(action.type)]

  def get_working_actions(self):
    return [action for action in self.actions if not ControlFlowAction.is_control_flow(action.type)]

  def is_running(self):
    return self.status in Job.RUNNING_STATUSES

  def __str__(self):
    return '%s - %s' % (self.id, self.status)


class Workflow(Job):
  _ATTRS = [
    'actions',
    'appName',
    'appPath',
    'conf',
    'consoleUrl',
    'createdTime',
    'endTime',
    'externalId',
    'group',
    'id',
    'lastModTime',
    'run',
    'startTime',
    'status',
    'user',
    'acl',
    'parentId'
  ]
  ACTION = WorkflowAction

  def _fixup(self):
    super(Workflow, self)._fixup()

    if self.createdTime:
      self.createdTime = parse_timestamp(self.createdTime)
    if self.lastModTime:
      self.lastModTime = parse_timestamp(self.lastModTime)
    if self.run:
      self.run = int(self.run)

  @property
  def type(self):
    return 'Workflow'

  def get_absolute_url(self):
    kwargs = {'job_id': self.id}
    if hasattr(self, 'oozie_coordinator') and self.oozie_coordinator:
      kwargs['coordinator_job_id'] = self.oozie_coordinator.id
    if hasattr(self, 'oozie_bundle') and self.oozie_bundle:
      kwargs['bundle_job_id'] = self.oozie_bundle.id
    return reverse('oozie:list_oozie_workflow', kwargs=kwargs)

  def get_progress(self):
    """How many actions are finished on the total of actions."""
    return int(sum([action.is_finished() for action in self.actions]) / float(max(len(self.actions), 1)) * 100)


class Coordinator(Job):
  _ATTRS = [
    'acl',
    'actions',
    'conf',
    'concurrency',
    'consoleUrl',
    'coordExternalId',
    'coordJobId',
    'coordJobName',
    'coordJobPath',
    'endTime',
    'executionPolicy',
    'frequency',
    'group',
    'lastAction',
    'mat_throttling',
    'nextMaterializedTime',
    'pauseTime',
    'startTime',
    'status',
    'timeOut',
    'timeUnit',
    'timeZone',
    'user',
  ]
  ACTION = CoordinatorAction

  def _fixup(self):
    super(Coordinator, self)._fixup()

    if self.nextMaterializedTime is not None:
      self.nextMaterializedTime = parse_timestamp(self.nextMaterializedTime)
    else:
      self.nextMaterializedTime = self.startTime

    # For when listing/mixing all the jobs together
    self.id = self.coordJobId
    self.appName = self.coordJobName

  @property
  def type(self):
    return 'Coordinator'

  def get_absolute_url(self, oozie_bundle=None):
    kwargs = {'job_id': self.id}
    if oozie_bundle:
      kwargs.update({'bundle_job_id': oozie_bundle.id})
    return reverse('oozie:list_oozie_coordinator', kwargs=kwargs)

  def get_progress(self):
    """How much more time before the final materialization."""
    next = mktime(self.nextMaterializedTime)
    start = mktime(self.startTime)
    end = mktime(self.endTime)

    if end != start:
      progress = min(int((1 - (end - next) / (end - start)) * 100), 100)
    else:
      progress = 100

    # Manage case of a rerun
    action_count = float(len(self.actions))
    if action_count != 0 and progress == 100:
      progress = int(sum([action.is_finished() for action in self.actions]) / action_count * 100)

    return progress

  @classmethod
  def aggreate(cls, actions):
    if not actions:
      return []

    result = []
    first = prev = actions[0]

    for a in actions[1:]:
      if int(a) != int(prev) + 1:
        result.append('-'.join((first, prev)))
        first = a
      prev = a

    result.append('-'.join((first, prev)))

    return result


class Bundle(Job):
  _ATTRS = [
    'status',
    'toString',
    'group',
    'conf',
    'bundleJobName',
    'startTime',
    'bundleCoordJobs',
    'kickoffTime',
    'acl',
    'bundleJobPath',
    'createdTime',
    'timeOut',
    'consoleUrl',
    'bundleExternalId',
    'timeUnit',
    'pauseTime',
    'bundleJobId',
    'endTime',
    'user',
  ]

  ACTION = BundleAction

  def _fixup(self):
    self.actions = self.bundleCoordJobs

    super(Bundle, self)._fixup()

    # For when listing/mixing all the jobs together
    self.id = self.bundleJobId
    self.appName = self.bundleJobName

  @property
  def type(self):
    return 'Bundle'

  def get_absolute_url(self):
    return reverse('oozie:list_oozie_bundle', kwargs={'job_id': self.id})

  def get_progress(self):
    progresses = [action.get_progress() for action in self.actions]
    count = len(progresses)

    if count != 0:
      return sum(progresses) / float(count)
    else:
      return 0


class JobList(object):
  """
  Represents a list of Oozie jobs (Workflows or Coordinators or Bundles).
  """
  _ATTRS = [
    'offset',
    'len',
    'total',
    'jobs',
  ]

  def __init__(self, klass, jobs_key, api, json_dict, filters=None):
    """
    json_dict is the oozie json.
    filters is (optionally) the dictionary of filters used to select this list
    """
    self._api = api
    self.offset = int(json_dict['offset'])
    self.total = int(json_dict['total'])
    self.jobs = [klass(self._api, wf_dict) for wf_dict in json_dict[jobs_key]]
    self.filters = filters


class WorkflowList(JobList):
  def __init__(self, api, json_dict, filters=None):
    super(WorkflowList, self).__init__(Workflow, 'workflows', api, json_dict, filters)


class CoordinatorList(JobList):
  def __init__(self, api, json_dict, filters=None):
    super(CoordinatorList, self).__init__(Coordinator, 'coordinatorjobs', api, json_dict, filters)


class BundleList(JobList):
  def __init__(self, api, json_dict, filters=None):
    super(BundleList, self).__init__(Bundle, 'bundlejobs', api, json_dict, filters)

