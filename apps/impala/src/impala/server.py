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
import threading

from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from beeswax.server.dbms import QueryServerException
from beeswax.server.hive_server2_lib import HiveServerClient

from ImpalaService import ImpalaHiveServer2Service
from impala.impala_flags import get_webserver_certificate_file
from impala.conf import DAEMON_API_USERNAME, DAEMON_API_PASSWORD


LOG = logging.getLogger(__name__)

API_CACHE = None
API_CACHE_LOCK = threading.Lock()


def get_api(user, url):
  global  API_CACHE
  if API_CACHE is None or API_CACHE.get(url) is None:
    API_CACHE_LOCK.acquire()
    try:
      if API_CACHE is None:
        API_CACHE = {}
      if API_CACHE.get(url) is None:
        API_CACHE[url] = ImpalaDaemonApi(url)
    finally:
      API_CACHE_LOCK.release()
  api = API_CACHE[url]
  api.set_user(user)
  return api


def _get_impala_server_url(session):
  properties = session.get_properties()
  http_addr = properties.get('coordinator_host', properties.get('http_addr'))
  # Remove scheme if found
  http_addr = http_addr.replace('http://', '').replace('https://', '')
  return ('https://' if get_webserver_certificate_file() else 'http://') + http_addr


class ImpalaServerClientException(Exception):
  pass


class ImpalaDaemonApiException(Exception):
  pass


class ImpalaServerClient(HiveServerClient):

  def get_exec_summary(self, operation_handle, session_handle):
    """
    Calls Impala HS2 API's GetExecSummary method on the given query handle
    :return: TExecSummary object serialized as a dict
    """
    req = ImpalaHiveServer2Service.TGetExecSummaryReq(operationHandle=operation_handle, sessionHandle=session_handle)

    # GetExecSummary() only works for closed queries
    try:
      self.close_operation(operation_handle)
    except QueryServerException, e:
      LOG.warn('Failed to close operation for query handle, query may be invalid or already closed.')

    resp = self.call(self._client.GetExecSummary, req)

    return self._serialize_exec_summary(resp.summary)


  def get_runtime_profile(self, operation_handle, session_handle):
    """
    Calls Impala HS2 API's GetRuntimeProfile method on the given query handle
    :return: TExecSummary object serialized as a dict
    """
    req = ImpalaHiveServer2Service.TGetRuntimeProfileReq(operationHandle=operation_handle, sessionHandle=session_handle)

    # TGetRuntimeProfileReq() only works for closed queries
    try:
      self.close_operation(operation_handle)
    except QueryServerException, e:
      LOG.warn('Failed to close operation for query handle, query may be invalid or already closed.')

    resp = self.call(self._client.GetRuntimeProfile, req)

    return resp.profile


  def _serialize_exec_summary(self, summary):
    try:
      summary_dict = {
        'state': summary.state,
        'exch_to_sender_map': summary.exch_to_sender_map,
        'error_logs': summary.error_logs,
        'status': None,
        'progress': None,
        'nodes': [],
      }

      if summary.status is not None:
        summary_dict['status'] = summary.status.__dict__

      if summary.progress is not None:
        summary_dict['progress'] = summary.progress.__dict__

      if summary.nodes:
        for node in summary.nodes:
          node_dict = node.__dict__

          if node.exec_stats is not None:
            node_dict['exec_stats'] = [stat.__dict__ for stat in node.exec_stats]

          if node.estimated_stats is not None:
            node_dict['estimated_stats'] = node.estimated_stats.__dict__

          summary_dict['nodes'].append(node_dict)

      return summary_dict
    except Exception, e:
      raise ImpalaServerClientException('Failed to serialize the TExecSummary object: %s' % str(e))


