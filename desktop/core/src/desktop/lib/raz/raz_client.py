#!/usr/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import json
import logging
import socket
import sys
import uuid

import requests
import requests_kerberos

from datetime import datetime, timedelta

from desktop.conf import AUTH_USERNAME
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.sdxaas.knox_jwt import fetch_jwt

import desktop.lib.raz.signer_protos_pb2 as raz_signer

if sys.version_info[0] > 2:
  from urllib.parse import urlparse as lib_urlparse, unquote as lib_urlunquote
else:
  from urlparse import urlparse as lib_urlparse
  from urllib import unquote as lib_urlunquote


LOG = logging.getLogger(__name__)


class RazToken:

  def __init__(self, raz_url, auth_type):
    self.raz_url = raz_url
    self.auth_handler = requests_kerberos.HTTPKerberosAuth(mutual_authentication=requests_kerberos.OPTIONAL)
    self.init_time = datetime.now()
    self.raz_token = None
    self.auth_type = auth_type

    o = lib_urlparse(self.raz_url)
    if not o.netloc:
      raise PopupException('Could not parse the host of the Raz server %s' % self.raz_url)
    self.raz_hostname, self.raz_port = o.netloc.split(':')
    self.scheme = o.scheme


  def get_delegation_token(self, user):
    ip_address = socket.gethostbyname(self.raz_hostname)
    GET_PARAMS = {
      "op": "GETDELEGATIONTOKEN",
      "service": "%s:%s" % (ip_address, self.raz_port),
      "renewer": AUTH_USERNAME.get(),
      "doAs": user
    }

    if self.auth_type == 'kerberos':
      r = requests.get(self.raz_url, GET_PARAMS, auth=self.auth_handler, verify=False)
    elif self.auth_type == 'jwt':
      jwt_token = fetch_jwt()
      if jwt_token is None:
        raise PopupException('Knox JWT is not available to send to RAZ.')

      _headers = {'Authorization': 'Bearer %s' % (jwt_token)}
      r = requests.get(self.raz_url, GET_PARAMS, headers=_headers, verify=False)

    self.raz_token = json.loads(r.text)['Token']['urlString']
    LOG.debug('Raz token: %s' % self.raz_token)

    return self.raz_token


  def renew_delegation_token(self, user):
    if self.raz_token is None:
      self.raz_token = self.get_delegation_token(user=user)
    if (self.init_time - timedelta(hours=8)) > datetime.now():
      r = requests.put("%s?op=RENEWDELEGATIONTOKEN&token=%s"%(self.raz_url, self.raz_token), auth=self.auth_handler, verify=False)
    return self.raz_token


