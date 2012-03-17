# (c) Copyright 2010 Cloudera, Inc. All rights reserved.

"""
Oozie objects.
"""

from cStringIO import StringIO

from desktop.lib import i18n
from desktop.lib.django_util import PopupException
from desktop.log.access import access_warn

import hadoop.confparse
from jobsub.oozie_lib.utils import parse_timestamp

# TODO(bc)  Smarter link from action to jobtracker
class Action(object):
  """
  Represents an Action. This is mostly just codifying the oozie json.
  """
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
  ]

  def __init__(self, json_dict):
    for attr in Action._ATTRS:
      setattr(self, attr, json_dict.get(attr))
    self._fixup()

  def _fixup(self):
    """
    Fixup:
      - time fields as struct_time
      - config dict
    """
    if self.startTime:
      self.startTime = parse_timestamp(self.startTime)
    if self.endTime:
      self.endTime = parse_timestamp(self.endTime)
    retries = int(self.retries)

    xml = StringIO(i18n.smart_str(self.conf))
    self.conf_dict = hadoop.confparse.ConfParse(xml)


class Workflow(object):
  """
  Represents a Workflow (i.e. job). This is mostly just codifying the oozie json.
  """
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
  ]

  def __init__(self, api, json_dict):
    for attr in Workflow._ATTRS:
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
    # TODO(bc)  Can we get the log and definition lazily?
    if self.startTime:
      self.startTime = parse_timestamp(self.startTime)
    if self.endTime:
      self.endTime = parse_timestamp(self.endTime)
    if self.createdTime:
      self.createdTime = parse_timestamp(self.createdTime)
    if self.lastModTime:
      self.lastModTime = parse_timestamp(self.lastModTime)

    self.run = int(self.run)

    self.actions = [ Action(act_dict) for act_dict in self.actions ]
    if self.conf is not None:
      xml = StringIO(i18n.smart_str(self.conf))
      self.conf_dict = hadoop.confparse.ConfParse(xml)
    else:
      self.conf_dict = { }


  def _get_log(self):
    """Get the log lazily"""
    if self._log is None:
      self._log = self._api.get_job_log(self.id)
    return self._log
  log = property(_get_log)

  def _get_definition(self):
    """Get the workflow definition lazily"""
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
      return [ ]

    res = [ ]
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
      access_warn(request, 'Insufficient permission')
      raise PopupException("Permission denied. User %s cannot modify user %s's job." %
                           (request.user.username, self.user))


class WorkflowList(object):
  """
  Represents a WorkflowList (i.e. jobs). This is mostly just codifying the oozie json.
  """
  _ATTRS = [
    'offset',
    'len',
    'total',
    'workflows',
  ]

  def __init__(self, api, json_dict, filters=None):
    """
    WorkflowList(json_dict, filters=None) -> WorkflowList

    json_dict is the oozie json.
    filters is (optionally) the dictionary of filters used to select this list
    """
    self._api = api
    self.offset = int(json_dict['offset'])
    self.total = int(json_dict['total'])
    self.workflows = [ Workflow(self._api, wf_dict) for wf_dict in json_dict['workflows'] ]
    self.filters = filters