class ImpalaDaemonApi(object):

  def __init__(self, server_url):
    self._url = server_url
    self._client = HttpClient(self._url, logger=LOG)
    # You can set username/password for Impala Web UI which overrides kerberos
    if DAEMON_API_USERNAME.get() is not None and DAEMON_API_PASSWORD.get() is not None:
      self._client.set_digest_auth(DAEMON_API_USERNAME.get(), DAEMON_API_PASSWORD.get())

    self._root = Resource(self._client)
    self._security_enabled = False
    self._thread_local = threading.local()


  def __str__(self):
    return "ImpalaDaemonApi at %s" % self._url


  @property
  def url(self):
    return self._url


  @property
  def security_enabled(self):
    return self._security_enabled


  @property
  def user(self):
    return self._thread_local.user


  def set_user(self, user):
    if hasattr(user, 'username'):
      self._thread_local.user = user.username
    else:
      self._thread_local.user = user


  def get_queries(self):
    params = {
      'json': 'true'
    }

    resp = self._root.get('queries', params=params)
    try:
      if isinstance(resp, basestring):
        return json.loads(resp)
      else:
        return resp
    except ValueError, e:
      raise ImpalaDaemonApiException('ImpalaDaemonApi did not return valid JSON: %s' % e)


  def get_query(self, query_id):
    params = {
      'query_id': query_id,
      'json': 'true'
    }

    resp = self._root.get('query_plan', params=params)
    try:
      if isinstance(resp, basestring):
        return json.loads(resp)
      else:
        return resp
    except ValueError, e:
      raise ImpalaDaemonApiException('ImpalaDaemonApi did not return valid JSON: %s' % e)


  def get_query_profile(self, query_id):
    params = {
      'query_id': query_id,
      'json': 'true'
    }

    resp = self._root.get('query_profile', params=params)
    try:
      if isinstance(resp, basestring):
        return json.loads(resp)
      else:
        return resp
    except ValueError, e:
      raise ImpalaDaemonApiException('ImpalaDaemonApi query_profile did not return valid JSON: %s' % e)

  def get_query_memory(self, query_id):
    params = {
      'query_id': query_id,
      'json': 'true'
    }

    resp = self._root.get('query_memory', params=params)
    try:
      if isinstance(resp, basestring):
        return json.loads(resp)
      else:
        return resp
    except ValueError, e:
      raise ImpalaDaemonApiException('ImpalaDaemonApi query_memory did not return valid JSON: %s' % e)

  def kill(self, query_id):
    params = {
      'query_id': query_id,
      'json': 'true'
    }
    resp = self._root.get('cancel_query', params=params)
    try:
      if isinstance(resp, basestring):
        return json.loads(resp)
      else:
        return resp
    except ValueError, e:
      raise ImpalaDaemonApiException('ImpalaDaemonApi kill did not return valid JSON: %s' % e)

  def get_query_backends(self, query_id):
    params = {
      'query_id': query_id,
      'json': 'true'
    }

    resp = self._root.get('query_backends', params=params)
    try:
      if isinstance(resp, basestring):
        return json.loads(resp)
      else:
        return resp
    except ValueError, e:
      raise ImpalaDaemonApiException('ImpalaDaemonApi query_backends did not return valid JSON: %s' % e)

  def get_query_finstances(self, query_id):
    params = {
      'query_id': query_id,
      'json': 'true'
    }

    resp = self._root.get('query_finstances', params=params)
    try:
      if isinstance(resp, basestring):
        return json.loads(resp)
      else:
        return resp
    except ValueError, e:
      raise ImpalaDaemonApiException('ImpalaDaemonApi query_finstances did not return valid JSON: %s' % e)

  def get_query_summary(self, query_id):
    params = {
      'query_id': query_id,
      'json': 'true'
    }

    resp = self._root.get('query_summary', params=params)
    try:
      if isinstance(resp, basestring):
        return json.loads(resp)
      else:
        return resp
    except ValueError, e:
      raise ImpalaDaemonApiException('ImpalaDaemonApi query_summary did not return valid JSON: %s' % e)

  def get_query_profile_encoded(self, query_id):
    params = {
      'query_id': query_id
    }

    return self._root.get('query_profile_encoded', params=params)