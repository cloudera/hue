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

from desktop.conf import TIME_ZONE
from desktop.conf import DEFAULT_USER
from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from liboozie.conf import SECURITY_ENABLED, OOZIE_URL, SSL_CERT_CA_VERIFY
from liboozie.types import WorkflowList, CoordinatorList, Coordinator, Workflow,\
  CoordinatorAction, WorkflowAction, BundleList, Bundle, BundleAction
from liboozie.utils import config_gen


LOG = logging.getLogger(__name__)
DEFAULT_USER = DEFAULT_USER.get()
API_VERSION = 'v1' # Overridden to v2 for SLA


_XML_CONTENT_TYPE = 'application/xml;charset=UTF-8'


def get_oozie(user, api_version=API_VERSION):
  oozie_url = OOZIE_URL.get()
  secure = SECURITY_ENABLED.get()
  ssl_cert_ca_verify = SSL_CERT_CA_VERIFY.get()

  return OozieApi(oozie_url, user, security_enabled=secure, api_version=api_version, ssl_cert_ca_verify=ssl_cert_ca_verify)


class OozieApi(object):
  def __init__(self, oozie_url, user, security_enabled=False, api_version=API_VERSION, ssl_cert_ca_verify=True):
    self._url = posixpath.join(oozie_url, api_version)
    self._client = HttpClient(self._url, logger=LOG)

    if security_enabled:
      self._client.set_kerberos_auth()

    self._client.set_verify(ssl_cert_ca_verify)

    self._root = Resource(self._client)
    self._security_enabled = security_enabled
    # To store username info
    if hasattr(user, 'username'):
      self.user = user.username
    else:
      self.user = user
    self.api_version = api_version

  def __str__(self):
    return "OozieApi at %s" % (self._url,)

  @property
  def url(self):
    return self._url

  @property
  def security_enabled(self):
    return self._security_enabled

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

  VALID_JOB_FILTERS = ('name', 'user', 'group', 'status', 'startcreatedtime', 'text')
  VALID_LOG_FILTERS = set(('recent', 'limit', 'loglevel', 'text'))

  def get_jobs(self, jobtype, offset=None, cnt=None, filters=None):
    """
    Get a list of Oozie jobs.

    Note that offset is 1-based.
    kwargs is used for filtering and may be one of VALID_FILTERS: name, user, group, status
    """
    params = self._get_params()
    if offset is not None:
      params['offset'] = str(offset)
    if cnt is not None:
      params['len'] = str(cnt)
    if filters is None:
      filters = []
    params['jobtype'] = jobtype

    filter_list = []
    for key, val in filters:
      if key not in OozieApi.VALID_JOB_FILTERS:
        raise ValueError('"%s" is not a valid filter for selecting jobs' % (key,))
      filter_list.append('%s=%s' % (key, val))
    params['filter'] = ';'.join(filter_list)

    # Send the request
    resp = self._root.get('jobs', params)
    if jobtype == 'wf':
      wf_list = WorkflowList(self, resp, filters=filters)
    elif jobtype == 'coord':
      wf_list = CoordinatorList(self, resp, filters=filters)
    else:
      wf_list = BundleList(self, resp, filters=filters)
    return wf_list

  def get_workflows(self, offset=None, cnt=None, filters=None):
    return self.get_jobs('wf', offset, cnt, filters)

  def get_coordinators(self, offset=None, cnt=None, filters=None):
    return self.get_jobs('coord', offset, cnt, filters)

  def get_bundles(self, offset=None, cnt=None, filters=None):
    return self.get_jobs('bundle', offset, cnt, filters)

  # TODO: make get_job accept any jobid
  def get_job(self, jobid):
    """
    get_job(jobid) -> Workflow
    """
    params = self._get_params()
    resp = self._root.get('job/%s' % (jobid,), params)
    wf = Workflow(self, resp)
    return wf

  def get_coordinator(self, jobid, offset=None, cnt=None, filters=None):
    params = self._get_params()
    if offset is not None:
      params['offset'] = str(offset)
    if cnt is not None:
      params['len'] = str(cnt)
    if filters is None:
      filters = {}
    params.update({'order': 'desc'})

    filter_list = []
    for key, val in filters:
      if key not in OozieApi.VALID_JOB_FILTERS:
        raise ValueError('"%s" is not a valid filter for selecting jobs' % (key,))
      filter_list.append('%s=%s' % (key, val))
    params['filter'] = ';'.join(filter_list)

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
    return self._root.get('job/%s' % (jobid,), params)


  def get_job_log(self, jobid, logfilter=None):
    """
    get_job_log(jobid) -> Log (xml string)
    """
    params = self._get_params()
    params['show'] = 'log'

    filter_list = []
    if logfilter is None:
      logfilter = []
    for key, val in logfilter:
      if key not in OozieApi.VALID_LOG_FILTERS:
        raise ValueError('"%s" is not a valid filter for job logs' % (key,))
      filter_list.append('%s=%s' % (key, val))
    params['logfilter'] = ';'.join(filter_list)
    return self._root.get('job/%s' % (jobid,), params)


  def get_job_graph(self, jobid, format='svg'):
    params = self._get_params()
    params['show'] = 'graph'
    params['show-kill'] = 'true'
    params['format'] = format
    svg_data = self._root.get('job/%s' % (jobid,), params)
    return svg_data


  def get_job_status(self, jobid):
    params = self._get_params()
    params['show'] = 'status'

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
    if action not in ('start', 'suspend', 'resume', 'kill', 'rerun', 'coord-rerun', 'bundle-rerun', 'change', 'ignore', 'update'):
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

  def dryrun(self, properties=None):
    defaults = {
      'user.name': self.user,
    }

    if properties is not None:
      defaults.update(properties)

    properties = defaults

    params = self._get_params()
    params['action'] = 'dryrun'
    return self._root.post('jobs', params, data=config_gen(properties), contenttype=_XML_CONTENT_TYPE)

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

  def get_metrics(self):
    params = self._get_params()
    resp = self._root.get('admin/metrics', params)
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
