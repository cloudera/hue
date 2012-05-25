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

import logging
import posixpath
import threading

from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from liboozie.types import WorkflowList, CoordinatorList, Coordinator, Workflow,\
  CoordinatorAction, WorkflowAction
from liboozie.utils import config_gen

# Manage deprecation after HUE-792.
# To Remove in Hue 3.
import jobsub.conf as jobsub_conf

if jobsub_conf.SECURITY_ENABLED.get() is not None:
  from jobsub.conf import SECURITY_ENABLED
else:
  from liboozie.conf import SECURITY_ENABLED

if jobsub_conf.OOZIE_URL.get() is not None:
  from jobsub.conf import OOZIE_URL
else:
  from liboozie.conf import OOZIE_URL

LOG = logging.getLogger(__name__)
DEFAULT_USER = 'hue'
API_VERSION = 'v1'

_XML_CONTENT_TYPE = 'application/xml;charset=UTF-8'

_api_cache = None
_api_cache_lock = threading.Lock()


def get_oozie():
  """Return a cached OozieApi"""
  global _api_cache
  if _api_cache is None:
    _api_cache_lock.acquire()
    try:
      if _api_cache is None:
        secure = SECURITY_ENABLED.get()
        _api_cache = OozieApi(OOZIE_URL.get(), secure)
    finally:
      _api_cache_lock.release()
  return _api_cache


class OozieApi(object):
  def __init__(self, oozie_url, security_enabled=False):
    self._url = posixpath.join(oozie_url, API_VERSION)
    self._client = HttpClient(self._url, logger=LOG)
    if security_enabled:
      self._client.set_kerberos_auth()
    self._root = Resource(self._client)
    self._security_enabled = security_enabled

    # To store user info
    self._thread_local = threading.local()

  def __str__(self):
    return "OozieApi at %s" % (self._url,)

  @property
  def url(self):
    return self._url

  @property
  def security_enabled(self):
    return self._security_enabled

  @property
  def user(self):
    try:
      return self._thread_local.user
    except AttributeError:
      return DEFAULT_USER

  def setuser(self, user):
    """Return the previous user"""
    prev = self.user
    self._thread_local.user = user
    return prev

  def _get_params(self):
    if self.security_enabled:
      return { 'doAs': self.user }
    return { 'user.name': DEFAULT_USER, 'doAs': self.user }


  VALID_JOB_FILTERS = ('name', 'user', 'group', 'status')

  def get_jobs(self, jobtype, offset=None, cnt=None, **kwargs):
    """
    Get a list of Oozie jobs.

    jobtype is 'wf', 'coord'
    Note that offset is 1-based.
    kwargs is used for filtering and may be one of VALID_FILTERS: name, user, group, status
    """
    params = self._get_params()
    if offset is not None:
      params['offset'] = str(offset)
    if cnt is not None:
      params['len'] = str(cnt)
    params['jobtype'] = jobtype

    filter_list = [ ]
    for key, val in kwargs.iteritems():
      if key not in OozieApi.VALID_JOB_FILTERS:
        raise ValueError('"%s" is not a valid filter for selecting jobs' % (key,))
      filter_list.append('%s=%s' % (key, val))
    params['filter'] = ';'.join(filter_list)

    # Send the request
    resp = self._root.get('jobs', params)
    if jobtype == 'wf':
      wf_list = WorkflowList(self, resp, filters=kwargs)
    else:
      wf_list = CoordinatorList(self, resp, filters=kwargs)
    return wf_list


  def get_workflows(self, offset=None, cnt=None, **kwargs):
    return self.get_jobs('wf', offset, cnt, **kwargs)


  def get_coordinators(self, offset=None, cnt=None, **kwargs):
    return self.get_jobs('coord', offset, cnt, **kwargs)


  # TODO: make get_job accept any jobid
  def get_job(self, jobid):
    """
    get_job(jobid) -> Workflow
    """
    params = self._get_params()
    resp = self._root.get('job/%s' % (jobid,), params)
    wf = Workflow(self, resp)
    return wf


  def get_coordinator(self, jobid):
    params = self._get_params()
    resp = self._root.get('job/%s' % (jobid,), params)
    return Coordinator(self, resp)


  def get_job_definition(self, jobid):
    """
    get_job_definition(jobid) -> Definition (xml string)
    """
    params = self._get_params()
    params['show'] = 'definition'
    xml = self._root.get('job/%s' % (jobid,), params)
    return xml


  def get_job_log(self, jobid):
    """
    get_job_log(jobid) -> Log (xml string)
    """
    params = self._get_params()
    params['show'] = 'log'
    xml = self._root.get('job/%s' % (jobid,), params)
    return xml

  def get_action(self, action_id):
    if 'C@' in action_id:
      Klass = CoordinatorAction
    else:
      Klass = WorkflowAction
    params = self._get_params()
    resp = self._root.get('job/%s' % (action_id,), params)
    return Klass(resp)

  def job_control(self, jobid, action):
    """
    job_control(jobid, action) -> None
    Raise RestException on error.
    """
    if action not in ('start', 'suspend', 'resume', 'kill'):
      msg = 'Invalid oozie job action: %s' % (action,)
      LOG.error(msg)
      raise ValueError(msg)
    params = self._get_params()
    params['action'] = action

    return self._root.put('job/%s' % jobid, params)


  def submit_workflow(self, application_path, properties=None):
    """
    submit_workflow(application_path, properties=None) -> jobid

    Submit a job to Oozie. May raise PopupException.
    """
    defaults = {
      'oozie.wf.application.path': application_path,
      'user.name': self.user,
    }

    if properties is not None:
      defaults.update(properties)
    properties = defaults

    return self.submit_job(properties)

  def submit_job(self, properties=None):
    """
    submit_job(properties=None, id=None) -> jobid

    Submit a job to Oozie. May raise PopupException.
    """
    defaults = {
      'user.name': self.user,
    }

    if properties is not None:
      defaults.update(properties)

    properties = defaults

    params = self._get_params()
    resp = self._root.post('jobs', params,
                  data=config_gen(properties),
                  contenttype=_XML_CONTENT_TYPE)
    return resp['id']


  def get_build_version(self):
    """
    get_build_version() -> Build version (dictionary)
    """
    params = self._get_params()
    resp = self._root.get('admin/build-version', params)
    return resp

  def get_instrumentation(self):
    """
    get_instrumentation() -> Oozie instrumentation (dictionary)
    """
    params = self._get_params()
    resp = self._root.get('admin/instrumentation', params)
    return resp

  def get_configuration(self):
    """
    get_configuration() -> Oozie config (dictionary)
    """
    params = self._get_params()
    resp = self._root.get('admin/configuration', params)
    return resp

  def get_oozie_status(self):
    """
    get_oozie_status() -> Oozie status (dictionary)
    """
    params = self._get_params()
    resp = self._root.get('admin/status', params)
    return resp