class RazClient(object):

  def __init__(self, raz_url, raz_token, username, service='s3', service_name='cm_s3', cluster_name='myCluster'):
    self.raz_url = raz_url.strip('/')
    self.raz_token = raz_token
    self.username = username
    self.service = service

    if self.service == 'adls':
      self.service_params = {
        'endpoint_prefix': 'adls',
        'service_name': 'adls',
        'serviceType': 'adls'
      }
    else:
      self.service_params = {
        'endpoint_prefix': 's3',
        'service_name': 's3',
        'serviceType': 's3'
      }

    self.service_name = service_name
    self.cluster_name = cluster_name
    self.requestid = str(uuid.uuid4())


  def check_access(self, method, url, params=None, headers=None, data=None):
    LOG.debug("Check access: method {%s}, url {%s}, params {%s}, headers {%s}" % (method, url, params, headers))

    path = lib_urlparse(url)
    url_params = dict([p.split('=') if '=' in p else (p, '') for p in path.query.split('&') if path.query])  # ?delete, ?prefix=/hue
    params = params if params is not None else {}
    headers = headers if headers is not None else {}

    endpoint = "%s://%s" % (path.scheme, path.netloc)
    resource_path = path.path.lstrip("/")

    request_data = {
      "requestId": self.requestid,
      "serviceType": self.service_params['serviceType'],
      "serviceName": self.service_name,
      "user": self.username,
      "userGroups": [],
      "clientIpAddress": "",
      "clientType": "",
      "clusterName": self.cluster_name,
      "clusterType": "",
      "sessionId": "",
      "accessTime": "",
      "context": {}
    }
    request_headers = {"Content-Type": "application/json"}
    raz_url = "%s/api/authz/%s/access?delegation=%s" % (self.raz_url, self.service, self.raz_token)

    if self.service == 'adls':
      self._make_adls_request(request_data, method, path, url_params, resource_path)
    elif self.service == 's3':
      self._make_s3_request(request_data, request_headers, method, params, headers, url_params, endpoint, resource_path, data=data)

    LOG.debug('Raz url: %s' % raz_url)
    LOG.debug("Sending access check headers: {%s} request_data: {%s}" % (request_headers, request_data))
    raz_req = requests.post(raz_url, headers=request_headers, json=request_data, verify=False)

    signed_response_result = None
    signed_response = None

    if raz_req.ok:
      result = raz_req.json().get("operResult", False) and raz_req.json()["operResult"]["result"]

      if result == "NOT_DETERMINED":
        msg = "Failure %s" % raz_req.json()
        LOG.error(msg)
        raise PopupException(msg)

      if result != "ALLOWED":
        msg = "Permission missing %s" % raz_req.json()
        raise PopupException(msg, error_code=401)

      if result == "ALLOWED":
        LOG.debug('Received allowed response %s' % raz_req.json())
        signed_response_data = raz_req.json()["operResult"]["additionalInfo"]

        if self.service == 'adls':
          LOG.debug("Received SAS %s" % signed_response_data["ADLS_DSAS"])
          return {'token': signed_response_data["ADLS_DSAS"]}
        else:
          signed_response_result = signed_response_data["S3_SIGN_RESPONSE"]

          if signed_response_result is not None:
            raz_response_proto = raz_signer.SignResponseProto()
            signed_response = raz_response_proto.FromString(base64.b64decode(signed_response_result))
            LOG.debug("Received signed Response %s" % signed_response)

          # Signed headers "only"
          if signed_response is not None:
            return dict([(i.key, i.value) for i in signed_response.signer_generated_headers])


  def _make_adls_request(self, request_data, method, path, url_params, resource_path):
    resource_path = resource_path.split('/', 1)

    storage_account = path.netloc.split('.')[0]
    container = resource_path[0]

    relative_path = "/"
    relative_path = self._handle_relative_path(method, url_params, resource_path, relative_path)

    access_type = self.handle_adls_req_mapping(method, url_params)

    request_data.update({
      "clientType": "adls",
      "operation": {
        "resource": {
          "storageaccount": storage_account,
          "container": container,
          "relativepath": relative_path,
        },
        "action": access_type,
        "accessTypes": [access_type]
      }
    })


  def _handle_relative_path(self, method, params, resource_path, relative_path):
    if len(resource_path) == 2:
      relative_path += resource_path[1]

    if relative_path == "/" and method == 'GET' and params.get('resource') == 'filesystem' and params.get('directory'):
      relative_path += params['directory']

    # Unquoting the full relative_path to catch edge cases like path having whitespaces or non-ascii chars.
    return lib_urlunquote(relative_path)


  def handle_adls_req_mapping(self, method, params):
    if method == 'HEAD':
      access_type = ''
      if params.get('action') == 'getStatus' or params.get('resource') == 'filesystem':
        access_type = 'get-status'
      if params.get('action') == 'getAccessControl':
        access_type = 'get-acl'

    if method == 'DELETE':
      access_type = 'delete-recursive' if params.get('recursive') == 'true' else 'delete'

    if method == 'GET':
      access_type = 'list' if params.get('resource') == 'filesystem' else 'read'

    if method == 'PATCH':
      if params.get('action') in ('append', 'flush'):
        access_type = 'write'
      elif params.get('action') == 'setAccessControl':
        access_type = 'set-permission'

    if method == 'PUT':
      if params.get('resource') == 'file':
        access_type = 'create-file'
      elif params.get('resource') == 'directory':
        access_type = 'create-directory'
      else:
        access_type = 'rename-source'

    return access_type


  def _make_s3_request(self, request_data, request_headers, method, params, headers, url_params, endpoint, resource_path, data=None):

    # In GET operations with non-ascii chars, only the non-ascii part is URL encoded.
    # We need to unquote the path fully before making a signed request for RAZ.
    if method == 'GET' and 'prefix' in url_params and '%' in url_params['prefix']:
      if sys.version_info[0] < 3 and isinstance(url_params['prefix'], unicode):
        url_params['prefix'] = url_params['prefix'].encode()

      url_params['prefix'] = lib_urlunquote(url_params['prefix'])

    allparams = [raz_signer.StringListStringMapProto(key=key, value=[val]) for key, val in url_params.items()]
    allparams.extend([raz_signer.StringListStringMapProto(key=key, value=[val]) for key, val in params.items()])
    headers = [raz_signer.StringStringMapProto(key=key, value=val) for key, val in headers.items()]

    LOG.debug(
      "Preparing sign request with "
      "http_method: {%s}, headers: {%s}, parameters: {%s}, endpoint: {%s}, resource_path: {%s}, content_to_sign: {%s}" %
      (method, headers, allparams, endpoint, resource_path, data)
    )

    # Raz signed request proto call expects data as bytes instead of str for Py3.
    if sys.version_info[0] > 2 and data is not None and not isinstance(data, bytes):
      data = data.encode()

    raz_req = raz_signer.SignRequestProto(
        endpoint_prefix=self.service_params['endpoint_prefix'],
        service_name=self.service_params['service_name'],
        endpoint=endpoint,
        http_method=method,
        headers=headers,
        parameters=allparams,
        resource_path=resource_path,
        content_to_sign=data,
        time_offset=0
    )
    raz_req_serialized = raz_req.SerializeToString()
    if sys.version_info[0] > 2:
      signed_request = base64.b64encode(raz_req_serialized).decode('utf-8')
    else:
      signed_request = base64.b64encode(raz_req_serialized)

    request_headers["Accept-Encoding"] = "gzip,deflate"
    request_data["context"] = {
      "S3_SIGN_REQUEST": signed_request
    }


def get_raz_client(raz_url, username, auth='kerberos', service='s3', service_name='cm_s3', cluster_name='myCluster'):
  if not username:
    from crequest.middleware import CrequestMiddleware
    request = CrequestMiddleware.get_request()
    username = request.user.username if request and hasattr(request, 'user') and request.user.is_authenticated else None

  if not username:
    raise PopupException('No username set.')

  raz = RazToken(raz_url, auth)
  raz_token = raz.get_delegation_token(user=username)

  return RazClient(raz_url, raz_token, username, service=service, service_name=service_name, cluster_name=cluster_name)
