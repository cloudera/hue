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


from desktop.conf import TIME_ZONE
from desktop.conf import DEFAULT_USER
from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from liboozie.conf import SECURITY_ENABLED
from liboozie.conf import OOZIE_URL
from liboozie.types import WorkflowList, CoordinatorList, Coordinator, Workflow,\
  CoordinatorAction, WorkflowAction, BundleList, Bundle, BundleAction
from liboozie.utils import config_gen


LOG = logging.getLogger(__name__)
DEFAULT_USER = DEFAULT_USER.get()
API_VERSION = 'v1' # Overridden to v2 for SLA

_XML_CONTENT_TYPE = 'application/xml;charset=UTF-8'

_api_cache = None
_api_cache_lock = threading.Lock()


def get_oozie(user, api_version=API_VERSION):
  global _api_cache
  if _api_cache is None or _api_cache.api_version != api_version:
    _api_cache_lock.acquire()
    try:
      if _api_cache is None or _api_cache.api_version != api_version:
        secure = SECURITY_ENABLED.get()
        _api_cache = OozieApi(OOZIE_URL.get(), secure, api_version)
    finally:
      _api_cache_lock.release()
  _api_cache.setuser(user)
  return _api_cache


class OozieApi(object):
  def __init__(self, oozie_url, security_enabled=False, api_version=API_VERSION):
    self._url = posixpath.join(oozie_url, api_version)
    self._client = HttpClient(self._url, logger=LOG)
    if security_enabled:
      self._client.set_kerberos_auth()
    self._root = Resource(self._client)
    self._security_enabled = security_enabled
    # To store username info
    self._thread_local = threading.local()
    self.api_version = api_version

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
    return self._thread_local.user

  def setuser(self, user):
    if hasattr(user, 'username'):
      self._thread_local.user = user.username
    else:
      self._thread_local.user = user

  def _get_params(self):
    if self.security_enabled:
      return { 'doAs': self.user, 'timezone': TIME_ZONE.get() }
    return { 'user.name': DEFAULT_USER, 'doAs': self.user, 'timezone': TIME_ZONE.get() }

  def _get_oozie_properties(self, properties=None):
    defaults = {
      'user.name': self.user,
    }

    if properties is not None:
      defaults.update(properties)

    return defaults

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
    elif jobtype == 'coord':
      wf_list = CoordinatorList(self, resp, filters=kwargs)
    else:
      wf_list = BundleList(self, resp, filters=kwargs)
    return wf_list

  def get_workflows(self, offset=None, cnt=None, **kwargs):
    return self.get_jobs('wf', offset, cnt, **kwargs)

  def get_coordinators(self, offset=None, cnt=None, **kwargs):
    return self.get_jobs('coord', offset, cnt, **kwargs)

  def get_bundles(self, offset=None, cnt=None, **kwargs):
    return self.get_jobs('bundle', offset, cnt, **kwargs)

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
    params.update({'len': -1})
    resp = self._root.get('job/%s' % (jobid,), params)
    return Coordinator(self, resp)

  def get_bundle(self, jobid):
    params = self._get_params()
    resp = self._root.get('job/%s' % (jobid,), params)
    return Bundle(self, resp)

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
    elif 'B@' in action_id:
      Klass = BundleAction
    else:
      Klass = WorkflowAction
    params = self._get_params()
    resp = self._root.get('job/%s' % (action_id,), params)
    return Klass(resp)

  def job_control(self, jobid, action, properties=None, parameters=None):
    """
    job_control(jobid, action) -> None
    Raise RestException on error.
    """
    if action not in ('start', 'suspend', 'resume', 'kill', 'rerun', 'coord-rerun', 'bundle-rerun'):
      msg = 'Invalid oozie job action: %s' % (action,)
      LOG.error(msg)
      raise ValueError(msg)
    properties = self._get_oozie_properties(properties)
    params = self._get_params()
    params['action'] = action
    if parameters is not None:
      params.update(parameters)

    return self._root.put('job/%s' % jobid, params,  data=config_gen(properties), contenttype=_XML_CONTENT_TYPE)

  def submit_workflow(self, application_path, properties=None):
    """
    submit_workflow(application_path, properties=None) -> jobid

    Raise RestException on error.
    """
    defaults = {
      'oozie.wf.application.path': application_path,
      'user.name': self.user,
    }

    if properties is not None:
      defaults.update(properties)
    properties = defaults

    return self.submit_job(properties)

  # Is name actually submit_coord?
  def submit_job(self, properties=None):
    """
    submit_job(properties=None, id=None) -> jobid

    Raise RestException on error.
    """
    defaults = {
      'user.name': self.user,
    }

    if properties is not None:
      defaults.update(properties)

    properties = defaults

    params = self._get_params()
    resp = self._root.post('jobs', params, data=config_gen(properties), contenttype=_XML_CONTENT_TYPE)
    return resp['id']

  def rerun(self, jobid, properties=None, params=None):
    properties = self._get_oozie_properties(properties)
    if params is None:
      params = self._get_params()
    else:
      self._get_params().update(params)

    params['action'] = 'rerun'

    return self._root.put('job/%s' % jobid, params, data=config_gen(properties), contenttype=_XML_CONTENT_TYPE)

  def get_build_version(self):
    """
    get_build_version() -> Build version (dictionary)
    """
    params = self._get_params()
    resp = self._root.get('admin/build-version', params)
    return resp

  def get_instrumentation(self):
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

  def get_oozie_slas(self, **kwargs):
    """
    filter=
      app_name=my-sla-app
      id=0000002-131206135002457-oozie-oozi-W
      nominal_start=2013-06-18T00:01Z
      nominal_end=2013-06-23T00:01Z
    """
    params = self._get_params()
    params['filter'] = ';'.join(['%s=%s' % (key, val) for key, val in kwargs.iteritems()])
    resp = self._root.get('sla', params)
    return resp['slaSummaryList']
