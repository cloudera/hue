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
import posixpath
import threading

from django.utils.translation import ugettext as _

from desktop.conf import DEFAULT_USER
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str
from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from hadoop import cluster


LOG = logging.getLogger(__name__)

_API_VERSION = 'v1'
_JSON_CONTENT_TYPE = 'application/json'

API_CACHE = None
API_CACHE_LOCK = threading.Lock()


def get_resource_manager(username=None):
  global API_CACHE

  if API_CACHE is None:
    API_CACHE_LOCK.acquire()
    try:
      if API_CACHE is None:
        yarn_cluster = cluster.get_cluster_conf_for_job_submission()
        if yarn_cluster is None:
          raise PopupException(_('No Resource Manager are available.'))
        API_CACHE = ResourceManagerApi(yarn_cluster.RESOURCE_MANAGER_API_URL.get(), yarn_cluster.SECURITY_ENABLED.get(), yarn_cluster.SSL_CERT_CA_VERIFY.get())
    finally:
      API_CACHE_LOCK.release()

  API_CACHE.setuser(username) # Set the correct user

  return API_CACHE


class ResourceManagerApi(object):

  def __init__(self, rm_url, security_enabled=False, ssl_cert_ca_verify=False):
    self._url = posixpath.join(rm_url, 'ws', _API_VERSION)
    self._client = HttpClient(self._url, logger=LOG)
    self._root = Resource(self._client)
    self._security_enabled = security_enabled
    self._thread_local = threading.local() # To store user info
    self.from_failover = False

    if self._security_enabled:
      self._client.set_kerberos_auth()

    self._client.set_verify(ssl_cert_ca_verify)

  def _get_params(self):
    params = {}

    if self.username != DEFAULT_USER.get(): # We impersonate if needed
      params['doAs'] = self.username
      if not self.security_enabled:
        params['user.name'] = DEFAULT_USER.get()

    return params

  def __str__(self):
    return "ResourceManagerApi at %s" % (self._url,)

  def setuser(self, user):
    curr = self.user
    self._thread_local.user = user
    return curr

  @property
  def user(self):
    return self.username # Backward compatibility

  @property
  def username(self):
    try:
      return self._thread_local.user
    except AttributeError:
      return DEFAULT_USER.get()

  @property
  def url(self):
    return self._url

  @property
  def security_enabled(self):
    return self._security_enabled

  def cluster(self, **kwargs):
    params = self._get_params()
    return self._execute(self._root.get, 'cluster/info', params=params, headers={'Accept': _JSON_CONTENT_TYPE})

  def apps(self, **kwargs):
    params = self._get_params()
    params.update(kwargs)
    return self._execute(self._root.get, 'cluster/apps', params=params, headers={'Accept': _JSON_CONTENT_TYPE})

  def app(self, app_id):
    params = self._get_params()
    return self._execute(self._root.get, 'cluster/apps/%(app_id)s' % {'app_id': app_id}, params=params, headers={'Accept': _JSON_CONTENT_TYPE})

  def appattempts(self, app_id):
    params = self._get_params()
    return self._execute(self._root.get, 'cluster/apps/%(app_id)s/appattempts' % {'app_id': app_id}, params=params, headers={'Accept': _JSON_CONTENT_TYPE})

  def appattempts_attempt(self, app_id, attempt_id):
    attempts = self.appattempts(app_id)
    for attempt in attempts['appAttempts']['appAttempt']:
      if attempt['id'] == attempt_id or attempt.get('appAttemptId'):
        return attempt
    raise PopupException('Application {} does not have application attempt with id {}'.format(app_id, attempt_id))

  def kill(self, app_id):
    data = {'state': 'KILLED'}
    token = None

    # Tokens are managed within the kill method but should be moved out when not alpha anymore or we support submitting an app.
    if self.security_enabled and False:
      full_token = self.delegation_token()
      if 'token' not in full_token:
        raise PopupException(_('YARN did not return any token field.'), detail=smart_str(full_token))
      data['X-Hadoop-Delegation-Token'] = token = full_token.pop('token')
      LOG.debug('Received delegation token %s' % full_token)

    try:
      params = self._get_params()
      return self._execute(self._root.put, 'cluster/apps/%(app_id)s/state' % {'app_id': app_id}, params=params, data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    finally:
      if token:
        self.cancel_token(token)

  def delegation_token(self):
    params = self._get_params()
    data = {'renewer': self.username}
    return self._execute(self._root.post, 'cluster/delegation-token', params=params, data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)

  def cancel_token(self, token):
    params = self._get_params()
    headers = {'Hadoop-YARN-RM-Delegation-Token': token}
    LOG.debug('Canceling delegation token of ' % self.username)
    return self._execute(self._root.delete, 'cluster/delegation-token', params=params, headers=headers)

  def _execute(self, function, *args, **kwargs):
    response = None
    try:
      response = function(*args, **kwargs)
    except Exception, e:
      raise PopupException(_('YARN RM returned a failed response: %s') % e)
    return response
